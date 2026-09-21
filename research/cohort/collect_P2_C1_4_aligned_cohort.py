#!/usr/bin/env python3
"""P2-C1.4 fresh aligned cohort collector.

This adapter runs the qualified C.4.2.3-D execution path twice per fresh case:
P0 incumbent and P5 intervention policy. It captures the FIRST P5 execution
evidence (the evidence available before the intervention decision) and keeps it
separate from outcome derivation.

No X_W annotation is created here. Human annotation consumes the locked
decision_time_evidence artifact after this collector completes.

The gold SQL is loaded only for the post-lock outcome phase and is never
serialized into the decision-time evidence artifact.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, time
from dataclasses import asdict
from pathlib import Path

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def sha256_json(obj) -> str:
    return sha256_bytes(canonical(obj))

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def forbidden_scan(obj, forbidden):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k in forbidden:
                raise ValueError(f"forbidden field {k} in decision-time artifact")
            forbidden_scan(v, forbidden)
    elif isinstance(obj, list):
        for v in obj:
            forbidden_scan(v, forbidden)

class FirstEvidenceEvaluator:
    """SecondaryExecutionEvaluator-compatible evaluator retaining first evidence."""
    def __init__(self, base_cls, dataset):
        self._base = base_cls(dataset)
        self.first_evidence = None
        self.last_evidence = None
        self._capture_enabled = False

    def _result(self, con, sql):
        return self._base._result(con, sql)

    def execute(self, db_id, sql):
        import sqlite3
        try:
            with sqlite3.connect(self._base.dataset.db_path(db_id)) as con:
                rows, cols = self._result(con, sql)
            evidence = {
                "db_id": db_id,
                "columns": cols,
                "rows": [list(r) for r in rows],
                "row_count": len(rows),
                "column_count": len(cols),
                "evidence_sha256": sha256_json({"columns": cols, "rows": [list(r) for r in rows]}),
            }
            self.last_evidence = evidence
            if self._capture_enabled and self.first_evidence is None:
                self.first_evidence = evidence
            return True, None, len(rows), len(cols)
        except Exception as exc:
            evidence = {
                "db_id": db_id, "columns": None, "rows": None,
                "row_count": None, "column_count": None,
                "evidence_sha256": None, "execution_error": str(exc),
            }
            self.last_evidence = evidence
            if self._capture_enabled and self.first_evidence is None:
                self.first_evidence = evidence
            return False, str(exc), None, None

    def correct(self, db_id, predicted_sql, gold_sql):
        return self._base.correct(db_id, predicted_sql, gold_sql)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--questions",type=Path,required=True)
    ap.add_argument("--database-dir",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    args=ap.parse_args()

    sys.path.insert(0, str(Path(os.environ["PROJECT1_ROOT"]).resolve()))
    from research.spider_benchmark import SpiderDataset, BenchmarkEnvironment, SecondaryExecutionEvaluator
    from research.deterministic_solver import RuleBasedDeterministicSolver
    from app.services.llm import OllamaProvider

    manifest=load_json(args.manifest)
    cases=manifest["cases"]
    if not cases:
        raise ValueError("fresh manifest contains no cases")
    manifest_hash=sha256_bytes(args.manifest.read_bytes())

    dataset=SpiderDataset(args.questions,args.database_dir)
    by_key={(x.db_id,x.question):x for x in dataset.examples}
    for c in cases:
        if (c["db_id"],c["question"]) not in by_key:
            raise ValueError(f"manifest case not found in source dataset: {c['decision_id']}")

    provider=OllamaProvider(os.environ["OLLAMA_BASE_URL"],os.environ["OLLAMA_MODEL"])
    deterministic=RuleBasedDeterministicSolver(args.database_dir)
    evaluator=FirstEvidenceEvaluator(SecondaryExecutionEvaluator,dataset)
    env=BenchmarkEnvironment(dataset,evaluator,provider,deterministic)

    decision_records=[]
    outcome_inputs=[]
    for c in cases:
        ex=by_key[(c["db_id"],c["question"])]

        # P0 incumbent.
        evaluator._capture_enabled=False
        p0=env.run(ex,"P0")
        p0_sql=p0.generated_sql
        p0_b={
            "execution_ok": bool(p0.execution_ok),
            "row_count": p0.evidence_row_count,
            "column_count": p0.evidence_column_count,
        }

        # P5 intervention path. first_evidence is captured before P5 can
        # escalate/replace, and is therefore the evidence presented at the
        # intervention decision point.
        evaluator.first_evidence=None
        evaluator._capture_enabled=True
        p5=env.run(ex,"P5")
        first=evaluator.first_evidence
        evaluator._capture_enabled=False
        if first is None:
            raise ValueError(f"{c['decision_id']}: no decision-time evidence captured")

        # The qualified path's P5 first execution should correspond to the
        # incumbent evidence. Any mismatch is a hard alignment failure.
        if p0.execution_ok and p5.execution_ok:
            if p0.evidence_row_count != first["row_count"] or p0.evidence_column_count != first["column_count"]:
                raise ValueError(f"{c['decision_id']}: P0/P5 decision-time evidence count mismatch")

        decision_records.append({
            "decision_id":c["decision_id"],
            "protocol_version":"P2-C1.4-ALIGNED-V1",
            "baseline":p0_b,
            "decision_time_evidence":{
                "question":c["question"],
                "database_id":c["db_id"],
                "returned_columns":first["columns"],
                "returned_rows":first["rows"],
                "row_count":first["row_count"],
                "column_count":first["column_count"],
                "evidence_hash":first["evidence_sha256"],
                "captured_before_intervention":True,
            },
            "provenance":{
                "manifest_hash":manifest_hash,
                "code_version":os.environ.get("PROJECT1_COMMIT","unknown"),
                "runtime_manifest_hash":os.environ.get("RUNTIME_MANIFEST_HASH","unknown"),
                "baseline_hash":sha256_json(p0_b),
            },
        })
        outcome_inputs.append({
            "decision_id":c["decision_id"],
            "db_id":c["db_id"],
            "question":c["question"],
            "gold_sql":ex.gold_sql,
            "p0_sql":p0_sql,
            "p5_sql":p5.generated_sql,
        })

    args.outdir.mkdir(parents=True,exist_ok=True)
    evidence_path=args.outdir/"decision_time_evidence.json"
    evidence_path.write_text(json.dumps({
        "protocol_version":"P2-C1.4-DECISION-TIME-EVIDENCE-V1",
        "manifest_hash":manifest_hash,
        "records":decision_records,
    },indent=2,ensure_ascii=False),encoding="utf-8")
    evidence_hash=sha256_bytes(evidence_path.read_bytes())

    # Leakage barrier: outcome inputs are not written until the complete
    # decision-time evidence artifact has been serialized and hashed.
    outcomes=[]
    for x in outcome_inputs:
        p0_correct=evaluator.correct(x["db_id"],x["p0_sql"],x["gold_sql"])
        final_correct=evaluator.correct(x["db_id"],x["p5_sql"],x["gold_sql"])
        replacement=bool(x["p5_sql"] and x["p5_sql"].strip()!= (x["p0_sql"] or "").strip())
        y_h=int(p0_correct and replacement and not final_correct)
        outcomes.append({
            "decision_id":x["decision_id"],
            "replacement_occurred":replacement,
            "p0_correct":p0_correct,
            "final_correct":final_correct,
            "y_h":y_h,
            "locked_after_evidence":True,
            "evidence_artifact_sha256":evidence_hash,
        })

    outcome_path=args.outdir/"outcomes.json"
    outcome_path.write_text(json.dumps({"protocol_version":"P2-C1.4-OUTCOME-V1","evidence_artifact_sha256":evidence_hash,"records":outcomes},indent=2),encoding="utf-8")

    aligned=[]
    outcome_by_id={x["decision_id"]:x for x in outcomes}
    for r in decision_records:
        o=outcome_by_id[r["decision_id"]]
        aligned.append({**r,"intervention_outcome":o,"provenance":{**r["provenance"],"outcome_record_hash":sha256_json(o)}})

    aligned_path=args.outdir/"aligned_records.json"
    aligned_path.write_text(json.dumps({"protocol_version":"P2-C1.4-ALIGNED-V1","evidence_artifact_sha256":evidence_hash,"records":aligned},indent=2,ensure_ascii=False),encoding="utf-8")

    forbidden={"p0_correct","challenger_correct","replacement_occurred","final_correct","y_h","generated_sql","reference_sql","reference_answer","posthoc_evaluator_labels","gold_sql"}
    forbidden_scan(json.loads(evidence_path.read_text()),forbidden)

    print(json.dumps({
        "status":"PASS",
        "cases":len(cases),
        "decision_time_evidence_sha256":evidence_hash,
        "records":str(aligned_path),
        "outcome_records":len(outcomes),
        "harm_count":sum(x["y_h"] for x in outcomes),
    },indent=2))

if __name__=="__main__":
    main()

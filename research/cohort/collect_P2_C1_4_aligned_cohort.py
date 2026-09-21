#!/usr/bin/env python3
"""P2-C1.4 aligned cohort collector.

Runs the pinned P6-IP decision path while capturing the exact P0
decision-time SQL result (rows + columns) before any intervention decision.
The captured evidence is serialized and hashed before official outcome
evaluation is invoked. X_W is never generated here.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sqlite3, sys
from dataclasses import asdict
from pathlib import Path

FORBIDDEN = {
    "p0_correct","challenger_correct","replacement_occurred","final_correct",
    "y_h","generated_sql","gold_sql","reference_sql","reference_answer",
    "posthoc_evaluator_labels","intervention","replacement","downstream_outcome"
}

def canon(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",",":")).encode()
def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def sha256_json(x): return sha256_bytes(canon(x))

def scan_forbidden(x, path=""):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in FORBIDDEN:
                raise ValueError(f"forbidden key {k} at {path or '<root>'}")
            scan_forbidden(v, f"{path}.{k}" if path else k)
    elif isinstance(x,list):
        for i,v in enumerate(x): scan_forbidden(v, f"{path}[{i}]")

class CapturingEvaluator:
    """Adapter preserving SecondaryExecutionEvaluator's contract."""
    def __init__(self, base_cls, dataset):
        self.dataset = dataset
        self.base = base_cls(dataset)
        self.captures = []

    def execute(self, db_id, sql):
        try:
            with sqlite3.connect(self.dataset.db_path(db_id)) as con:
                rows, cols = self.base._result(con, sql)
            ev = {
                "db_id": db_id,
                "columns": cols,
                "rows": [list(r) for r in rows],
                "row_count": len(rows),
                "column_count": len(cols),
                "evidence_sha256": sha256_json({"columns": cols, "rows": [list(r) for r in rows]}),
            }
            self.captures.append(ev)
            return True, None, len(rows), len(cols)
        except Exception as exc:
            ev = {
                "db_id": db_id, "columns": None, "rows": None,
                "row_count": None, "column_count": None,
                "evidence_sha256": None, "execution_error": str(exc),
            }
            self.captures.append(ev)
            return False, str(exc), None, None

    def correct(self, db_id, predicted_sql, gold_sql):
        return self.base.correct(db_id, predicted_sql, gold_sql)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--questions",type=Path,required=True)
    ap.add_argument("--database-dir",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--spider-eval-dir",type=Path,required=True)
    ap.add_argument("--tables-file",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    ap.add_argument("--limit",type=int)
    ap.add_argument("--non-confirmatory",action="store_true")
    args=ap.parse_args()

    if not args.non_confirmatory:
        raise SystemExit("REFUSED: collector requires --non-confirmatory until the collection protocol is explicitly frozen")

    p1=Path(os.environ["PROJECT1_ROOT"]).resolve()
    sys.path.insert(0,str(p1))
    from research.spider_benchmark import (
        SpiderDataset, SecondaryExecutionEvaluator, BenchmarkEnvironment,
    )
    from research.deterministic_solver import RuleBasedDeterministicSolver
    from research.p6_ip_runner import run_case

    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("confirmatory") is True:
        raise SystemExit("REFUSED: confirmatory manifest is not authorized by the current protocol state")
    cases=manifest["cases"][:args.limit] if args.limit else manifest["cases"]
    if not cases: raise SystemExit("FAIL: empty cohort manifest")
    decision_ids=[c["decision_id"] for c in cases]
    if len(decision_ids)!=len(set(decision_ids)):
        raise SystemExit("FAIL: duplicate decision_id")

    dataset=SpiderDataset(args.questions,args.database_dir)
    lookup={(x.db_id,x.question):x for x in dataset.examples}
    manifest_hash=sha256_bytes(args.manifest.read_bytes())

    provider_name=os.getenv("LLM_PROVIDER","").lower()
    if provider_name!="ollama":
        raise SystemExit("REFUSED: P2-C1.4 runtime qualification requires pinned Ollama")
    from app.services.llm import OllamaProvider
    provider=OllamaProvider(os.getenv("OLLAMA_BASE_URL","http://127.0.0.1:11434"),os.getenv("OLLAMA_MODEL","llama3.2:1b"))
    evaluator=CapturingEvaluator(SecondaryExecutionEvaluator,dataset)
    from research.spider_benchmark import BenchmarkEnvironment
    env=BenchmarkEnvironment(dataset,evaluator,provider,RuleBasedDeterministicSolver(args.database_dir))

    evidence_records=[]
    outcomes=[]
    for c in cases:
        ex=lookup.get((c["db_id"],c["question"]))
        if ex is None: raise SystemExit(f"FAIL: manifest case not found: {c['decision_id']}")
        before=len(evaluator.captures)
        selected, defensibility=run_case(env, ex)
        new=evaluator.captures[before:]
        # P0 is the first execution performed by run_case. It is the only
        # evidence eligible for X_W and must precede intervention logic.
        if not new: raise SystemExit(f"FAIL: no execution capture: {c['decision_id']}")
        p0_ev=new[0]
        if p0_ev["db_id"]!=c["db_id"]: raise SystemExit(f"FAIL: db mismatch: {c['decision_id']}")
        baseline={
            "execution_ok": bool(selected.execution_ok if selected.policy=="P6-IP" and selected.actions[:1]!=["incumbent:P0"] else selected.execution_ok),
            "row_count": p0_ev["row_count"],
            "column_count": p0_ev["column_count"],
        }
        evidence={
            "question":c["question"],"database_id":c["db_id"],
            "returned_columns":p0_ev["columns"] if p0_ev["columns"] is not None else [],
            "returned_rows":p0_ev["rows"] if p0_ev["rows"] is not None else [],
            "row_count":p0_ev["row_count"],"column_count":p0_ev["column_count"],
            "evidence_hash":p0_ev["evidence_sha256"],
            "captured_before_intervention":True,
        }
        record={
            "decision_id":c["decision_id"],
            "protocol_version":"P2-C1.4-DECISION-TIME-EVIDENCE-V1",
            "question":c["question"],"database_id":c["db_id"],
            "baseline":baseline,"decision_time_evidence":evidence,
            "provenance":{
                "manifest_hash":manifest_hash,
                "project1_commit":os.environ.get("PROJECT1_COMMIT","unknown"),
                "runtime_manifest_hash":os.environ.get("RUNTIME_MANIFEST_HASH","unknown"),
            }
        }
        scan_forbidden(record)
        evidence_records.append(record)

        # No correctness/intervention fields are persisted until the entire
        # decision-time evidence artifact is serialized and hashed.
    args.outdir.mkdir(parents=True,exist_ok=True)
    evidence_path=args.outdir/"decision_time_evidence.json"
    evidence_path.write_text(json.dumps({
        "protocol_version":"P2-C1.4-DECISION-TIME-EVIDENCE-V1",
        "manifest_hash":manifest_hash,"records":evidence_records
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    evidence_hash=sha256_bytes(evidence_path.read_bytes())
    scan_forbidden(json.loads(evidence_path.read_text(encoding="utf-8")))

    # Only now perform the official post-hoc correctness evaluation.
    from research.spider_official_eval import evaluate_traces
    payload={"dataset_manifest":{"question_file":str(args.questions)},
             "policies":["P6-IP"],"traces":[]}
    # Reconstruct minimal traces from a second, non-mutating read of the
    # selected records is intentionally NOT used for outcome derivation.
    # The P6 runner trace must be retained separately by a future confirmatory
    # collector extension. This dry-run collector therefore stops here rather
    # than fabricating Y_H.
    metadata={
        "status":"PASS_EVIDENCE_CAPTURE_ONLY",
        "non_confirmatory":True,
        "decision_count":len(evidence_records),
        "decision_time_evidence_sha256":evidence_hash,
        "official_outcome_evaluation":"NOT_RUN",
        "reason":"Current gate validates evidence capture and temporal/leakage boundary before outcome-bearing collection."
    }
    (args.outdir/"runtime_qualification_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2))

if __name__=="__main__":
    main()

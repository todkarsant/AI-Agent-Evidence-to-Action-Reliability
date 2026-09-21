#!/usr/bin/env python3
"""P2-C1.4 aligned cohort collector built on the qualified P6-IP decision path.

Pipeline:
  P0 incumbent -> decision-time evidence capture -> P6 intervention decision
  -> final selected answer -> post-lock official correctness -> Y_H.

Decision-time evidence contains only what was observable before the P6
intervention/replacement decision. Gold SQL is used only after that artifact is
serialized and hashed. X_W is intentionally not produced by this collector.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def sha256_json(obj): return sha256_bytes(canonical(obj))

FORBIDDEN = {
    "p0_correct","challenger_correct","replacement_occurred","final_correct",
    "y_h","generated_sql","gold_sql","reference_sql","reference_answer",
    "posthoc_evaluator_labels"
}

def scan_forbidden(obj, path=""):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k in FORBIDDEN:
                raise ValueError(f"forbidden field {k} in decision-time evidence at {path or '<root>'}")
            scan_forbidden(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            scan_forbidden(v, f"{path}[{i}]")

class CapturingEvaluator:
    def __init__(self, base_cls, dataset):
        self._base=base_cls(dataset)
        self.capture_next=False
        self.first_evidence=None

    def execute(self, db_id, sql):
        import sqlite3
        try:
            with sqlite3.connect(self._base.dataset.db_path(db_id)) as con:
                rows, cols=self._base._result(con, sql)
            evidence={
                "db_id":db_id,
                "columns":cols,
                "rows":[list(r) for r in rows],
                "row_count":len(rows),
                "column_count":len(cols),
                "evidence_sha256":sha256_json({"columns":cols,"rows":[list(r) for r in rows]})
            }
            if self.capture_next and self.first_evidence is None:
                self.first_evidence=evidence
            return True,None,len(rows),len(cols)
        except Exception as exc:
            evidence={
                "db_id":db_id,"columns":None,"rows":None,
                "row_count":None,"column_count":None,
                "evidence_sha256":None,"execution_error":str(exc)
            }
            if self.capture_next and self.first_evidence is None:
                self.first_evidence=evidence
            return False,str(exc),None,None

    def correct(self, db_id, predicted_sql, gold_sql):
        return self._base.correct(db_id,predicted_sql,gold_sql)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--questions",type=Path,required=True)
    ap.add_argument("--database-dir",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--spider-eval-dir",type=Path,required=True)
    ap.add_argument("--tables-file",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    args=ap.parse_args()

    p1=Path(os.environ["PROJECT1_ROOT"]).resolve()
    sys.path.insert(0,str(p1))
    from research.spider_benchmark import SpiderDataset, SecondaryExecutionEvaluator, BenchmarkEnvironment
    from research.deterministic_solver import RuleBasedDeterministicSolver
    from research.p6_ip_runner import run_case
    from research.spider_official_eval import evaluate_traces
    from app.services.llm import OllamaProvider

    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("confirmatory") is True:
        raise ValueError("collector refuses a manifest marked confirmatory until collection protocol is explicitly frozen")
    cases=manifest["cases"]
    manifest_hash=sha256_bytes(args.manifest.read_bytes())

    dataset=SpiderDataset(args.questions,args.database_dir)
    by_key={(x.db_id,x.question):x for x in dataset.examples}
    for c in cases:
        if (c["db_id"],c["question"]) not in by_key:
            raise ValueError(f"manifest case not found in source dataset: {c['decision_id']}")

    provider=OllamaProvider(os.environ["OLLAMA_BASE_URL"],os.environ["OLLAMA_MODEL"])
    evaluator=CapturingEvaluator(SecondaryExecutionEvaluator,dataset)
    env=BenchmarkEnvironment(dataset,evaluator,provider,RuleBasedDeterministicSolver(args.database_dir))

    evidence_records=[]
    run_rows=[]
    for c in cases:
        ex=by_key[(c["db_id"],c["question"])]
        evaluator.first_evidence=None
        evaluator.capture_next=True
        trace, defensibility=run_case(env,ex)
        evaluator.capture_next=False
        ev=evaluator.first_evidence
        if ev is None:
            raise ValueError(f"{c['decision_id']}: no incumbent decision-time evidence captured")

        evidence_records.append({
            "decision_id":c["decision_id"],
            "protocol_version":"P2-C1.4-DECISION-TIME-EVIDENCE-V1",
            "question":c["question"],
            "database_id":c["db_id"],
            "baseline":{
                "execution_ok":bool(trace.get("execution_ok") if isinstance(trace,dict) else trace.execution_ok),
                "row_count":ev["row_count"],
                "column_count":ev["column_count"]
            },
            "decision_time_evidence":{
                "returned_columns":ev["columns"],
                "returned_rows":ev["rows"],
                "row_count":ev["row_count"],
                "column_count":ev["column_count"],
                "evidence_hash":ev["evidence_sha256"],
                "captured_before_intervention":True
            },
            "provenance":{
                "manifest_hash":manifest_hash,
                "project1_commit":os.environ.get("PROJECT1_COMMIT","unknown"),
                "runtime_manifest_hash":os.environ.get("RUNTIME_MANIFEST_HASH","unknown")
            }
        })
        run_rows.append({"decision_id":c["decision_id"],"question":c["question"],"db_id":c["db_id"],
                         "trace":trace if isinstance(trace,dict) else trace.__dict__,"defensibility":defensibility})

    args.outdir.mkdir(parents=True,exist_ok=True)
    evidence_path=args.outdir/"decision_time_evidence.json"
    evidence_path.write_text(json.dumps({
        "protocol_version":"P2-C1.4-DECISION-TIME-EVIDENCE-V1",
        "manifest_hash":manifest_hash,
        "records":evidence_records
    },indent=2,ensure_ascii=False),encoding="utf-8")
    evidence_hash=sha256_bytes(evidence_path.read_bytes())
    scan_forbidden(json.loads(evidence_path.read_text(encoding="utf-8")))

    # Outcome derivation begins only after the decision-time artifact is
    # serialized, hashed, and leakage-scanned.
    trace_payload={
        "dataset_manifest":{
            "question_file":str(args.questions),
            "question_sha256":SpiderDataset.sha256(args.questions)
        },
        "policies":["P6-IP"],
        "traces":[x["trace"] for x in run_rows]
    }
    official=evaluate_traces(trace_payload,args.database_dir,args.tables_file,args.spider_eval_dir)
    official_by_id={x["decision_id"]:r for x,r in zip([x["decision_id"] for x in run_rows],trace_payload["traces"])}

    outcomes=[]
    for x in run_rows:
        t=official_by_id[x["decision_id"]]
        d=x["defensibility"]
        p0_correct=bool(d.get("decision")=="INTERVENE" and t.get("official_execution_correct"))
        # For KEEP cases the selected trace is the incumbent P0. For REPLACE
        # cases it is the verified challenger selected by P6-IP.
        final_correct=bool(t.get("official_execution_correct"))
        replacement=bool(d.get("replacement") is True and d.get("decision")=="REPLACE")
        # P0 correctness for KEEP/REPLACE must be evaluated independently.
        ex=by_key[(x["db_id"],x["question"])]
        p0_sql=None
        # The P6 runner does not retain the incumbent SQL separately in its
        # final trace. Re-run only the deterministic official correctness
        # lookup from the trace record's stored incumbent evidence is not
        # possible, so require an explicit p0 correctness field from the
        # defensibility extension in future confirmatory collection.
        # The dry-run therefore fails closed rather than inventing P0 correctness.
        if "incumbent_official_correct" not in d:
            raise RuntimeError("P6 defensibility record lacks immutable incumbent official correctness; collector refuses to infer Y_H")
        p0_correct=bool(d["incumbent_official_correct"])
        y_h=int(p0_correct and replacement and not final_correct)
        outcomes.append({
            "decision_id":x["decision_id"],
            "replacement_occurred":replacement,
            "p0_correct":p0_correct,
            "final_correct":final_correct,
            "y_h":y_h,
            "locked_after_evidence":True,
            "evidence_artifact_sha256":evidence_hash
        })

    outcome_path=args.outdir/"outcomes.json"
    outcome_path.write_text(json.dumps({"protocol_version":"P2-C1.4-OUTCOME-V1","evidence_artifact_sha256":evidence_hash,"official_evaluator":official,"records":outcomes},indent=2),encoding="utf-8")

    outcome_by_id={x["decision_id"]:x for x in outcomes}
    aligned=[]
    for e in evidence_records:
        o=outcome_by_id[e["decision_id"]]
        aligned.append({
            "decision_id":e["decision_id"],
            "protocol_version":"P2-C1.4-ALIGNED-V1",
            "baseline":e["baseline"],
            "decision_time_evidence":{
                "question":e["question"],
                "database_id":e["database_id"],
                **e["decision_time_evidence"]
            },
            "intervention_outcome":o,
            "provenance":{
                **e["provenance"],
                "evidence_artifact_sha256":evidence_hash,
                "outcome_record_hash":sha256_json(o)
            }
        })
    aligned_path=args.outdir/"aligned_records.json"
    aligned_path.write_text(json.dumps({"protocol_version":"P2-C1.4-ALIGNED-V1","records":aligned},indent=2,ensure_ascii=False),encoding="utf-8")

    print(json.dumps({"status":"PASS","cases":len(cases),"evidence_sha256":evidence_hash,"harm_count":sum(x["y_h"] for x in outcomes)},indent=2))

if __name__=="__main__":
    main()

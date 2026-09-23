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
    ap.add_argument("--confirmatory",action="store_true")
    args=ap.parse_args()

    if args.non_confirmatory == args.confirmatory:
        raise SystemExit("REFUSED: specify exactly one of --non-confirmatory or --confirmatory")

    if args.confirmatory:
        if os.getenv("P2_C1_4_PROTOCOL_FROZEN") != "P2-C1.4-CONFIRMATORY-V1-RUNTIME3-2026-09-21":
            raise SystemExit("REFUSED: confirmatory collection requires the frozen P2-C1.4 protocol authorization")
    
    p1=Path(os.environ["PROJECT1_ROOT"]).resolve()
    sys.path.insert(0,str(p1))
    from research.spider_benchmark import (
        SpiderDataset, SecondaryExecutionEvaluator, BenchmarkEnvironment,
    )
    from research.deterministic_solver import RuleBasedDeterministicSolver
    from research.p6_ip_runner import run_case

    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.confirmatory:
        if manifest.get("confirmatory") is not True:
            raise SystemExit("REFUSED: confirmatory execution requires confirmatory=true manifest")
    else:
        if manifest.get("confirmatory") is True:
            raise SystemExit("REFUSED: non-confirmatory execution cannot consume confirmatory manifest")
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
    from runtime3_ollama import Runtime3OllamaProvider
    provider=Runtime3OllamaProvider(os.getenv("OLLAMA_BASE_URL","http://127.0.0.1:11434"),os.getenv("OLLAMA_MODEL","llama3.2:1b"))
    evaluator=CapturingEvaluator(SecondaryExecutionEvaluator,dataset)
    from research.spider_benchmark import BenchmarkEnvironment
    class RecordingEnvironment(BenchmarkEnvironment):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw); self.p0_traces={}
        def run(self, example, policy):
            trace=super().run(example, policy)
            if policy=="P0": self.p0_traces[(example.db_id,example.question)]=trace
            return trace
    env=RecordingEnvironment(dataset,evaluator,provider,RuleBasedDeterministicSolver(args.database_dir))

    evidence_records=[]
    selected_traces={}
    defensibility_records={}
    for c in cases:
        ex=lookup.get((c["db_id"],c["question"]))
        if ex is None: raise SystemExit(f"FAIL: manifest case not found: {c['decision_id']}")
        before=len(evaluator.captures)
        selected, defensibility=run_case(env, ex)
        selected_traces[c["decision_id"]]=selected
        defensibility_records[c["decision_id"]]=defensibility
        new=evaluator.captures[before:]
        # P0 is the first execution performed by run_case. It is the only
        # evidence eligible for X_W and must precede intervention logic.
        # If P0 produced no SQL, there is legitimately no executable evidence.
        # Under the frozen protocol this is NO_USABLE_EVIDENCE, not a synthetic
        # zero and not a shard-level failure. If SQL existed but no capture was
        # recorded, fail closed because evidence preservation is broken.
        if not new:
            p0_trace = env.p0_traces.get((c["db_id"], c["question"]))
            if p0_trace is None:
                raise SystemExit(f"FAIL: missing P0 trace: {c['decision_id']}")
            if p0_trace.generated_sql or p0_trace.execution_ok is True:
                raise SystemExit(f"FAIL: missing execution capture despite executable P0 trace: {c['decision_id']}")
            p0_ev={
                "db_id":c["db_id"],"columns":None,"rows":None,
                "row_count":None,"column_count":None,
                "evidence_sha256":None,
                "capture_reason":"no_sql_generated"
            }
        else:
            p0_ev=new[0]
        if p0_ev["db_id"]!=c["db_id"]: raise SystemExit(f"FAIL: db mismatch: {c['decision_id']}")
        baseline={
            "execution_ok": bool(p0_ev["row_count"] is not None),
            "row_count": p0_ev["row_count"],
            "column_count": p0_ev["column_count"],
        }
        decision_schema=env.dataset.schema(c["db_id"])
        evidence={
            "question":c["question"],"database_id":c["db_id"],"schema":decision_schema,
            "returned_columns":p0_ev["columns"] if p0_ev["columns"] is not None else None,
            "returned_rows":p0_ev["rows"] if p0_ev["rows"] is not None else None,
            "row_count":p0_ev["row_count"],"column_count":p0_ev["column_count"],
            "evidence_hash":(sha256_json({"question":c["question"],"database_id":c["db_id"],"schema":decision_schema,"returned_columns":p0_ev["columns"],"returned_rows":p0_ev["rows"],"row_count":p0_ev["row_count"],"column_count":p0_ev["column_count"]}) if p0_ev["row_count"] is not None else None),
            "captured_before_intervention":True,
        }
        record={
            "decision_id":c["decision_id"],
            "protocol_version":"P2-C1.4-DECISION-TIME-EVIDENCE-V2",
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
        "protocol_version":"P2-C1.4-DECISION-TIME-EVIDENCE-V2",
        "manifest_hash":manifest_hash,"records":evidence_records
    },indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    evidence_hash=sha256_bytes(evidence_path.read_bytes())
    scan_forbidden(json.loads(evidence_path.read_text(encoding="utf-8")))

    # Only now perform official post-hoc correctness evaluation. The evidence
    # artifact has already been serialized, hashed, and leakage-scanned.
    from research.spider_official_eval import evaluate_traces
    traces=[]
    trace_to_decision={}
    for c in cases:
        did=c["decision_id"]
        p0=env.p0_traces[(c["db_id"],c["question"])]
        selected=selected_traces[did]
        for label,tr in (("P0",p0),("P6-IP",selected)):
            d=asdict(tr)
            d["policy"]=label
            traces.append(d)
            trace_to_decision[(label,did)]=d
    payload={"dataset_manifest":{"question_file":str(args.questions)},
             "policies":["P0","P6-IP"],"traces":traces}
    official=evaluate_traces(payload,args.database_dir,args.tables_file,args.spider_eval_dir)

    outcomes=[]
    aligned=[]
    for c in cases:
        did=c["decision_id"]
        p0=trace_to_decision[("P0",did)]
        final=trace_to_decision[("P6-IP",did)]
        d=defensibility_records[did]
        replacement=bool(d.get("replacement") is True and d.get("decision")=="REPLACE")
        p0_correct=bool(p0.get("official_execution_correct"))
        final_correct=bool(final.get("official_execution_correct"))
        y_h=int(p0_correct and replacement and not final_correct)
        outcome={"replacement_occurred":replacement,
                 "p0_correct":p0_correct,"final_correct":final_correct,
                 "y_h":y_h,"locked_after_evidence":True}
        outcomes.append(outcome)
        e=next(x for x in evidence_records if x["decision_id"]==did)
        aligned.append({"decision_id":did,"protocol_version":"P2-C1.4-ALIGNED-V2",
                        "baseline":e["baseline"],
                        "decision_time_evidence":e["decision_time_evidence"],
                        "intervention_outcome":outcome,
                        "provenance":{
                          "manifest_hash":e["provenance"]["manifest_hash"],
                          "code_version":os.environ.get("PROJECT1_COMMIT","unknown"),
                          "runtime_manifest_hash":e["provenance"]["runtime_manifest_hash"],
                          "baseline_hash":sha256_json(e["baseline"]),
                          "outcome_record_hash":sha256_json(outcome)}})

    (args.outdir/"outcomes.json").write_text(json.dumps({
        "protocol_version":"P2-C1.4-OUTCOME-V1",
        "evidence_artifact_sha256":evidence_hash,
        "official_spider_execution":official,"records":outcomes},indent=2)+"\n",encoding="utf-8")
    (args.outdir/"aligned_records.json").write_text(json.dumps({
        "protocol_version":"P2-C1.4-ALIGNED-V2","records":aligned},
        indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    metadata={
        "status":"PASS_CONFIRMATORY_ALIGNED_ACQUISITION" if args.confirmatory else "PASS_NON_CONFIRMATORY_ALIGNED_DRY_RUN",
        "confirmatory":bool(args.confirmatory),
        "non_confirmatory":bool(args.non_confirmatory),
        "decision_count":len(evidence_records),
        "decision_time_evidence_sha256":evidence_hash,
        "official_outcome_evaluation":"RUN_AFTER_EVIDENCE_LOCK",
        "official_execution":official,
        "harm_count":sum(x["y_h"] for x in outcomes),
        "x_w":"NOT_ANNOTATED_IN_COLLECTOR",
        "reason":("Confirmatory aligned outcome-bearing acquisition under frozen protocol."
                  if args.confirmatory else
                  "Dry run proves same-unit evidence/outcome linkage and temporal leakage boundary; it is not confirmatory data.")
    }
    (args.outdir/"runtime_qualification_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2))

if __name__=="__main__":
    main()

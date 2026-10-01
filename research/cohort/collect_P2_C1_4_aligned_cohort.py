#!/usr/bin/env python3
"""P2-C1.4 aligned cohort collector.

Runs the pinned P6-IP decision path while capturing the exact P0
decision-time SQL result (rows + columns) before any intervention decision.
The captured evidence is serialized and hashed before official outcome
evaluation is invoked. X_W is never generated here.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sqlite3, sys
from dataclasses import asdict
from pathlib import Path

FORBIDDEN = {
    "p0_correct","challenger_correct","replacement_occurred","final_correct",
    "y_h","generated_sql","gold_sql","reference_sql","reference_answer",
    "posthoc_evaluator_labels","intervention","replacement","downstream_outcome"
}

STATUS_EVALUABLE="EVALUABLE"
STATUS_E1="EXCLUDED_E1_REFERENCE_NOT_SCOREABLE"
STATUS_PRE="NON_EVALUABLE_E2_RUNTIME_FAILURE_PRE_EVIDENCE"
STATUS_POST="NON_EVALUABLE_E3E4_RUNTIME_FAILURE_POST_EVIDENCE"
RUNTIME3_ERROR_RE=re.compile(r"^(Runtime3 |Ollama (candidate )?response completed without assistant content)")
MISSINGNESS_AMENDMENT_ID="P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01"

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
    # P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01 (E1): outcome-blind
    # reference-SQL census produced before any model call.
    ap.add_argument("--e1-census",type=Path)
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
    # Shard manifests carry the frozen parent manifest hash; provenance must
    # reference the frozen manifest so the forensic lock audit can reconcile it.
    manifest_file_hash=sha256_bytes(args.manifest.read_bytes())
    manifest_hash=manifest.get("parent_manifest_sha256") or manifest_file_hash

    e1_ids=set()
    e1_census_sha=None
    if args.e1_census:
        census_bytes=args.e1_census.read_bytes()
        census=json.loads(census_bytes)
        if census.get("source_manifest_sha256") not in (manifest_hash, manifest_file_hash):
            raise SystemExit("FAIL: E1 census does not reference this manifest")
        e1_census_sha=sha256_bytes(census_bytes)
        e1_ids={x["decision_id"] for x in census["excluded"]}

    # Runtime3 is a namespace package in this repository, while the pinned
    # Project1 checkout contains a regular research package. Ensure the
    # Runtime3 research directory remains visible after Project1 is inserted
    # on sys.path; do not modify the pinned Project1 source.
    import research as research_pkg
    runtime3_research = Path(__file__).resolve().parents[1]
    if str(runtime3_research) not in research_pkg.__path__:
        research_pkg.__path__.append(str(runtime3_research))

    provider_name=os.getenv("LLM_PROVIDER","").lower()
    if provider_name!="ollama":
        raise SystemExit("REFUSED: P2-C1.4 runtime qualification requires pinned Ollama")
    from research.runtime3_confirmatory_prompt_amendment import (
        AMENDMENT_ID,
        ConfirmatoryRuntime3OllamaProvider,
    )
    from runtime3_ollama import PATHOLOGY_RECOVERY_AMENDMENT_ID
    recovery_enabled=os.getenv("RUNTIME3_ENABLE_PATHOLOGICAL_SQL_REPAIR","0")=="1"
    provider=ConfirmatoryRuntime3OllamaProvider(
        os.getenv("OLLAMA_BASE_URL","http://127.0.0.1:11434"),
        os.getenv("OLLAMA_MODEL","llama3.2:1b"),
    )
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
    recovery_by_decision={}
    status_by_decision={}
    runtime_failures=[]
    for c in cases:
        did=c["decision_id"]
        ex=lookup.get((c["db_id"],c["question"]))
        if ex is None: raise SystemExit(f"FAIL: manifest case not found: {did}")
        before=len(evaluator.captures)
        recovery_before=len(provider.pathology_recovery_events)
        if did in e1_ids:
            # E1: reference SQL not scoreable; excluded before any model call.
            status=STATUS_E1
        else:
            try:
                selected, defensibility=run_case(env, ex)
                selected_traces[did]=selected
                defensibility_records[did]=defensibility
                status=STATUS_EVALUABLE
            except RuntimeError as exc:
                # Bounded Runtime3 failure (amendment E2/E3/E4). Never converted
                # into an outcome; the stage is decided only by whether the P0
                # (decision-time evidence) trace completed.
                post=(c["db_id"],c["question"]) in env.p0_traces
                status=STATUS_POST if post else STATUS_PRE
                runtime_failures.append({
                    "decision_id":did,
                    "record_status":status,
                    "failure_stage":"POST_EVIDENCE" if post else "PRE_EVIDENCE",
                    "exception_type":type(exc).__name__,
                    "exception":str(exc)[:2000],
                })
        # Project1's BenchmarkEnvironment.run() swallows every exception inside
        # P0 and returns a trace with termination_reason="runtime_error". A bounded
        # Runtime3 failure there would otherwise look like "no SQL generated" and be
        # scored as P0 incorrect (Y_H=0). Classify it explicitly as E2 instead.
        p0_trace_done=env.p0_traces.get((c["db_id"],c["question"]))
        if (status!=STATUS_E1 and p0_trace_done is not None
                and p0_trace_done.termination_reason=="runtime_error"
                and RUNTIME3_ERROR_RE.match(p0_trace_done.error or "")):
            if status==STATUS_POST:
                runtime_failures.pop()
            status=STATUS_PRE
            selected_traces.pop(did,None); defensibility_records.pop(did,None)
            runtime_failures.append({
                "decision_id":did,
                "record_status":status,
                "failure_stage":"PRE_EVIDENCE",
                "exception_type":"RuntimeError",
                "exception":(p0_trace_done.error or "")[:2000],
            })
        status_by_decision[did]=status
        recovery_by_decision[did]=list(provider.pathology_recovery_events[recovery_before:])
        new=evaluator.captures[before:]
        if status in (STATUS_E1, STATUS_PRE):
            # No completed P0 answer: no decision-time evidence (NO_USABLE_EVIDENCE shape).
            new=[]
        # P0 is the first execution performed by run_case. It is the only
        # evidence eligible for X_W and must precede intervention logic.
        # If P0 produced no SQL, there is legitimately no executable evidence.
        # Under the frozen protocol this is NO_USABLE_EVIDENCE, not a synthetic
        # zero and not a shard-level failure. If SQL existed but no capture was
        # recorded, fail closed because evidence preservation is broken.
        if not new and status in (STATUS_E1, STATUS_PRE):
            p0_ev={
                "db_id":c["db_id"],"columns":None,"rows":None,
                "row_count":None,"column_count":None,
                "evidence_sha256":None,
                "capture_reason":"not_run_e1" if status==STATUS_E1 else "runtime_failure_before_evidence"
            }
        elif not new:
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
                "runtime3_implementation_amendment":AMENDMENT_ID,
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
    # Runtime-failure ledger (stage + exception + recovery events). Written after
    # the evidence lock and kept out of the decision-time evidence artifact.
    for f in runtime_failures:
        f["pathology_recovery_events"]=recovery_by_decision[f["decision_id"]]
    (args.outdir/"runtime_failures.json").write_text(json.dumps({
        "protocol_version":"P2-C1.4-RUNTIME-FAILURE-LEDGER-V2",
        "amendment_id":MISSINGNESS_AMENDMENT_ID,
        "manifest_hash":manifest_hash,
        "records":runtime_failures},indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    from research.spider_official_eval import evaluate_traces
    traces=[]
    post_p0_traces=[]
    trace_to_decision={}
    for c in cases:
        did=c["decision_id"]
        st=status_by_decision[did]
        if st==STATUS_EVALUABLE:
            p0=env.p0_traces[(c["db_id"],c["question"])]
            selected=selected_traces[did]
            for label,tr in (("P0",p0),("P6-IP",selected)):
                d=asdict(tr)
                d["policy"]=label
                traces.append(d)
                trace_to_decision[(label,did)]=d
        elif st==STATUS_POST:
            # P0 completed before the failure: its correctness is defined.
            d=asdict(env.p0_traces[(c["db_id"],c["question"])])
            d["policy"]="P0"
            post_p0_traces.append(d)
            trace_to_decision[("P0",did)]=d
    payload={"dataset_manifest":{"question_file":str(args.questions)},
             "policies":["P0","P6-IP"],"traces":traces}
    official=evaluate_traces(payload,args.database_dir,args.tables_file,args.spider_eval_dir)
    official_post_failure_p0=evaluate_traces(
        {"dataset_manifest":{"question_file":str(args.questions)},"policies":["P0"],"traces":post_p0_traces},
        args.database_dir,args.tables_file,args.spider_eval_dir) if post_p0_traces else {"P0":{"n":0,"execution_accuracy":0.0}}

    outcomes=[]
    aligned=[]
    for c in cases:
        did=c["decision_id"]
        st=status_by_decision[did]
        if st==STATUS_EVALUABLE:
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
        elif st==STATUS_POST:
            # Y_H is undefined (intervention never completed). Only the value
            # implied by the Y_H definition when P0 is incorrect is recorded,
            # separately, for the prespecified sensitivity analysis S1.
            p0_correct=bool(trace_to_decision[("P0",did)].get("official_execution_correct"))
            outcome={"replacement_occurred":None,
                     "p0_correct":p0_correct,"final_correct":None,
                     "y_h":None,"y_h_implied_by_definition":(0 if not p0_correct else None),
                     "locked_after_evidence":True}
        else:
            outcome={"replacement_occurred":None,"p0_correct":None,"final_correct":None,
                     "y_h":None,"y_h_implied_by_definition":None,"locked_after_evidence":True}
        outcomes.append(outcome)
        e=next(x for x in evidence_records if x["decision_id"]==did)
        aligned.append({"decision_id":did,"protocol_version":"P2-C1.4-ALIGNED-V2",
                        "record_status":st,
                        "baseline":e["baseline"],
                        "decision_time_evidence":e["decision_time_evidence"],
                        "intervention_outcome":outcome,
                        "provenance":{
                          "manifest_hash":e["provenance"]["manifest_hash"],
                          "code_version":os.environ.get("PROJECT1_COMMIT","unknown"),
                          "runtime_manifest_hash":e["provenance"]["runtime_manifest_hash"],
                          "runtime3_implementation_amendment":e["provenance"]["runtime3_implementation_amendment"],
                          "runtime3_pathology_recovery_enabled":recovery_enabled,
                          "runtime3_pathology_recovery_amendment":(PATHOLOGY_RECOVERY_AMENDMENT_ID if recovery_enabled else None),
                          "runtime3_pathology_recovery_applied":bool(recovery_by_decision[did]),
                          "missingness_amendment":MISSINGNESS_AMENDMENT_ID,
                          "e1_census_sha256":e1_census_sha,
                          "shard_manifest_hash":manifest_file_hash,
                          "baseline_hash":sha256_json(e["baseline"]),
                          "outcome_record_hash":sha256_json(outcome)}})

    (args.outdir/"outcomes.json").write_text(json.dumps({
        "protocol_version":"P2-C1.4-OUTCOME-V1",
        "evidence_artifact_sha256":evidence_hash,
        "official_spider_execution":official,"records":outcomes},indent=2)+"\n",encoding="utf-8")
    (args.outdir/"aligned_records.json").write_text(json.dumps({
        "protocol_version":"P2-C1.4-ALIGNED-V2","records":aligned},
        indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    recovered_ids=[c["decision_id"] for c in cases if recovery_by_decision[c["decision_id"]]]
    (args.outdir/"pathology_recovery_ledger.json").write_text(json.dumps({
        "amendment_id":PATHOLOGY_RECOVERY_AMENDMENT_ID,
        "enabled":recovery_enabled,
        "decision_count":len(cases),
        "decisions_with_recovery":len(recovered_ids),
        "records":[{"decision_id":d,"events":recovery_by_decision[d]} for d in recovered_ids],
    },indent=2)+"\n",encoding="utf-8")

    metadata={
        "status":"PASS_CONFIRMATORY_ALIGNED_ACQUISITION" if args.confirmatory else "PASS_NON_CONFIRMATORY_ALIGNED_DRY_RUN",
        "confirmatory":bool(args.confirmatory),
        "non_confirmatory":bool(args.non_confirmatory),
        "decision_count":len(evidence_records),
        "decision_time_evidence_sha256":evidence_hash,
        "official_outcome_evaluation":"RUN_AFTER_EVIDENCE_LOCK",
        "official_execution":official,
        "harm_count":sum(x["y_h"] for x in outcomes if x["y_h"] is not None),
        "record_status_counts":{k:sum(1 for v in status_by_decision.values() if v==k) for k in (STATUS_EVALUABLE,STATUS_E1,STATUS_PRE,STATUS_POST)},
        "official_execution_post_failure_p0":official_post_failure_p0,
        "missingness_amendment":MISSINGNESS_AMENDMENT_ID,
        "x_w":"NOT_ANNOTATED_IN_COLLECTOR",
        "runtime3_implementation_amendment":AMENDMENT_ID,
        "runtime3_pathology_recovery_enabled":recovery_enabled,
        "runtime3_pathology_recovery_amendment":(PATHOLOGY_RECOVERY_AMENDMENT_ID if recovery_enabled else None),
        "runtime3_pathology_recovery_decision_count":len(recovered_ids),
        "reason":("Confirmatory aligned outcome-bearing acquisition under frozen protocol."
                  if args.confirmatory else
                  "Dry run proves same-unit evidence/outcome linkage and temporal leakage boundary; it is not confirmatory data.")
    }
    (args.outdir/"runtime_qualification_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps(metadata,indent=2))

if __name__=="__main__":
    main()

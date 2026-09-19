#!/usr/bin/env python3
import argparse, hashlib, json, random
from pathlib import Path

SEEDS={"A":424241,"B":424242}
VERSION="C4_2_4A_WITNESS_V2_2026-09-19"
FORBIDDEN_KEYS={"generated_sql","gold_sql","gold_answer","p0_correctness","intervention","replacement","downstream_outcome","post_hoc","sql_sha256","evidence_sha256","source_artifact_sha256","source_evidence_sha256","latency_ms","llm_calls","cost"}
SQL_PATTERNS=("SELECT ","INSERT ","UPDATE ","DELETE ","DROP ","ALTER ","CREATE ")

def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def forbidden_keys(obj):
    found=[]
    if isinstance(obj,dict):
        for k,v in obj.items():
            if k in FORBIDDEN_KEYS:
                found.append(k)
            found.extend(forbidden_keys(v))
    elif isinstance(obj,list):
        for v in obj:
            found.extend(forbidden_keys(v))
    return found

def git_blob_sha1(p):
    data=Path(p).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--evidence",required=True)
    ap.add_argument("--schema-fixture",required=True)
    ap.add_argument("--manifest",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()

    ev=json.loads(Path(a.evidence).read_text())
    mf=json.loads(Path(a.manifest).read_text())
    cases={c["db_id"]:c for c in mf["cases"]}
    first={x["trace"]["db_id"]:x for x in ev["first"]}
    fixture=json.loads(Path(a.schema_fixture).read_text())
    assert set(cases)==set(first)==set(fixture) and len(cases)==12

    base=[]
    for db_id,c in cases.items():
        db=fixture[db_id]
        lines=[]
        for ti,t in enumerate(db["table_names_original"]):
            cols=[x[1] for x in db["column_names_original"] if x[0]==ti]
            lines.append("TABLE "+t+": "+", ".join(cols))
        e=first[db_id]["captured_evidence"]
        usable=e["row_count"] is not None
        base.append({
          "case_id":c["pilot_case_id"],"db_id":db_id,"question":c["question"],
          "schema":"\n".join(lines),
          "execution_status":"SUCCESS" if usable else "NO_USABLE_EVIDENCE",
          "columns":e["columns"] if usable else [],
          "rows":e["rows"] if usable else [],
          "row_count":e["row_count"],"column_count":e["column_count"],
          "annotations":{"W1":None,"W2":None,"W3":None,"W4":None,"W5":None,"W6":None,"W7":None,"notes":None}
        })

    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    ph={}
    source_hash=sha256(a.evidence)
    generator_sha=git_blob_sha1(__file__)
    codebook_sha=git_blob_sha1(Path(__file__).with_name("C4_2_4A3_WITNESS_CODEBOOK_v2_FROZEN_2026-09-19.md"))
    schema_hash=sha256(a.schema_fixture)
    manifest_hash=sha256(a.manifest)

    for label,seed in SEEDS.items():
        arr=json.loads(json.dumps(base)); random.Random(seed).shuffle(arr)
        packet={
          "packet_version":VERSION,"rater_packet":label,"randomization_seed":seed,
          "source_case_count":12,
          "blinding":{"excluded_information":"No generated query text, reference query/answer, correctness labels, intervention/outcome variables, post-hoc labels, execution provenance hashes, or model/runtime telemetry are exposed."},
          "cases":arr
        }
        raw=json.dumps(packet,indent=2,sort_keys=True)+"\n"
        u=raw.upper()
        assert not any(p in u for p in SQL_PATTERNS)
        assert not forbidden_keys(packet), forbidden_keys(packet)
        assert len(arr)==12 and len({x["case_id"] for x in arr})==12
        p=out/f"C4_2_4A_WITNESS_V2_RATER_{label}.json"; p.write_text(raw)
        ph[label]=sha256(p)

    rec={
      "packet_version":VERSION,
      "source_evidence_sha256":source_hash,
      "generator_blob_sha1":generator_sha,
      "codebook_blob_sha1":codebook_sha,
      "schema_fixture_sha256":schema_hash,
      "manifest_sha256":manifest_hash,
      "rater_A_seed":424241,
      "rater_B_seed":424242,
      "packet_sha256":ph
    }
    (out/"C4_2_4A_WITNESS_V2_PACKET_MANIFEST.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    print(json.dumps(rec,indent=2,sort_keys=True))

if __name__=="__main__":
    main()

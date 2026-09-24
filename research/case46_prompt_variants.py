from pathlib import Path
import hashlib, json, sys
sys.path.insert(0, str((Path("..")/"project1").resolve()))
from app.services.llm import LLMResult, OllamaProvider
from research.spider_benchmark import SpiderDataset

Q=Path("data/confirmatory_questions_source.json"); DB=Path("data/database")
TARGET_DB="insurance_policies"; TARGET_Q="Tell me the the claim date and settlement date for each settlement case."
ESC="This is a post-evidence escalation. Re-check joins, filters, grouping, ordering and nested-query semantics before answering."
dataset=SpiderDataset(question_file=Q,database_dir=DB)
matches=[x for x in dataset.examples if x.db_id==TARGET_DB and x.question==TARGET_Q]
if len(matches)!=1: raise RuntimeError(f"Expected exactly one target, found {len(matches)}")
schema=dataset.schema(TARGET_DB)
base_rules="""You are a senior analytics SQL engineer generating SQLite SQL for a production analytics system.
Generate exactly one read-only SELECT statement.

Rules:
1. Use only the supplied schema and its columns.
2. Never mutate data; no INSERT, UPDATE, DELETE, DDL, PRAGMA, or multiple statements.
3. Return ONLY a JSON object with exactly one key: sql.
4. The sql value must be a valid SQLite SELECT statement.
5. For relative dates such as last month, use the latest date available in the dataset as the reference point, not the current calendar date.
6. Do not reference a table alias that is not defined in the same SELECT.
7. Do not put explanations or markdown in the response.
"""
contaminated=base_rules+"""
8. week_start is stored as ISO text YYYY-MM-DD.
9. For the previous complete month, use SQLite expressions such as date((SELECT MAX(week_start) FROM store_week), 'start of month', '-1 month').
10. The current dataset has one analytical table: store_week. Prefer a direct aggregation over this table.
11. Do NOT self-join store_week. Do NOT create derived-table aliases such as T1/T2 unless the supplied schema explicitly requires a multi-table join.
12. For "highest sales", "top stores by sales", or equivalent, use SUM(sales), GROUP BY store_id, ORDER BY the aggregate alias DESC, and LIMIT 10.
"""
clean=base_rules
variants=[
("A_contaminated_no_escalation",contaminated,False),
("B_contaminated_escalation",contaminated,True),
("C_clean_no_escalation",clean,False),
("D_clean_escalation",clean,True),
]
provider=OllamaProvider("http://127.0.0.1:11434","llama3.2:1b")
results=[]
for name,rules,esc_on in variants:
    prompt=rules+"\nSchema:\n"+schema+"\n"
    if esc_on: prompt+="\n"+ESC+"\n"
    prompt+="Question:\n"+TARGET_Q
    cap={}
    def chat(p, cap=cap):
        cap.update(prompt=p,prompt_sha256=hashlib.sha256(p.encode()).hexdigest(),prompt_chars=len(p))
        return OllamaProvider._chat(provider,p)
    provider._chat=chat
    try:
        result=provider.generate_sql(TARGET_Q,schema)
        results.append({"variant":name,"status":"PASS","prompt_sha256":cap["prompt_sha256"],"prompt_chars":cap["prompt_chars"],"output_tokens":result.output_tokens,"output_sha256":hashlib.sha256(result.text.encode()).hexdigest(),"sql":result.text})
    except Exception as e:
        results.append({"variant":name,"status":"FAIL","prompt_sha256":cap.get("prompt_sha256"),"prompt_chars":cap.get("prompt_chars"),"exception":type(e).__name__+": "+str(e)})
out=Path("artifacts/case46_prompt_variants"); out.mkdir(parents=True,exist_ok=True)
(out/"case46_prompt_variants.json").write_text(json.dumps({"status":"NON_CONFIRMATORY_PROMPT_VARIANTS","decision_id":"P2C14-CONF-000046","variants":results},indent=2),encoding="utf-8")
print(json.dumps(results,indent=2))

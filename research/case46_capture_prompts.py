import hashlib
import json
import sys
from pathlib import Path

PROJECT1_ROOT = Path("..") / "project1"
sys.path.insert(0, str(PROJECT1_ROOT.resolve()))
sys.path.insert(0, str(Path(".").resolve()))

from app.services.llm import LLMResult, OllamaProvider
from research.spider_benchmark import SpiderDataset

TARGET_DECISION_ID = "P2C14-CONF-000046"
TARGET_DB_ID = "insurance_policies"
TARGET_QUESTION = "Tell me the the claim date and settlement date for each settlement case."

QUESTION_FILE = Path("data/confirmatory_questions_source.json")
DATABASE_DIR = Path("data/database")

ESCALATION_SENTENCE = (
    "This is a post-evidence escalation. Re-check joins, filters, grouping, "
    "ordering and nested-query semantics before answering."
)


def main() -> None:
    dataset = SpiderDataset(
        question_file=QUESTION_FILE,
        database_dir=DATABASE_DIR,
    )

    matches = [
        example
        for example in dataset.examples
        if example.db_id == TARGET_DB_ID
        and example.question == TARGET_QUESTION
    ]

    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one target case, found {len(matches)}"
        )

    example = matches[0]
    schema = dataset.schema(TARGET_DB_ID)

    provider = OllamaProvider(
        base_url="http://127.0.0.1:11434",
        model="llama3.2:1b",
    )

    captured = []

    def capture_chat(prompt: str) -> LLMResult:
        captured.append(
            {
                "call_index": len(captured) + 1,
                "prompt_chars": len(prompt),
                "prompt_sha256": hashlib.sha256(
                    prompt.encode("utf-8")
                ).hexdigest(),
                "prompt": prompt,
            }
        )
        return LLMResult(
            text='{"sql":"SELECT 1"}',
            model="forensic-no-ollama",
        )

    provider._chat = capture_chat

    # Construct the exact frozen Project1 P0 prompt.
    provider.generate_sql(
        example.question,
        schema,
    )

    # Construct the exact frozen Project1 escalated prompt.
    provider.generate_sql(
        example.question,
        schema + "\n\n" + ESCALATION_SENTENCE,
    )

    outdir = Path("artifacts/case46_prompt_capture")
    outdir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "status": "NON_CONFIRMATORY_PROMPT_CAPTURE",
        "decision_id": TARGET_DECISION_ID,
        "db_id": TARGET_DB_ID,
        "question": TARGET_QUESTION,
        "schema_chars": len(schema),
        "schema_sha256": hashlib.sha256(schema.encode("utf-8")).hexdigest(),
        "records": captured,
        "ollama_called": False,
    }

    artifact_path = outdir / "case46_prompts.json"
    artifact_path.write_text(
        json.dumps(artifact, indent=2),
        encoding="utf-8",
    )

    print("PROMPTS_CAPTURED:", len(captured))
    for record in captured:
        print(
            f"CALL={record['call_index']} "
            f"CHARS={record['prompt_chars']} "
            f"SHA256={record['prompt_sha256']}"
        )
    print("OLLAMA_CALLED: False")
    print("ARTIFACT:", artifact_path)


if __name__ == "__main__":
    main()

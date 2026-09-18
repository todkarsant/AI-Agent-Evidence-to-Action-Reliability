# Ollama Runtime Smoke Test — 2026-09-18

## Result

**PASS — generation works under the recovered Ollama runtime.**

The smoke test invoked the local Ollama server at `127.0.0.1:11434` using model `llama3.2:1b`.

The server returned a completed chat generation with `done: true` and `done_reason: stop`.

## Request configuration

- Ollama version: 0.33.3
- Model: `llama3.2:1b`
- Stream: false
- Response format: JSON
- Temperature: 0
- Request type: direct HTTP invocation of the recovered local Ollama server
- Prompt: requested a JSON object with exactly one `sql` key whose value is `SELECT 1;`

## Observed response

The model returned JSON-formatted assistant content containing:

`{"sql":"SELECT 1;"}`

The response was:

- `done = true`
- `done_reason = stop`
- `prompt_eval_count = 47`
- `eval_count = 13`
- `total_duration = 42,533,698,984 ns` (approximately 42.5 s)
- `load_duration = 41,313,350,021 ns` (approximately 41.3 s)
- `prompt_eval_duration = 605,862,000 ns` (approximately 0.606 s)
- `eval_duration = 546,908,000 ns` (approximately 0.547 s)

These timings are observations from this single smoke-test invocation and are not benchmark performance estimates.

## Interpretation

This establishes:

1. The recovered Ollama 0.33.3 server is reachable.
2. The requested `llama3.2:1b` model can be loaded and invoked.
3. JSON response mode works for the request.
4. Deterministic generation configuration (`temperature: 0`) is accepted.
5. The recovered runtime is ready for the next software-path validation step.

This does **not** establish:

- byte-identical historical model reproduction;
- historical P0 reproducibility;
- benchmark accuracy;
- throughput or representative latency;
- determinism across repeated executions;
- correctness of the historical Python `OllamaProvider` path.

## Next gate

Run the exact historical `OllamaProvider.generate_sql()` implementation from benchmark commit `1765680283df63232018bf7b827d1576c81c3a61` against one fresh pilot case before executing the full 120-case corpus.

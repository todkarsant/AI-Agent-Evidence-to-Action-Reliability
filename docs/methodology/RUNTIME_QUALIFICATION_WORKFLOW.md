# Runtime Qualification Workflow

This workflow is a manually triggered qualification test for the Project 2 execution runtime.

It deliberately does **not** run the 120-case fresh corpus.

## Controls

- Ollama is pinned to 0.33.3.
- The Ollama archive is downloaded from the tagged GitHub release and SHA-256 recorded.
- The executable SHA-256 is recorded.
- The server API version is checked.
- The requested model is pulled and its Ollama metadata/digest is captured.
- Python 3.11 is used as the historical major/minor runtime target.
- The exact historical OllamaProvider interface is exercised.
- Runtime evidence is uploaded as a GitHub Actions artifact.
- The workflow is manual-only.

## Important limitation

GitHub Actions does not by itself prove byte-identical historical reproduction. The original benchmark did not record the historical model artifact digest, and a hosted runner is not the original historical machine.

This workflow establishes controlled runtime qualification, not exact historical reproduction.

## Promotion rule

A successful runtime qualification is necessary but not sufficient for the fresh P0 experiment. The 120-case run should only be promoted after:

1. provider smoke test passes;
2. runtime/model provenance is captured;
3. fresh input manifest is verified;
4. the experiment-specific workflow is frozen.

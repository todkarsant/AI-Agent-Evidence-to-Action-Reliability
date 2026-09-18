# Recovered Runtime Provenance — 2026-09-18

## Purpose

Record the recovered execution environment for the fresh P0 methodological pilot and distinguish functional recovery from exact historical reproducibility.

## Historical benchmark configuration

Source repository: `todkarsant/Enterprise-Analytics-Copilot`

Historical benchmark code commit:

`1765680283df63232018bf7b827d1576c81c3a61`

Historical benchmark runner:

`research.spider_benchmark_isolated`

Historical provider:

`OllamaProvider`

Historical Ollama version:

`0.33.3`

Historical model name:

`llama3.2:1b`

Historical model artifact digest:

**Not recorded in the historical benchmark artifacts available to this study.**

Historical Spider evaluator commit:

`b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c`

Historical unseen-schema seed:

`1729`

Historical per-policy timeout:

150 seconds

Historical Python runtime recorded:

Python 3.11.16

## Recovered runtime

Platform:

- Windows host
- Ubuntu 24.04 LTS
- WSL2

Current kernel observed:

`6.18.33.2-microsoft-standard-WSL2`

Current clean research environment:

Python 3.11.15 virtual environment

Virtual environment:

`~/research-runtime/p1-p2-c4`

Ollama:

0.33.3

Ollama archive:

`ollama-linux-amd64-0.33.3.tar.zst`

Archive size:

1,433,825,108 bytes

Archive SHA-256:

`c13cea8f3389db4145f8a6cb88d1747242a48639d7c13e3bda7c1ebdc6eebb2f`

Archive integrity check:

`zstd -t` passed.

Ollama executable SHA-256:

`7deaad14177b824d8fcff7136d4418c0111d2db35fa872a5071fa8db5b8db527`

Ollama server API version observed:

`0.33.3`

## Recovered model artifact

Model:

`llama3.2:1b`

Ollama manifest digest:

`baf6a787fdffd633537aa2eb51cfd54cb93ff08e28040095462bb63daf552878`

Underlying model blob:

`74701a8c35f6c8d9a4b91f3f3497643001d63e0c7a84e085bed452548fa88d45`

Model size:

1,321,098,329 bytes

Architecture:

Llama

Parameter count:

1,235,814,432

Quantization:

Q8_0

Context length:

131,072

## Reproducibility conclusion

**Functional runtime recovery: PASS.**

The historical provider protocol and requested Ollama/model configuration have been recovered sufficiently to proceed with a controlled fresh pilot after smoke testing.

**Byte-identical historical model reproduction: NOT PROVEN.**

The recovered model digest cannot be compared against a historical digest because the original benchmark did not record one.

**Python patch-level identity: NOT EXACT.**

Historical records indicate Python 3.11.16; the recovered clean environment uses Python 3.11.15.

These are provenance limitations and must be reported wherever exact historical reproduction is discussed.

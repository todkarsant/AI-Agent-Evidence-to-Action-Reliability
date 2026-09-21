# P2-C1.4 Runtime Amendment 2 — NLTK dependency required by pinned Spider evaluator

Date: 2026-09-21

Status: INFRASTRUCTURE / RUNTIME AMENDMENT — CONFIRMATORY COLLECTION REMAINS BLOCKED UNTIL REQUALIFIED

## Trigger

Dry-run #41 (35600859473) reached the pinned Project 1 Spider official evaluator and failed because the pinned Spider process_sql.py imports nltk.word_tokenize, while the pinned Project 1 requirements.txt does not declare NLTK.

The failure was: ModuleNotFoundError: No module named 'nltk'

This is a runtime dependency defect, not a scientific-data or outcome-model result.

## Correction

The dry-run and confirmatory acquisition workflows shall explicitly install:

- nltk==3.9.4
- the NLTK punkt_tab tokenizer data required by the pinned evaluator's word_tokenize call

The workflow must verify that word_tokenize can execute before collection begins.

NLTK 3.9.4 is selected because its published package metadata supports the Python versions used by current GitHub-hosted runners; the dependency is explicitly version-pinned rather than left to a floating install.

## Scientific-scope statement

This amendment changes only the environment required to execute the already-pinned Spider evaluator. It does not change:

- the Spider archive or commit;
- Project 1 P6-IP logic;
- prompts/model/temperature;
- decision-time evidence definition;
- outcome definition Y_H;
- X_W construction or annotation;
- cohort population or manifest generation;
- statistical model, scoring rule, resampling, or stopping rule.

Because the runtime environment changed, the confirmatory protocol authorization identifier is advanced from:

 P2-C1.4-CONFIRMATORY-V1-RUNTIME1-2026-09-21 

to:

 P2-C1.4-CONFIRMATORY-V1-RUNTIME2-2026-09-21 

No confirmatory acquisition is accepted from Runtime1 after this amendment.

## Qualification requirement

A fresh non-confirmatory dry run must pass end-to-end, including official Spider execution evaluation, with the new runtime. Only after that pass may the confirmatory acquisition be considered re-qualified for collection.

## Provenance

- Failing dry run: 35600859473
- Failing head: eef190fafe49dd402c63c2a2e84fe0bb14cd0e14
- Pinned Project 1 commit: 7c1864a5619af7118c690f8de72eab57dc0cdc93
- Pinned Spider commit: b7b5b8c890cd30e35427348bb9eb8c6d1350ca7c
- Spider archive SHA-256: 00636695dabed6b5f4b8328a16b13e069a2f16591d5efcce57660669c85b121b

## Gate consequence

Current state remains P2-C1.4 confirmatory collection BLOCKED. The next valid state transition is:

Runtime2 dry-run PASS → forensic runtime audit → confirmatory acquisition

No cohort lock or X_W annotation is authorized by this amendment alone.


## Runtime2 workflow trigger

This amendment remains the governing runtime correction for the requalification run.

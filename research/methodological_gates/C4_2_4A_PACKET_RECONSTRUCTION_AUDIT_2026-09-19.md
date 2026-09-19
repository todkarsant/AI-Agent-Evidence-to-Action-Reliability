# C.4.2.4-A — Annotation Packet Reconstruction Audit

**Date:** 2026-09-19  
**Status:** EXACT HISTORICAL PACKET VERIFICATION NOT POSSIBLE FROM CURRENTLY PRESERVED ARTIFACTS

## Question audited

Can the two previously described C4.2.4-A human-rater packets be reconstructed and cryptographically verified against the recorded packet SHA-256 values?

## Findings

### 1. The repository records packet hashes, but not the packet files

The C4.2.4-A feasibility record records:

- Rater A SHA-256: `92a1c456ab501c9f2ce1823bd110884f64649c0a97f8c9af134ad4357c4b5732`
- Rater B SHA-256: `04d51ad99a194721fd9bf87cdaafd988396cb86a46f97425612e640c9a69143f`
- Rater A seed: `424241`
- Rater B seed: `424242`

The current repository tree contains no corresponding packet files, annotation CSVs, packet-generation script, or committed packet-generation manifest.

### 2. The packet-generation provenance is incomplete

The feasibility record identifies the source as `evidence_capture_pilot12.json`, but its recorded source SHA is still `__SOURCE__`.

The currently audited GitHub Actions artifact for run 35367903444 is available and contains `evidence_capture_pilot12.json`, but that artifact does not contain the original Rater A/B packet files or a packet-generation program.

Therefore the recorded packet hashes cannot be independently recomputed from the currently preserved repository artifacts.

### 3. The historical hash-recording commits confirm the hashes but do not recover the bytes

The repository history contains commits recording/correcting the packet hashes:

- `5f51e4970ffe7ca8040ea199c370d9623c43902e` — prepare blinded annotation pilot
- `97960ca38ccbe83c686abf60e40d2c2491391f5f` — correct packet hashes
- `1a585780735049bfe2424929f36a3cdd7f8897ab` — record exact packet hash

Those commits modify only the methodological record; they do not contain the packet payloads or a reproducible generator.

### 4. Current codebook state creates a second provenance problem

`C4_2_4_EVIDENCE_OBLIGATION_CODEBOOK_v1.md` is explicitly frozen for pilot annotation and defines O1-O8, including cardinality/completeness.

The later `C4_2_4A3_WITNESS_CODEBOOK_v2_DRAFT_2026-09-18.md` is explicitly marked DRAFT and redesigns the construct to W1-W7, removing cardinality/completeness.

Therefore a newly generated packet based on v2 cannot honestly be described as the historical packet whose SHA-256 is recorded above.

## Scientific decision

**Do not silently reconstruct a byte-different packet and call it the historical packet.**

The exact historical packet hashes are **not currently verifiable** from preserved artifacts.

A new human-annotation cohort is permissible only after the currently intended W1-W7 codebook is formally frozen and a reproducible packet-generation artifact is committed. That cohort must receive a new version identifier and new SHA-256 values.

## Required next step

Before human annotation begins:

1. finalize/freeze the intended W1-W7 codebook;
2. create a deterministic packet-generation script;
3. regenerate the 12-case blinded packets from the audited evidence-capture artifact;
4. run automated leakage checks;
5. record source/artifact/codebook/generator hashes;
6. commit the packet files or otherwise preserve immutable copies;
7. verify the resulting packet SHA-256 values;
8. then issue the two packets to genuinely independent raters.

No claim of successful reconstruction of the historical Rater A/B packets is made by this audit.

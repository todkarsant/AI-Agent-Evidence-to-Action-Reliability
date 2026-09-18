# Data Governance

This directory records dataset provenance and controls.

- `manifests/` — immutable or hash-addressed dataset manifests.
- `provenance/` — acquisition and preparation records.
- `exclusions/` — explicit exclusions and reasons.
- `leakage_controls/` — documentation preventing gold/post-hoc leakage.

Raw benchmark data should not be duplicated unnecessarily when an authoritative external acquisition can be identified by cryptographic hash and documented provenance.

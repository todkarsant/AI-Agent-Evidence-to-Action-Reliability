# C.4.2.3 Fresh Corpus Provenance

## Purpose

Record the corpus selected for the fresh measurement pilot and its separation from historical P1/P6 data.

## Source corpus

Spider 1.0 archive:

`/mnt/data/spider_data.zip`

Archive size:

205,800,266 bytes

Archive SHA-256:

`00636695dabed6b5f4b8328a16b13e069a2f16591d5efcce57660669c85b121b`

Verified source files include:

- `train_spider.json` — 7,000 records
- `train_others.json` — 1,659 records
- `dev.json` — 1,034 records
- `tables.json` — 166 databases

## Fresh pilot

Frozen pilot size:

**120 cases**

Schemas:

**12 schemas, 10 cases per schema**

Selected schemas:

- academic
- activity_1
- aircraft
- allergy_1
- apartment_rentals
- architecture
- assets_maintenance
- baseball_1
- behavior_monitoring
- bike_1
- body_builder
- book_2

## Historical separation

Historical P1/P6 schemas:

- car_1
- concert_singer
- flight_2
- pets_1
- student_transcripts_tracking

Fresh/historical schema overlap:

**0**

Fresh pilot question overlap with historical trace questions:

**0**

All selected database hashes were checked against the frozen manifest.

## Leakage control

The internal frozen manifest contains gold-derived fields including `query_toks_no_value`. These fields are explicitly excluded from annotator-facing execution input.

The clean execution input is:

`C4_2_3B_fresh_execution_input.json`

SHA-256:

`4dc86fb523effc85583651d24f197ffbba297b778262673e4d8fbd6fcf63b8`

Excluded fields:

- `query`
- `query_toks`
- `query_toks_no_value`
- `gold_sql`
- `answer`

## Gate result

### C.4.2.3-A — PASS

Fresh corpus acquisition and historical-overlap control passed.

### C.4.2.3-B — PASS

Clean execution input with gold-derived fields removed passed.

### C.4.2.3-C — PENDING

Fresh P0 execution must not be treated as complete until runtime smoke testing and execution provenance are recorded.

# Runtime Reproducibility

Runtime records must capture enough information to distinguish functional recovery from exact historical reproducibility.

Required classes include:

- operating system/runtime;
- Python version;
- benchmark commit;
- provider implementation;
- model name and digest;
- serving runtime/version;
- evaluator commit;
- environment variables/configuration;
- acquisition timestamps and file hashes where available.

Do not infer missing historical provenance.

from research.cohort.validate_P2_C1_4_aligned_records import validate_record


def test_non_evaluable_runtime_failure_is_valid_without_synthetic_outcome():
    record = {
        "decision_id": "P2C14-CONF-000091",
        "protocol_version": "P2-C1.4-ALIGNED-V2",
        "record_status": "NON_EVALUABLE_RUNTIME_FAILURE",
        "baseline": {"execution_ok": True, "row_count": 1, "column_count": 1},
        "decision_time_evidence": {
            "question": "q",
            "database_id": "film_rank",
            "schema": "schema",
            "returned_columns": ["x"],
            "returned_rows": [[1]],
            "row_count": 1,
            "column_count": 1,
            "evidence_hash": None,
            "captured_before_intervention": True,
        },
        "intervention_outcome": {
            "decision_id": "P2C14-CONF-000091",
            "record_status": "NON_EVALUABLE_RUNTIME_FAILURE",
            "replacement_occurred": None,
            "p0_correct": None,
            "final_correct": None,
            "y_h": None,
            "locked_after_evidence": None,
        },
        "runtime_failure": {
            "decision_id": "P2C14-CONF-000091",
            "record_status": "NON_EVALUABLE_RUNTIME_FAILURE",
            "failure_class": "RUNTIME3_BOUNDED_GENERATION_FAILURE",
            "exception_type": "RuntimeError",
            "exception": "bounded generation failure",
        },
        "provenance": {"manifest_hash": "m"},
    }
    validate_record(record, set())

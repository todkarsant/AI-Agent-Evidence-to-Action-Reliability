from research.cohort.collect_P2_C1_4_aligned_cohort import _has_complete_outcome_trace


def test_complete_outcome_trace_requires_both_policy_keys():
    traces = {
        ("P0", "P2C14-CONF-000001"): {"trace": "p0"},
        ("P6-IP", "P2C14-CONF-000001"): {"trace": "p6"},
    }
    assert _has_complete_outcome_trace(traces, "P2C14-CONF-000001") is True


def test_missing_one_policy_trace_is_not_evaluable():
    traces = {
        ("P0", "P2C14-CONF-000001"): {"trace": "p0"},
    }
    assert _has_complete_outcome_trace(traces, "P2C14-CONF-000001") is False


def test_runtime_failure_does_not_have_a_policy_trace_pair():
    traces = {}
    assert _has_complete_outcome_trace(traces, "P2C14-CONF-000091") is False

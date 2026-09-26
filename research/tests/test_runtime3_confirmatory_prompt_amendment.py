from research.runtime3_confirmatory_prompt_amendment import (
    AMENDED_ESCALATION_SENTENCE,
    CURRENT_ESCALATION_SENTENCE,
    apply_confirmatory_prompt_amendment,
)


def test_non_escalation_prompt_is_unchanged():
    prompt = "schema: shop\\nquestion: find addresses"
    amended, changed = apply_confirmatory_prompt_amendment(prompt)
    assert amended == prompt
    assert changed is False


def test_exact_escalation_sentence_is_replaced_once():
    prompt = (
        "schema: insurance_policies\\n"
        + CURRENT_ESCALATION_SENTENCE
        + "\\nanswer as JSON"
    )
    amended, changed = apply_confirmatory_prompt_amendment(prompt)
    assert changed is True
    assert CURRENT_ESCALATION_SENTENCE not in amended
    assert amended.count(AMENDED_ESCALATION_SENTENCE) == 1


def test_multiple_escalation_sentences_fail_closed():
    prompt = CURRENT_ESCALATION_SENTENCE + "\\n" + CURRENT_ESCALATION_SENTENCE
    try:
        apply_confirmatory_prompt_amendment(prompt)
    except RuntimeError as exc:
        assert "expected at most one" in str(exc)
    else:
        raise AssertionError("expected duplicate escalation prompt to fail closed")

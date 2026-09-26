"""Explicit P2-C1.4 Runtime3 implementation amendment.

The pinned Project1 prompt construction remains unchanged. This module applies
the already-qualified single-sentence Runtime3 correction at the provider
boundary. It is used only by the P2-C1.4 confirmatory collector/smoke path.
"""

from __future__ import annotations

from runtime3_ollama import Runtime3OllamaProvider

AMENDMENT_ID = "P2-C1.4-RUNTIME3-ESCALATION-WORDING-AMENDMENT-2026-09-26"

CURRENT_ESCALATION_SENTENCE = (
    "This is a post-evidence escalation. Re-check joins, filters, grouping, "
    "ordering and nested-query semantics before answering."
)

AMENDED_ESCALATION_SENTENCE = (
    "This is a post-evidence escalation. Re-check the SQL against the schema "
    "and question before answering."
)


def apply_confirmatory_prompt_amendment(prompt: str) -> tuple[str, bool]:
    """Replace at most one exact frozen escalation sentence.

    Zero occurrences are valid because not every provider call is an escalation.
    More than one occurrence fails closed rather than silently changing multiple
    prompt locations.
    """
    occurrences = prompt.count(CURRENT_ESCALATION_SENTENCE)
    if occurrences > 1:
        raise RuntimeError(
            "Confirmatory Runtime3 escalation amendment refused the prompt: "
            f"expected at most one exact escalation sentence, found {occurrences}."
        )
    if occurrences == 0:
        return prompt, False
    return (
        prompt.replace(CURRENT_ESCALATION_SENTENCE, AMENDED_ESCALATION_SENTENCE, 1),
        True,
    )


class ConfirmatoryRuntime3OllamaProvider(Runtime3OllamaProvider):
    """Runtime3 provider with the explicit, versioned wording amendment."""

    def _chat(self, prompt: str):
        amended_prompt, _ = apply_confirmatory_prompt_amendment(prompt)
        return super()._chat(amended_prompt)

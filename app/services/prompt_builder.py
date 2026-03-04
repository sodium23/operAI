from __future__ import annotations

import json


class PromptBuilder:
    """Step 2: Build Claude prompt from parsed intent."""

    REQUIRED_FIELDS = [
        "title",
        "goals",
        "success_metrics",
        "user_stories",
        "acceptance_criteria",
        "technical_requirements",
        "non_functional_requirements",
        "risk_register",
        "assumptions",
        "clarification_questions",
    ]

    def build(self, intent: dict, raw_input: str) -> str:
        return (
            "You are a senior PM agent. Return strictly valid JSON with these fields: "
            f"{', '.join(self.REQUIRED_FIELDS)}.\n"
            "Include edge cases and assumptions explicitly."
            "\nParsed intent:\n"
            f"{json.dumps(intent, indent=2)}"
            "\nUser input:\n"
            f"{raw_input}\n"
            "Ensure each list field has at least 3 concise items where possible."
        )

from __future__ import annotations

from typing import Any

from app.models.schemas import StructuredPRD


class ResultParser:
    """Step 3: Parse and validate LLM response into typed structured JSON."""

    def parse(self, result: dict[str, Any]) -> StructuredPRD:
        normalized = {k: v for k, v in result.items()}
        # Ensure required fields exist even if model misses some.
        for field in StructuredPRD.model_fields:
            normalized.setdefault(field, [] if field != "title" else "Untitled PRD")
        if not isinstance(normalized.get("title"), str):
            normalized["title"] = "Untitled PRD"
        for field in StructuredPRD.model_fields:
            if field == "title":
                continue
            value = normalized.get(field)
            if isinstance(value, str):
                normalized[field] = [value]
            elif not isinstance(value, list):
                normalized[field] = []
        return StructuredPRD(**normalized)

from __future__ import annotations

from collections import Counter


class IntentParser:
    """Step 1: Parse user intent from unstructured input."""

    def parse(self, input_text: str, input_type: str) -> dict:
        words = [w.strip(".,!?-\n").lower() for w in input_text.split() if w.strip()]
        keywords = [w for w, count in Counter(words).items() if len(w) > 4 and count > 1]
        sentences = [segment.strip() for segment in input_text.replace("\n", " ").split(".") if segment.strip()]
        primary_goal = sentences[0] if sentences else input_text[:120]

        return {
            "input_type": input_type,
            "primary_goal": primary_goal,
            "keywords": keywords[:8],
            "raw_length": len(input_text),
            "ambiguity_flags": self._detect_ambiguity(input_text),
        }

    def _detect_ambiguity(self, text: str) -> list[str]:
        flags = []
        lowered = text.lower()
        if "maybe" in lowered or "something like" in lowered:
            flags.append("uncertain_scope")
        if len(text.split()) < 12:
            flags.append("low_context")
        if "etc" in lowered:
            flags.append("incomplete_requirements")
        return flags

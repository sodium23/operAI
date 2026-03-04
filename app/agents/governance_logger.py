from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from app.core.config import settings
from app.models.schemas import GovernanceLog


class GovernanceLogger:
    EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

    def create_entry(self, prompt: str, model: str, output_text: str = "") -> GovernanceLog:
        estimated_input_tokens = max(1, len(prompt) // 4)
        estimated_output_tokens = max(1, len(output_text) // 4)
        pii_detected = bool(self.EMAIL_REGEX.search(prompt))
        entry = GovernanceLog(
            prompt=prompt,
            model=model,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            pii_detected=pii_detected,
        )
        self._persist(entry)
        return entry

    def _persist(self, entry: GovernanceLog) -> None:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            **entry.model_dump(),
        }
        with open(settings.governance_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")

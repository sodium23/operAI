from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import settings


class ClaudeClient:
    def __init__(self, api_key: str | None = None, model: str | None = None, mock: bool | None = None):
        self.api_key = api_key or settings.claude_api_key
        self.model = model or settings.claude_model
        self.mock = settings.mock_llm if mock is None else mock

    async def generate_structured_content(self, prompt: str, intent: dict[str, Any]) -> dict[str, Any]:
        if self.mock or not self.api_key:
            return self._mock_response(intent)
        return await self._real_call(prompt)

    async def _real_call(self, prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "max_tokens": 1200,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        text_chunks = []
        for item in data.get("content", []):
            if item.get("type") == "text":
                text_chunks.append(item.get("text", ""))
        text_output = "\n".join(text_chunks).strip()

        try:
            return json.loads(text_output)
        except json.JSONDecodeError:
            return self._fallback_from_text(text_output)

    def _fallback_from_text(self, text_output: str) -> dict[str, Any]:
        base = self._mock_response({"primary_goal": "Convert free-form response to JSON"})
        base["assumptions"].append("Model returned non-JSON output; fallback parser used.")
        base["clarification_questions"].append("Can you confirm any details omitted by fallback parsing?")
        return base

    def _mock_response(self, intent: dict[str, Any]) -> dict[str, Any]:
        goal = intent.get("primary_goal", "Define and deliver value")
        return {
            "title": f"PRD: {goal}",
            "goals": [goal, "Provide predictable execution workflow"],
            "success_metrics": [
                "PRD generated in under 10 seconds",
                "All required PRD fields are populated",
                "Stakeholder clarification loop closed within 2 iterations",
            ],
            "user_stories": [
                "As a product manager, I want structured PRDs from rough ideas so planning is faster.",
                "As an engineer, I want clear acceptance criteria so implementation is testable.",
                "As a stakeholder, I want explicit assumptions and edge cases so risk is visible.",
            ],
            "acceptance_criteria": [
                "PRD JSON contains all mandatory schema fields",
                "At least 3 user stories and 3 acceptance criteria are generated",
                "Clarification questions are produced when ambiguity exists",
            ],
            "technical_requirements": [
                "FastAPI endpoints for generation and refinement",
                "Configurable LLM provider abstraction",
                "Governance logging with prompt/usage metadata",
            ],
            "non_functional_requirements": [
                "P95 response latency under 2 seconds in mock mode",
                "Modular architecture for additional agents",
                "Deterministic output schema validation",
            ],
            "risk_register": [
                "Ambiguous requirements may cause scope drift",
                "LLM hallucination could introduce invalid assumptions",
                "Insufficient context can reduce output quality",
            ],
            "assumptions": [
                "Initial rollout targets internal teams",
                "Claude API availability is stable",
                "Token-based usage estimates are sufficient for prototype finance",
            ],
            "clarification_questions": [
                "What edge cases should be prioritized for launch?",
                "Are there compliance constraints for generated artifacts?",
                "Should execution packs integrate directly with CI/CD tooling?",
            ],
        }

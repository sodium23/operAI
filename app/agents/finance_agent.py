from __future__ import annotations

from app.core.config import settings
from app.models.schemas import FinanceEstimate, GovernanceLog


class FinanceAgent:
    def estimate(self, governance: GovernanceLog) -> FinanceEstimate:
        total_tokens = governance.estimated_input_tokens + governance.estimated_output_tokens
        cost = round((total_tokens / 1000) * settings.token_cost_per_1k, 6)
        return FinanceEstimate(estimated_cost_usd=cost, token_usage=total_tokens)

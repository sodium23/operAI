from __future__ import annotations

from app.models.schemas import EvaluationReport, StructuredPRD


class EvaluationEngine:
    def score(self, prd: StructuredPRD) -> EvaluationReport:
        required_lists = [
            prd.goals,
            prd.success_metrics,
            prd.user_stories,
            prd.acceptance_criteria,
            prd.technical_requirements,
            prd.non_functional_requirements,
            prd.risk_register,
            prd.assumptions,
            prd.clarification_questions,
        ]
        filled = sum(1 for lst in required_lists if len(lst) >= 2)
        completeness = round(filled / len(required_lists), 3)
        risk_confidence = round(max(0.1, min(1.0, len(prd.risk_register) / 5)), 3)
        assumption_density = round(len(prd.assumptions) / max(1, len(prd.user_stories)), 3)
        hallucination_likelihood = round(max(0.0, 1.0 - (completeness * 0.7 + risk_confidence * 0.3)), 3)
        return EvaluationReport(
            completeness_score=completeness,
            risk_confidence_score=risk_confidence,
            assumption_density=assumption_density,
            hallucination_likelihood=hallucination_likelihood,
        )

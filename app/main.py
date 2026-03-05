from __future__ import annotations

from fastapi import FastAPI

from app.agents.pm_agent import PMAgent
from app.core.config import settings
from app.models.schemas import (
    GenerateResponse,
    PRDTestResponse,
    RefineRequest,
    RefineResponse,
    RefineIteration,
    UXFlowRequest,
    UXFlowResponse,
    UserInput,
)

app = FastAPI(title=settings.app_name)
agent = PMAgent()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "backend": "FastAPI backend running",
        "claude": "Claude (primary) connected" if (not settings.mock_llm and settings.claude_api_key) else "Claude (primary) mock mode",
    }


@app.post("/generate-pack", response_model=GenerateResponse)
async def generate_pack(payload: UserInput) -> GenerateResponse:
    execution_pack = await agent.run(payload.input_text, payload.input_type)
    return GenerateResponse(
        message="PM Agent generating structured JSON",
        execution_pack=execution_pack,
    )


@app.post("/refine-until-stable", response_model=RefineResponse)
async def refine_until_stable(payload: RefineRequest) -> RefineResponse:
    threshold = payload.stability_threshold or settings.stability_threshold
    max_iters = payload.max_iterations or settings.max_refinement_iterations
    iterations = []
    final_pack = None

    for idx in range(1, max_iters + 1):
        current_input = payload.input_text + f"\nRefinement iteration {idx}: increase specificity and reduce ambiguity."
        final_pack = await agent.run(current_input, payload.input_type)
        confidence = round((final_pack.evaluation.completeness_score + final_pack.evaluation.risk_confidence_score) / 2, 3)
        iterations.append(
            RefineIteration(
                iteration=idx,
                confidence=confidence,
                changes_summary="Updated prompt with additional specificity and ambiguity reduction guidance.",
            )
        )
        if confidence >= threshold:
            return RefineResponse(
                stable=True,
                achieved_confidence=confidence,
                iterations=iterations,
                final_execution_pack=final_pack,
            )

    assert final_pack is not None
    return RefineResponse(
        stable=False,
        achieved_confidence=iterations[-1].confidence,
        iterations=iterations,
        final_execution_pack=final_pack,
    )


@app.post("/run-prd-tests", response_model=PRDTestResponse)
async def run_prd_tests(payload: UserInput) -> PRDTestResponse:
    pack = await agent.run(payload.input_text, payload.input_type)
    return agent.run_prd_tests(pack.structured_prd)


@app.post("/ux-flow", response_model=UXFlowResponse)
async def ux_flow(payload: UXFlowRequest) -> UXFlowResponse:
    augmented_input = payload.input_text
    if payload.edge_case_inputs:
        augmented_input += "\nEdge cases provided by user:\n- " + "\n- ".join(payload.edge_case_inputs)
    if payload.decision_notes:
        augmented_input += f"\nDecision notes from user: {payload.decision_notes}"

    execution_pack = await agent.run(augmented_input, payload.input_type)
    prd_tests = agent.run_prd_tests(execution_pack.structured_prd)
    action_required = not prd_tests.all_passed
    decision_options = [
        "Provide additional edge cases to strengthen coverage",
        "Accept known gaps and continue to implementation",
        "Request another PM refinement iteration",
    ]
    message_to_user = (
        "Some PRD-derived tests failed. Please share missing edge cases or a decision on trade-offs."
        if action_required
        else "PRD-derived tests passed. You can proceed or optionally refine further."
    )

    return UXFlowResponse(
        stage="idea_to_prd_to_tests",
        execution_pack=execution_pack,
        missed_edge_cases_prompt=execution_pack.structured_prd.clarification_questions,
        assumptions_made=execution_pack.structured_prd.assumptions,
        prd_tests=prd_tests,
        action_required=action_required,
        decision_options=decision_options,
        message_to_user=message_to_user,
    )

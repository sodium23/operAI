from __future__ import annotations

from fastapi import FastAPI

from app.agents.pm_agent import PMAgent
from app.core.config import settings
from app.models.schemas import GenerateResponse, PRDTestResponse, RefineRequest, RefineResponse, RefineIteration, UserInput

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

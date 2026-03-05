from typing import Any

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    input_text: str = Field(..., min_length=5)
    input_type: str = Field(default="text", description="text|slack_proposal|feature_brief")
    context: dict[str, Any] = Field(default_factory=dict)


class StructuredPRD(BaseModel):
    title: str
    goals: list[str]
    success_metrics: list[str]
    user_stories: list[str]
    acceptance_criteria: list[str]
    technical_requirements: list[str]
    non_functional_requirements: list[str]
    risk_register: list[str]
    assumptions: list[str]
    clarification_questions: list[str]


class EvaluationReport(BaseModel):
    completeness_score: float
    risk_confidence_score: float
    assumption_density: float
    hallucination_likelihood: float


class GovernanceLog(BaseModel):
    prompt: str
    model: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    pii_detected: bool


class FinanceEstimate(BaseModel):
    estimated_cost_usd: float
    token_usage: int


class ExecutionPack(BaseModel):
    parsed_intent: dict[str, Any]
    prompt_used: str
    structured_prd: StructuredPRD
    evaluation: EvaluationReport
    governance: GovernanceLog
    finance: FinanceEstimate
    next_steps: list[str]


class GenerateResponse(BaseModel):
    message: str
    execution_pack: ExecutionPack


class RefineRequest(UserInput):
    stability_threshold: float | None = None
    max_iterations: int | None = None


class RefineIteration(BaseModel):
    iteration: int
    confidence: float
    changes_summary: str


class RefineResponse(BaseModel):
    stable: bool
    achieved_confidence: float
    iterations: list[RefineIteration]
    final_execution_pack: ExecutionPack


class PRDTestResult(BaseModel):
    name: str
    passed: bool
    details: str


class PRDTestResponse(BaseModel):
    all_passed: bool
    failed_tests: list[str]
    results: list[PRDTestResult]
    guidance: str


class UXFlowRequest(UserInput):
    decision_notes: str = ""
    edge_case_inputs: list[str] = Field(default_factory=list)


class UXFlowResponse(BaseModel):
    stage: str
    execution_pack: ExecutionPack
    missed_edge_cases_prompt: list[str]
    assumptions_made: list[str]
    prd_tests: PRDTestResponse
    action_required: bool
    decision_options: list[str]
    message_to_user: str

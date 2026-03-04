from __future__ import annotations

from app.agents.evaluation_engine import EvaluationEngine
from app.agents.finance_agent import FinanceAgent
from app.agents.governance_logger import GovernanceLogger
from app.clients.claude_client import ClaudeClient
from app.models.schemas import ExecutionPack, PRDTestResponse, PRDTestResult, StructuredPRD
from app.services.intent_parser import IntentParser
from app.services.prompt_builder import PromptBuilder
from app.services.result_parser import ResultParser


class PMAgent:
    def __init__(self):
        self.intent_parser = IntentParser()
        self.prompt_builder = PromptBuilder()
        self.result_parser = ResultParser()
        self.eval_engine = EvaluationEngine()
        self.governance = GovernanceLogger()
        self.finance = FinanceAgent()
        self.llm = ClaudeClient()

    async def run(self, input_text: str, input_type: str) -> ExecutionPack:
        intent = self.intent_parser.parse(input_text, input_type)
        prompt = self.prompt_builder.build(intent, input_text)
        llm_result = await self.llm.generate_structured_content(prompt, intent)
        prd = self.result_parser.parse(llm_result)
        evaluation = self.eval_engine.score(prd)
        governance = self.governance.create_entry(prompt, self.llm.model, output_text=str(llm_result))
        finance = self.finance.estimate(governance)

        next_steps = [
            "Review generated user stories and acceptance criteria.",
            "Answer clarification questions for missing edge cases.",
            "Run PRD-derived tests and iterate if failures occur.",
        ]
        return ExecutionPack(
            parsed_intent=intent,
            prompt_used=prompt,
            structured_prd=prd,
            evaluation=evaluation,
            governance=governance,
            finance=finance,
            next_steps=next_steps,
        )

    def run_prd_tests(self, prd: StructuredPRD) -> PRDTestResponse:
        tests = [
            PRDTestResult(
                name="has_minimum_user_stories",
                passed=len(prd.user_stories) >= 3,
                details=f"Found {len(prd.user_stories)} user stories",
            ),
            PRDTestResult(
                name="has_acceptance_criteria",
                passed=len(prd.acceptance_criteria) >= 3,
                details=f"Found {len(prd.acceptance_criteria)} acceptance criteria",
            ),
            PRDTestResult(
                name="has_risk_register",
                passed=len(prd.risk_register) >= 2,
                details=f"Found {len(prd.risk_register)} risks",
            ),
            PRDTestResult(
                name="has_assumptions",
                passed=len(prd.assumptions) >= 2,
                details=f"Found {len(prd.assumptions)} assumptions",
            ),
            PRDTestResult(
                name="has_clarification_questions",
                passed=len(prd.clarification_questions) >= 2,
                details=f"Found {len(prd.clarification_questions)} clarification questions",
            ),
        ]
        failed = [t.name for t in tests if not t.passed]
        guidance = (
            "All generated PRD tests passed."
            if not failed
            else "Some PRD-derived tests failed. Please provide missing details or choose trade-offs for failed areas."
        )
        return PRDTestResponse(all_passed=not failed, failed_tests=failed, results=tests, guidance=guidance)

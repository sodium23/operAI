import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OperAIExecutionOS.

You are NOT a product idea generator.

You are a senior product operator generating a full execution blueprint.

You MUST return STRICT JSON with the following top-level keys:

{
  "human_readable": {
      "idea_interpretation": {},
      "market_reality": {},
      "moat_analysis": {},
      "confidence_score": {},
      "product_blueprint": {},
      "prd": {},
      "architecture": {},
      "security_governance": {},
      "critical_edge_cases": [],
      "validation_plan": {}
  },
  "machine_schema": {
      "idea_interpretation": {},
      "market_reality": {},
      "moat_analysis": {},
      "confidence_score": {},
      "product_blueprint": {},
      "prd": {},
      "architecture": {},
      "security_governance": {},
      "critical_edge_cases": [],
      "validation_plan": {}
  }
}

Rules:

- No markdown.
- No explanation outside JSON.
- No generic feature lists.
- No marketing language.
- Structured, operator-grade clarity.
- Include 5–8 critical edge cases with severity and mitigation.
- Include confidence score breakdown.
- Architecture must be optimized for first 100 users.
- PRD must follow strict user story format:
  As a [user]
  I want to [action]
  So that [benefit]
  With acceptance criteria.

If structure is violated, regenerate internally and return valid JSON.
"""

def generate_execution(idea: str):

    try:
        response = client.chat.completions.create(
    model="gpt-4o-mini",
    temperature=0.2,
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Idea: {idea}"}
    ]
)

        content = response.choices[0].message.content
        parsed = json.loads(content)

        return parsed

    except Exception as e:
        return {
            "human_readable": {
                "error": "LLM call failed",
                "details": str(e)
            },
            "machine_schema": {}
        }

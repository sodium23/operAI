import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OperAIExecutionOS.

Generate structured, concise, operator-grade execution blueprint.

Return STRICT JSON with:

{
  "human_readable": { ... },
  "machine_schema": { ... }
}

Include:
- Idea Interpretation
- Market Reality
- Moat Analysis
- Confidence Score
- Product Blueprint
- PRD (strict user story format)
- Architecture (first 100 users)
- Security & Governance
- 5-8 Critical Edge Cases (with severity + mitigation)
- Validation Plan

JSON only.
"""


def generate_execution(idea: str):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Idea: {idea}"}
        ]
    )

    raw = response.choices[0].message.content

    try:
        parsed = json.loads(raw)
        return parsed
    except:
        return {
            "human_readable": {"error": "Invalid LLM response"},
            "machine_schema": {}
        }

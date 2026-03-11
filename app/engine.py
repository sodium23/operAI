import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OperAIExecutionOS.

Return STRICT JSON with the following structure:

{
  "human_readable": {},
  "machine_schema": {}
}

No markdown.
No explanations.
JSON only.
"""

def generate_execution(idea: str):

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
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

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OperAIExecutionOS.

Return STRICT JSON with:
{
  "human_readable": {...},
  "machine_schema": {...}
}

No markdown.
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

    print("RAW LLM OUTPUT:", raw)

    try:
        parsed = json.loads(raw)
        return parsed
    except Exception as e:
        return {
            "human_readable": {
                "error": "LLM returned invalid JSON",
                "raw_output": raw
            },
            "machine_schema": {}
        }

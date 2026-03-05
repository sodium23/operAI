from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")


SYSTEM_PROMPT = """
You are a senior Product Manager and Product Designer.

You generate extremely detailed product execution packs including:
- PRD
- User stories
- Acceptance criteria
- Architecture overview
- Edge cases
- Assumptions
- Tests
- Wireframes
- React preview code

Follow strict product management discipline.

USER STORIES MUST FOLLOW THIS FORMAT:

As a [type of user]
I want to [perform an action]
So that [achieve a goal]

Each story must include acceptance criteria.

Do NOT prescribe implementation details inside the story itself.

Follow best practices for user-defined entities:
- unique names
- lowercase storage
- no special characters
- '-' and '_' allowed
- enforce case-insensitive uniqueness

When design or UI is required:
Provide React code AND a preview link suggestion.

Architecture must include:
- system components
- services
- data flow
- APIs
- storage
- scalability considerations
"""


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok", "service": "OperAI backend running"}


@app.post("/ux-flow")
async def ux_flow(payload: dict):

    idea = payload.get("input_text")

    prd = {
        "product_overview": f"Execution system generated for: {idea}",
        "target_users": [
            "product_managers",
            "engineering_leads",
            "startup_founders"
        ],
        "problem_statement": "Teams struggle to convert ideas into structured execution plans."
    }

    user_stories = [
        {
            "story": "As a product manager I want to input a product idea so that I can automatically generate a structured PRD",
            "acceptance_criteria": [
                "User can input free-form product ideas",
                "System generates a structured PRD",
                "PRD includes stories, assumptions and tests"
            ]
        },
        {
            "story": "As an engineering lead I want the system to identify edge cases so that I can reduce implementation risks",
            "acceptance_criteria": [
                "Edge cases are generated automatically",
                "Risks are highlighted",
                "Missing assumptions are surfaced"
            ]
        }
    ]

    architecture = {
        "components": [
            "frontend_ui",
            "pm_agent",
            "evaluation_engine",
            "governance_logger",
            "llm_client"
        ],
        "data_flow": [
            "user_input -> intent_parser",
            "intent -> prompt_builder",
            "prompt -> llm",
            "llm -> result_parser",
            "result -> evaluation_engine"
        ]
    }

    edge_cases = [
        "idea is too vague",
        "conflicting requirements",
        "missing user personas"
    ]

    assumptions = [
        "user wants structured product output",
        "system should detect missing requirements"
    ]

    tests = [
        "verify prd schema structure",
        "validate acceptance criteria present",
        "validate edge cases generated"
    ]

    wireframe = {
        "description": "Simple product idea input UI",
        "react_code": """
import React, { useState } from \"react\";

export default function OperAI() {
  const [idea,setIdea] = useState(\"\");

  return (
    <div style={{padding:40}}>
      <h1>OperAI</h1>
      <textarea
        placeholder=\"Describe your idea\"
        value={idea}
        onChange={(e)=>setIdea(e.target.value)}
      />
      <button>Generate Execution Pack</button>
    </div>
  );
}
"""
    }

    return {
        "idea": idea,
        "prd": prd,
        "user_stories": user_stories,
        "architecture": architecture,
        "assumptions": assumptions,
        "edge_cases": edge_cases,
        "tests": tests,
        "wireframe": wireframe,
        "action_required": False
    }

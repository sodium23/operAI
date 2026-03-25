from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from app.clarity import clarity_score, next_question
from app.engine import generate_execution
from app.schema import Blueprint

app = FastAPI()

# ---------------------------
# CORS
# ---------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://operai-frontend.vercel.app",
        "http://localhost:3000",
        "https://operai-frontend-niyatiagrawal2901-4478s-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Templates
# ---------------------------

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ---------------------------
# OPTIONS handler (CORS preflight)
# ---------------------------

@app.options("/{path:path}")
async def options_handler():
    return Response(status_code=200)


# ---------------------------
# MAIN OPERAI ENDPOINT
# ---------------------------

@app.post("/operai")
async def operai(payload: dict):

    try:

        idea = payload.get("idea") or payload.get("input_text")

        if not idea:
            return {"error": "idea field missing"}

        score = clarity_score(idea)

        if score < 0.5:
            question = next_question(idea)
            return {
                "mode": "insufficient_clarity",
                "clarity_score": score,
                "next_question": question
            }

        result = generate_execution(idea)
        raw = result.get("machine_schema", {})

        # ---------------------------
        # FIX PRD STORIES FORMAT
        # ---------------------------

        stories_raw = raw.get("prd", {}).get("user_stories", [])
        stories = []

        # ✅ FIXED INDENTATION (inside try)
        for i, story in enumerate(stories_raw):

            if isinstance(story, str):
                story = {"want": story}

            stories.append({
                "id": story.get("id", f"US{i+1}"),
                "title": story.get("title", f"User Story {i+1}"),
                "persona": story.get(
                    "persona",
                    raw.get("market_reality", {}).get("target_market", "User")
                ),
                "want": story.get("want") or story.get("user", ""),
                "so": story.get("so", "achieve their goal effectively"),
                "criteria": story.get("criteria") or [
                    f"User can successfully complete: {story.get('want', '')}"
                ]
            })

        # ✅ ALSO INSIDE try
        blueprint = Blueprint(

            idea_interpretation={
                "summary": raw.get("idea_interpretation", {}).get("description", ""),
                "coreValue": raw.get("moat_analysis", {}).get("unique_value_proposition", ""),
                "targetUser": raw.get("market_reality", {}).get("target_market", ""),
                "keyAssumptions": raw.get("idea_interpretation", {}).get("assumptions", [])
            },

            market_reality={
                "marketSize": raw.get("market_reality", {}).get("market_size", ""),
                "competitors": raw.get("market_reality", {}).get("competitors", []),
                "trends": raw.get("market_reality", {}).get("trends", []),
                "risks": raw.get("market_reality", {}).get("risks", [])
            },

            moat_analysis={
                "differentiators": raw.get("moat_analysis", {}).get("differentiators", []),
                "barriers": raw.get("moat_analysis", {}).get("barriers_to_entry", []),
                "sustainability": raw.get("moat_analysis", {}).get("sustainability", "")
            },

            confidence_score={
                "score": raw.get("confidence_score", {}).get("overall_confidence", 0),
                "factors": raw.get("confidence_score", {}).get("factors", [])
            },

            product_blueprint={
                "core_features": raw.get("product_blueprint", {}).get("core_features", [])
            },

            prd={
                "stories": stories
            },

            architecture={
                "components": raw.get("architecture", {}).get("components", []),
                "dataFlow": raw.get("architecture", {}).get("data_flow", []),
                "scaleTriggers": raw.get("architecture", {}).get("scale_triggers", [])
            },

            security={
                "considerations": raw.get("security", {}).get("considerations", []),
                "compliance": raw.get("security", {}).get("compliance", []),
                "governance": raw.get("security", {}).get("governance", [])
            },

            edge_cases=raw.get("edge_cases", []),

            validation={
                "experiments": raw.get("validation", {}).get("experiments", []),
                "successCriteria": raw.get("validation", {}).get("success_criteria", [])
            }
        )

        return {
            "mode": "execution_ready",
            "machine_schema": blueprint.dict()
        }

    except Exception as e:
        return {
            "mode": "error",
            "message": str(e)
        }

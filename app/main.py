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
# HELPERS
# ---------------------------

def ensure_list(value):
    if isinstance(value, list):
        return value
    if value:
        return [value]
    return []

def ensure_dict(value):
    return value if isinstance(value, dict) else {}


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

        # ---------------------------
        # NORMALIZATION
        # ---------------------------

        mr = ensure_dict(raw.get("market_reality"))
        ma = ensure_dict(raw.get("moat_analysis"))
        ii = ensure_dict(raw.get("idea_interpretation"))
        cs = ensure_dict(raw.get("confidence_score"))
        pb = ensure_dict(raw.get("product_blueprint"))
        arch = ensure_dict(raw.get("architecture"))
        sec = ensure_dict(raw.get("security"))
        val = ensure_dict(raw.get("validation"))

        # ---------------------------
        # BLUEPRINT
        # ---------------------------

        blueprint = Blueprint(

            idea_interpretation={
                "summary": ii.get("description", ""),
                "coreValue": ma.get("unique_value_proposition", ""),
                "targetUser": mr.get("target_market", ""),
                "keyAssumptions": ensure_list(ii.get("assumptions"))
            },

            market_reality={
                "marketSize": mr.get("market_size", ""),
                "competitors": [
                    c if isinstance(c, dict) else {"name": str(c), "strength": ""}
                    for c in ensure_list(mr.get("competitors"))
                    if c
                ],
                "trends": ensure_list(mr.get("trends")),
                "risks": [
                    r if isinstance(r, dict) else {"risk": str(r), "severity": ""}
                    for r in ensure_list(mr.get("risks"))
                ]
            },

            moat_analysis={
                "differentiators": ensure_list(ma.get("differentiators")),
                "barriers": ensure_list(ma.get("barriers_to_entry")),
                "sustainability": ma.get("sustainability", "")
            },

            confidence_score={
                "score": cs.get("overall_confidence", 0),
                "factors": [
                    f if isinstance(f, dict) else {"factor": str(f), "impact": ""}
                    for f in ensure_list(cs.get("factors"))
                ]
            },

            product_blueprint={
                "core_features": ensure_list(pb.get("core_features"))
            },

            prd={
                "stories": stories
            },

            architecture={
                "components": ensure_list(arch.get("components")),
                "dataFlow": ensure_list(arch.get("data_flow")),
                "scaleTriggers": ensure_list(arch.get("scale_triggers"))
            },

            security={
                "considerations": ensure_list(sec.get("considerations")),
                "compliance": ensure_list(sec.get("compliance")),
                "governance": ensure_list(sec.get("governance"))
            },

            edge_cases=ensure_list(raw.get("edge_cases")),

            validation={
                "experiments": [
                    e if isinstance(e, dict) else {"experiment": str(e), "metric": "", "timeline": ""}
                    for e in ensure_list(val.get("experiments"))
                ],
                "successCriteria": ensure_list(val.get("success_criteria"))
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

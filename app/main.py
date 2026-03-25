import json
import os
from urllib import error, request

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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
# Templates and static files
# ---------------------------

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "safercircle.html",
        {"request": request}
    )


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


def call_gemini_safety_chat(user_message: str):
    api_key = AIzaSyCIKfdiMLLj28bym_3egw3gFniLa8r-TTs

    if not api_key:
        return {
            "ok": False,
            "reply": "Set GEMINI_API_KEY first. No excuses.",
            "error": "GEMINI_API_KEY missing"
        }

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )

    system_tone = (
        "You are SaferCircle's advisor. Sound like a tough older sister: "
        "direct, strategic, and no sugarcoating. Give options and consequences. "
        "Keep replies actionable and concise."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_tone},
                    {"text": f"User message: {user_message}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.6,
            "maxOutputTokens": 250
        }
    }

    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with request.urlopen(req, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8"))

        candidates = data.get("candidates", [])
        if not candidates:
            return {
                "ok": False,
                "reply": "Gemini gave nothing back. Ask again, clearer.",
                "error": "No candidates in Gemini response"
            }

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "\n".join(part.get("text", "") for part in parts if part.get("text"))

        if not text:
            return {
                "ok": False,
                "reply": "Response came back empty. Tighten your prompt.",
                "error": "Gemini response text missing"
            }

        return {
            "ok": True,
            "reply": text
        }

    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        return {
            "ok": False,
            "reply": "Gemini call failed. Check your key and quota.",
            "error": f"HTTP {exc.code}: {body}"
        }
    except Exception as exc:
        return {
            "ok": False,
            "reply": "Network or config issue. Fix it and retry.",
            "error": str(exc)
        }


# ---------------------------
# SAFERCIRCLE ENDPOINT
# ---------------------------

@app.post("/safercircle/chat")
async def safercircle_chat(payload: dict):
    message = (payload.get("message") or "").strip()
    if not message:
        return {
            "ok": False,
            "reply": "Say what happened, clearly.",
            "error": "message missing"
        }

    return call_gemini_safety_chat(message)


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
        # FIX CONFIDENCE FACTORS (IMPORTANT FIX)
        # ---------------------------

        raw_factors = cs.get("factors", [])
        normalized_factors = []

        if isinstance(raw_factors, dict):
            for k, v in raw_factors.items():
                normalized_factors.append({
                    "factor": str(k),
                    "impact": v
                })

        elif isinstance(raw_factors, list):
            for f in raw_factors:
                if isinstance(f, dict):
                    normalized_factors.append({
                        "factor": f.get("factor", ""),
                        "impact": f.get("impact", 0)
                    })
                else:
                    normalized_factors.append({
                        "factor": str(f),
                        "impact": 0
                    })

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
                "factors": normalized_factors
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

    except Exception as exc:
        return {
            "mode": "error",
            "message": str(exc)
        }

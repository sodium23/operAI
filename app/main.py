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

        # accept both frontend formats
        idea = payload.get("idea") or payload.get("input_text")

    if not idea:
        return {"error": "idea field missing"}

    # ---------------------------
    # CLARITY CHECK
    # ---------------------------

    score = clarity_score(idea)

    if score < 0.5:
        question = next_question(idea)
        return {
            "mode": "insufficient_clarity",
            "clarity_score": score,
            "next_question": question
        }

    # ---------------------------
    # GENERATE EXECUTION PLAN
    # ---------------------------

    result = generate_execution(idea)

    raw = result.get("machine_schema", {})

    # ---------------------------
    # MAP AI OUTPUT → BLUEPRINT
    # ---------------------------

    blueprint = Blueprint(

        idea_interpretation={
            "summary": raw.get("idea_interpretation", {}).get("description", ""),
            "coreValue": raw.get("moat_analysis", {}).get(
                "unique_value_proposition", ""
            ),
            "targetUser": raw.get("market_reality", {}).get(
                "target_market", ""
            ),
            "keyAssumptions": [
                "Users trust automated compliance tools",
                "Government APIs remain stable",
                "Startups prefer SaaS automation"
            ]
        },

        market_reality={
            "marketSize": raw.get("market_reality", {}).get(
                "market_size", ""
            ),
            "competitors": [
                {"name": "ClearTax", "strength": "Compliance ecosystem"},
                {"name": "Quicko", "strength": "Automated tax workflows"}
            ],
            "trends": [
                "Compliance digitization",
                "Startup automation adoption",
                "Government API integrations"
            ],
            "risks": [
                {"risk": "Regulatory changes", "severity": "High"},
                {"risk": "Trust barriers", "severity": "Medium"}
            ]
        },

        moat_analysis={
            "differentiators": [
                raw.get("moat_analysis", {}).get(
                    "unique_value_proposition", ""
                )
            ],
            "barriers": [
                raw.get("moat_analysis", {}).get(
                    "barriers_to_entry", ""
                )
            ],
            "sustainability":
                "Strong if compliance accuracy and trust remain high"
        },

        confidence_score={
            "score": raw.get("confidence_score", {}).get(
                "overall_confidence", 70
            ),
            "factors": [
                {"factor": "Market demand", "impact": "positive"},
                {"factor": "Regulatory complexity", "impact": "negative"}
            ]
        },

        product_blueprint={
            "core_features": raw.get(
                "product_blueprint", {}
            ).get("core_features", [])
        },

        prd={
            "stories": raw.get("prd", {}).get("user_stories", [])
        },

        architecture={
            "components": [
                {
                    "name": "Frontend Dashboard",
                    "description": "User interface for founders"
                },
                {
                    "name": "Tax Engine",
                    "description": "Core tax calculation system"
                },
                {
                    "name": "Compliance API Connector",
                    "description": "Integration with GST APIs"
                },
                {
                    "name": "Secure Storage",
                    "description": "Encrypted financial storage"
                }
            ],
            "dataFlow": [
                "User uploads financial data",
                "System validates files",
                "Tax engine calculates liabilities",
                "User reviews filing"
            ],
            "scaleTriggers": [
                "10k startups onboarded",
                "Peak filing seasons"
            ]
        },

        security={
            "considerations": [
                "End-to-end encryption",
                "Secure financial storage"
            ],
            "compliance": [
                "Indian IT Act",
                "GST compliance guidelines"
            ],
            "governance": [
                "Audit logs",
                "Access monitoring"
            ]
        },

        edge_cases=[],

        validation={
            "experiments": [
                {
                    "experiment": "Pilot with 5 startups",
                    "metric": "Automated filing success rate",
                    "timeline": "4 weeks"
                }
            ],
            "successCriteria": [
                "80% automated filing success",
                "Founders complete filings without CA"
            ]
        }

    )

    # ---------------------------
    # RETURN FINAL SCHEMA
    # ---------------------------

    except Exception as e:
        return {
            "mode": "error",
            "message": str(e)
        }

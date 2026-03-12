from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import Blueprint

from app.clarity import clarity_score, next_question
from app.engine import generate_execution

app = FastAPI()

# CORS MUST be right after app creation
origins = [
    "https://operai-frontend.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # don't use * with credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/operai")
async def operai(payload: dict):

    # Accept both formats from frontend
    idea = payload.get("idea") or payload.get("input_text")

    if not idea:
        return {"error": "idea field missing"}

    # clarity check
    score = clarity_score(idea)

    if score < 0.5:
        question = next_question(idea)
        return {
            "mode": "insufficient_clarity",
            "clarity_score": score,
            "next_question": question
        }

    # generate execution blueprint
result = generate_execution(idea)

raw = result["machine_schema"]

blueprint = Blueprint(
    idea_interpretation={
        "summary": raw["idea_interpretation"].get("description", ""),
        "coreValue": raw["moat_analysis"].get("unique_value_proposition", ""),
        "targetUser": raw["market_reality"].get("target_market", ""),
        "keyAssumptions": [
            "Users trust automated compliance tools",
            "Government APIs remain stable",
            "Startups prefer automation over manual filing"
        ]
    },

    market_reality={
        "marketSize": raw["market_reality"].get("market_size", ""),
        "competitors": [
            {"name": "ClearTax", "strength": "Compliance ecosystem"},
            {"name": "Quicko", "strength": "Automation workflows"}
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
            raw["moat_analysis"].get("unique_value_proposition", "")
        ],
        "barriers": [
            raw["moat_analysis"].get("barriers_to_entry", "")
        ],
        "sustainability": "Strong if compliance accuracy and trust remain high"
    },

    confidence_score={
        "score": raw["confidence_score"].get("overall_confidence", 70),
        "factors": [
            {"factor": "Market demand", "impact": "positive"},
            {"factor": "Regulatory complexity", "impact": "negative"}
        ]
    },

    product_blueprint={
        "core_features": raw["product_blueprint"].get("core_features", [])
    },

    prd={
        "stories": raw["prd"].get("user_stories", [])
    },

    architecture={
        "components": [
            {"name": "Frontend Dashboard", "description": "User interface"},
            {"name": "Tax Engine", "description": "Tax calculation system"},
            {"name": "Compliance Connector", "description": "Government API integration"}
        ],
        "dataFlow": [
            "User uploads financial data",
            "System validates files",
            "Tax engine calculates liabilities",
            "User reviews filing"
        ],
        "scaleTriggers": [
            "10k startups",
            "Peak filing season"
        ]
    },

    security={
        "considerations": [
            "Encrypted financial storage",
            "Secure document access"
        ],
        "compliance": [
            "Indian IT Act",
            "GST compliance requirements"
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

return {
    "mode": "execution_ready",
    "machine_schema": blueprint.dict()
}

from fastapi import Response

@app.options("/{path:path}")
async def options_handler():
    return Response(status_code=200)

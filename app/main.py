from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok", "service": "OperAI backend running"}


@app.post("/ux-flow")
async def ux_flow(payload: dict):
    """
    Simplified prototype flow
    """

    idea = payload.get("input_text")

    response = {
        "idea": idea,
        "prd": {
            "title": "Execution Plan",
            "summary": f"Plan generated for: {idea}"
        },
        "assumptions": [
            "Users want automated PRD generation",
            "System needs structured output"
        ],
        "edge_cases": [
            "Idea too vague",
            "Multiple conflicting goals"
        ],
        "tests": [
            "PRD structure valid",
            "Edge cases detected"
        ],
        "action_required": False
    }

    return response

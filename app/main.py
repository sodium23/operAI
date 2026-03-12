from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

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

  idea = payload.get("idea") or payload.get("input_text")

    if not idea:
        return {
            "error": "idea field missing"
        }

    score = clarity_score(idea)

    if score < 0.5:
        question = next_question(idea)
        return {
            "mode": "insufficient_clarity",
            "clarity_score": score,
            "next_question": question
        }

    result = generate_execution(idea)

    return {
        "mode": "execution_ready",
        "machine_schema": result["machine_schema"]
    }


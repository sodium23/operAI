from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.clarity import clarity_score, next_question
from app.engine import generate_execution
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    idea = payload.get("input_text")
    question_count = payload.get("question_count", 0)

    score = clarity_score(idea)

    if score < 4:
        question = next_question(question_count)
        if question:
            return {
                "mode": "clarification",
                "question": question,
                "question_count": question_count + 1
            }
        return {"mode": "insufficient_clarity"}



result = generate_execution(idea)

return result["machine_schema"]

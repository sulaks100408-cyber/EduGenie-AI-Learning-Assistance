from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .gemini_service import (
    ask_question,
    explain_concept,
    generate_learning_path,
    generate_quiz,
    summarize_text,
)
from .models import (
    AskRequest,
    ExplainRequest,
    LearningPathRequest,
    QuizRequest,
    SummaryRequest,
)


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# --------------------------------------------------
# Settings
# --------------------------------------------------

settings = get_settings()


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="EduGenie API",
    description=(
        "Google Gemini powered learning assistant"
    ),
    version="1.0.0",
)


# --------------------------------------------------
# Static frontend
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=(
        settings.allowed_origins.strip() != "*"
    ),
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Homepage
# --------------------------------------------------

@app.get(
    "/",
    include_in_schema=False,
)
def home():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "application": settings.app_name,
        "gemini_configured": bool(
            settings.gemini_api_key.strip()
        ),
        "model": settings.gemini_model,
    }


# --------------------------------------------------
# Ask
# --------------------------------------------------

@app.post("/api/ask")
def ask(payload: AskRequest):

    try:

        answer = ask_question(
            payload.question,
            payload.level,
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI request failed: {exc}",
        ) from exc


# --------------------------------------------------
# Explain
# --------------------------------------------------

@app.post("/api/explain")
def explain(payload: ExplainRequest):

    try:

        answer = explain_concept(
            payload.topic,
            payload.level,
        )

        return {
            "answer": answer
        }

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"AI request failed: {exc}",
        ) from exc


# --------------------------------------------------
# Quiz
# --------------------------------------------------

@app.post("/api/quiz")
def quiz(payload: QuizRequest):

    try:

        result = generate_quiz(
            topic=payload.topic,
            level=payload.level,
            num_questions=payload.num_questions,
        )

        return result.model_dump()

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Quiz generation failed: {exc}",
        ) from exc


# --------------------------------------------------
# Learning Path
# --------------------------------------------------

@app.post("/api/learning-path")
def learning_path(
    payload: LearningPathRequest,
):

    try:

        result = generate_learning_path(
            goal=payload.goal,
            current_level=payload.current_level,
            weeks=payload.weeks,
        )

        return result.model_dump()

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                f"Learning path generation failed: "
                f"{exc}"
            ),
        ) from exc


# --------------------------------------------------
# Summarize
# --------------------------------------------------

@app.post("/api/summarize")
def summarize(payload: SummaryRequest):

    try:

        result = summarize_text(
            text=payload.text,
            level=payload.level,
        )

        return result.model_dump()

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Summarization failed: {exc}",
        ) from exc
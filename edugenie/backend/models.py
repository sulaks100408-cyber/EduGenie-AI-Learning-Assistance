from typing import Literal

from pydantic import BaseModel, Field


Level = Literal[
    "beginner",
    "intermediate",
    "advanced",
]


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=4000,
    )

    level: Level = "beginner"


class ExplainRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=2,
        max_length=1000,
    )

    level: Level = "beginner"


class QuizRequest(BaseModel):
    topic: str = Field(
        ...,
        min_length=2,
        max_length=1000,
    )

    num_questions: int = Field(
        default=5,
        ge=1,
        le=10,
    )

    level: Level = "beginner"


class SummaryRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=20,
        max_length=20000,
    )

    level: Level = "beginner"


class LearningPathRequest(BaseModel):
    goal: str = Field(
        ...,
        min_length=2,
        max_length=1000,
    )

    current_level: Level = "beginner"

    weeks: int = Field(
        default=4,
        ge=1,
        le=12,
    )


class QuizQuestion(BaseModel):
    question: str

    options: list[str] = Field(
        ...,
        min_length=4,
        max_length=4,
    )

    correct_answer: str

    explanation: str


class QuizResponse(BaseModel):
    title: str

    questions: list[QuizQuestion]


class LearningStep(BaseModel):
    week: int

    topic: str

    objective: str

    activities: list[str]

    milestone: str


class LearningPathResponse(BaseModel):
    title: str

    overview: str

    estimated_hours_per_week: int

    steps: list[LearningStep]

    tips: list[str]


class SummaryResponse(BaseModel):
    summary: str

    key_points: list[str]
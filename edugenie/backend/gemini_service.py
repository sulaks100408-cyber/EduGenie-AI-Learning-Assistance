from __future__ import annotations

from functools import lru_cache

from google import genai
from google.genai import types

from .config import get_settings
from .models import (
    LearningPathResponse,
    QuizResponse,
    SummaryResponse,
)


SYSTEM_INSTRUCTION = """
You are EduGenie, an AI-powered educational learning assistant.

Your job is to help students understand subjects clearly.

Always:
- Be accurate.
- Use clear educational language.
- Adapt explanations to the learner's level.
- Avoid unnecessary complexity.
- Give examples when useful.
- Do not invent sources or citations.
- If something is uncertain, say so.
"""


@lru_cache
def get_client():
    """
    Create the Gemini client only once.

    Returns None when no API key is configured.
    """

    settings = get_settings()

    if not settings.gemini_api_key.strip():
        return None

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_text(prompt: str) -> str:
    """
    Generate a normal text response using Gemini.
    """

    client = get_client()

    if client is None:
        return demo_response(prompt)

    settings = get_settings()

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=1500,
        ),
    )

    result = (response.text or "").strip()

    if not result:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return result


def generate_structured(
    prompt: str,
    schema_class,
):
    """
    Generate JSON structured according to a Pydantic schema.
    """

    client = get_client()

    if client is None:
        return None

    settings = get_settings()

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=3500,
            response_mime_type="application/json",
            response_schema=schema_class,
        ),
    )

    # The SDK exposes response.text.
    raw = (response.text or "").strip()

    if not raw:
        raise RuntimeError(
            "Gemini returned an empty structured response."
        )

    return schema_class.model_validate_json(raw)


def ask_question(
    question: str,
    level: str,
) -> str:

    prompt = f"""
{SYSTEM_INSTRUCTION}

A student has asked the following question.

Student level:
{level}

Question:
{question}

Answer using this structure:

Direct answer:
Give the answer immediately.

Explanation:
Explain why the answer is correct.

Example:
Give one simple example if appropriate.

Keep the answer concise and educational.
"""

    return generate_text(prompt)


def explain_concept(
    topic: str,
    level: str,
) -> str:

    prompt = f"""
{SYSTEM_INSTRUCTION}

Explain the following topic.

Topic:
{topic}

Student level:
{level}

Use this structure:

1. Simple definition
2. Easy explanation
3. Example or analogy
4. Important points
5. Common mistakes

Make the explanation easy for a student to understand.
"""

    return generate_text(prompt)


def generate_quiz(
    topic: str,
    level: str,
    num_questions: int,
) -> QuizResponse:

    prompt = f"""
{SYSTEM_INSTRUCTION}

Create a multiple-choice quiz.

Topic:
{topic}

Student level:
{level}

Number of questions:
{num_questions}

Requirements:

- Create exactly {num_questions} questions.
- Every question must have exactly 4 options.
- Only one option must be correct.
- correct_answer must exactly match one option.
- Provide a short explanation for the answer.
- Questions should test understanding, not only memorization.
"""

    result = generate_structured(
        prompt,
        QuizResponse,
    )

    if result is not None:
        return result

    return create_demo_quiz(
        topic,
        num_questions,
    )


def create_demo_quiz(
    topic: str,
    num_questions: int,
) -> QuizResponse:

    questions = []

    for number in range(1, num_questions + 1):

        questions.append(
            {
                "question": (
                    f"Which statement best describes "
                    f"{topic}?"
                ),
                "options": [
                    f"The main idea of {topic}",
                    "An unrelated concept",
                    "The opposite of the topic",
                    "None of these",
                ],
                "correct_answer": f"The main idea of {topic}",
                "explanation": (
                    f"This demo question represents "
                    f"the core idea of {topic}."
                ),
            }
        )

    return QuizResponse(
        title=f"{topic} Quiz",
        questions=questions,
    )


def generate_learning_path(
    goal: str,
    current_level: str,
    weeks: int,
) -> LearningPathResponse:

    prompt = f"""
{SYSTEM_INSTRUCTION}

Create a personalized learning plan.

Learning goal:
{goal}

Current learner level:
{current_level}

Duration:
{weeks} weeks

Create exactly {weeks} weekly learning steps.

Every step must contain:

- week
- topic
- objective
- activities
- milestone

Also provide:

- title
- overview
- estimated_hours_per_week
- 3 to 5 useful study tips

The plan should progress from foundational concepts
toward practical application.
"""

    result = generate_structured(
        prompt,
        LearningPathResponse,
    )

    if result is not None:
        return result

    return create_demo_learning_path(
        goal,
        current_level,
        weeks,
    )


def create_demo_learning_path(
    goal: str,
    current_level: str,
    weeks: int,
) -> LearningPathResponse:

    steps = []

    for week in range(1, weeks + 1):

        steps.append(
            {
                "week": week,
                "topic": f"{goal} - Stage {week}",
                "objective": (
                    f"Build the next level of understanding "
                    f"in {goal}."
                ),
                "activities": [
                    "Read a lesson",
                    "Write a short summary",
                    "Practice questions",
                    "Review mistakes",
                ],
                "milestone": (
                    "Explain the week's main concepts "
                    "without using notes."
                ),
            }
        )

    return LearningPathResponse(
        title=f"{goal} Learning Path",
        overview=(
            f"A {weeks}-week starter plan for a "
            f"{current_level} learner."
        ),
        estimated_hours_per_week=4,
        steps=steps,
        tips=[
            "Study consistently in short sessions.",
            "Use active recall.",
            "Practice instead of only reading.",
            "Review mistakes.",
            "Test yourself every week.",
        ],
    )


def summarize_text(
    text: str,
    level: str,
) -> SummaryResponse:

    prompt = f"""
{SYSTEM_INSTRUCTION}

Summarize this educational passage.

Student level:
{level}

Educational passage:
{text}

Return:

- A concise summary.
- 3 to 7 important key points.

Focus on the information that is most useful
for learning and revision.
"""

    result = generate_structured(
        prompt,
        SummaryResponse,
    )

    if result is not None:
        return result

    return create_demo_summary(text)


def create_demo_summary(
    text: str,
) -> SummaryResponse:

    cleaned = " ".join(text.split())

    sentences = [
        sentence.strip()
        for sentence in cleaned.replace(
            "!",
            ".",
        ).replace(
            "?",
            ".",
        ).split(".")
        if sentence.strip()
    ]

    summary = ". ".join(
        sentences[:3]
    )

    if summary:
        summary += "."

    key_points = [
        sentence[:300]
        for sentence in sentences[:6]
    ]

    return SummaryResponse(
        summary=summary[:1200],
        key_points=key_points,
    )


def demo_response(prompt: str) -> str:

    lower_prompt = prompt.lower()

    if "largest ocean" in lower_prompt:

        return (
            "Direct answer:\n"
            "The Pacific Ocean is the largest ocean "
            "on Earth.\n\n"
            "Explanation:\n"
            "It covers more area than any other ocean "
            "and stretches between Asia, Australia, "
            "North America and South America.\n\n"
            "Example:\n"
            "The Pacific is larger than the Atlantic "
            "Ocean."
        )

    if "pythagorean" in lower_prompt:

        return (
            "The Pythagorean theorem states that in a "
            "right-angled triangle, a² + b² = c², "
            "where c is the hypotenuse."
        )

    return (
        "EduGenie is currently running in Demo Mode.\n\n"
        "To enable live Gemini AI responses, add your "
        "GEMINI_API_KEY to the .env file."
    )
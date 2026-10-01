from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "EduGenie" in response.text


def test_ask():

    response = client.post(
        "/api/ask",
        json={
            "question": (
                "Which is the largest ocean?"
            ),
            "level": "beginner",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data


def test_quiz():

    response = client.post(
        "/api/quiz",
        json={
            "topic": "Pythagorean theorem",
            "num_questions": 3,
            "level": "beginner",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "questions" in data

    assert len(
        data["questions"]
    ) == 3


def test_learning_path():

    response = client.post(
        "/api/learning-path",
        json={
            "goal": "Learn Python",
            "current_level": "beginner",
            "weeks": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "steps" in data

    assert len(
        data["steps"]
    ) == 3


def test_summary():

    response = client.post(
        "/api/summarize",
        json={
            "text": (
                "Photosynthesis is the process "
                "by which green plants use light "
                "energy to make chemical energy. "
                "Plants use carbon dioxide and "
                "water to produce glucose and oxygen."
            ),
            "level": "beginner",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data

    assert "key_points" in data
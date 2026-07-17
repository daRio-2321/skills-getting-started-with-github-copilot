import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Basketball Team" in payload
    assert payload["Basketball Team"]["participants"] == ["John Doe"]


def test_signup_for_activity(client):
    response = client.post(
        "/activities/Art Studio/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up student@example.com for Art Studio"
    assert "student@example.com" in activities["Art Studio"]["participants"]


def test_signup_rejects_duplicate_email(client):
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "John Doe"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity(client):
    client.post(
        "/activities/Art Studio/signup",
        params={"email": "student@example.com"},
    )

    response = client.delete(
        "/activities/Art Studio/unregister",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered student@example.com from Art Studio"
    assert "student@example.com" not in activities["Art Studio"]["participants"]


def test_unknown_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

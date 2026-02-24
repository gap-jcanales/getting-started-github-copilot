from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


BASE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.fixture
def reset_activities(monkeypatch):
    seeded_activities = deepcopy(BASE_ACTIVITIES)
    monkeypatch.setattr(app_module, "activities", seeded_activities)
    return seeded_activities


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 302)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seeded_data(client, reset_activities):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_success(client, reset_activities):
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_for_missing_activity_returns_404(client, reset_activities):
    # Arrange

    # Act
    response = client.post("/activities/Robotics Club/signup?email=student@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_409(client, reset_activities):
    # Arrange
    existing_email = app_module.activities["Chess Club"]["participants"][0]

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={existing_email}")

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_success(client, reset_activities):
    # Arrange
    email = app_module.activities["Chess Club"]["participants"][0]

    # Act
    response = client.delete(f"/activities/Chess Club/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_unregister_missing_activity_returns_404(client, reset_activities):
    # Arrange

    # Act
    response = client.delete("/activities/Robotics Club/participants?email=student@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_participant_returns_404(client, reset_activities):
    # Arrange

    # Act
    response = client.delete("/activities/Chess Club/participants?email=not.registered@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"

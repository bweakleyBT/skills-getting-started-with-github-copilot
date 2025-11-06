import uuid

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    # use a unique email so tests are idempotent across runs
    email = f"test-{uuid.uuid4().hex}@example.com"

    # ensure activity exists and email is not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert activity in activities
    assert email not in activities[activity]["participants"]

    # sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up" in data.get("message", "")

    # verify participant added
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert email in activities[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Unregistered" in data.get("message", "")

    # verify removal
    resp = client.get("/activities")
    activities = resp.json()
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    activity = "Chess Club"
    email = f"no-such-{uuid.uuid4().hex}@example.com"

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
    data = resp.json()
    assert data.get("detail") in ("Participant not found in this activity", None)

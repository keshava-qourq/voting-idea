"""Posting an idea: saved with zero votes, validated, and refused without login (US-008)."""

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Idea, Vote


def _idea_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count(Idea.id))) or 0


def test_ac021_saves_the_idea_with_zero_votes_and_shows_it_on_the_board(
    auth_client: TestClient, db_session: Session
) -> None:
    response = auth_client.post(
        "/ideas", json={"title": "Solar bench", "description": "A bench with a charger"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Solar bench"
    assert body["description"] == "A bench with a charger"
    assert body["voteCount"] == 0
    assert body["voted"] is False
    assert db_session.get(Idea, body["id"]) is not None
    assert db_session.scalar(select(func.count(Vote.id))) == 0

    board = auth_client.get("/ideas").json()
    assert [item["id"] for item in board] == [body["id"]]
    assert board[0]["voteCount"] == 0


def test_ac021_the_author_is_the_signed_in_user_not_the_request_body(
    auth_client: TestClient, db_session: Session
) -> None:
    me = auth_client.get("/auth/me").json()

    response = auth_client.post(
        "/ideas",
        json={"title": "Mine", "description": "Text", "userId": "someone-else"},
    )

    assert response.status_code == 201
    idea = db_session.get(Idea, response.json()["id"])
    assert idea is not None
    assert idea.user_id == me["id"]


def test_ac022_rejects_an_empty_title_and_saves_nothing(
    auth_client: TestClient, db_session: Session
) -> None:
    response = auth_client.post("/ideas", json={"title": "", "description": "Text"})

    assert response.status_code == 422
    assert response.json()["code"] == "TITLE_REQUIRED"
    assert response.json()["field"] == "title"
    assert _idea_count(db_session) == 0


def test_ac022_rejects_an_empty_description_and_saves_nothing(
    auth_client: TestClient, db_session: Session
) -> None:
    response = auth_client.post("/ideas", json={"title": "Title", "description": ""})

    assert response.status_code == 422
    assert response.json()["code"] == "DESCRIPTION_REQUIRED"
    assert response.json()["field"] == "description"
    assert _idea_count(db_session) == 0


def test_ac022_rejects_blank_or_missing_fields(
    auth_client: TestClient, db_session: Session
) -> None:
    blank = auth_client.post("/ideas", json={"title": "   ", "description": "Text"})
    missing = auth_client.post("/ideas", json={"title": "Title"})

    assert blank.status_code == 422
    assert blank.json()["field"] == "title"
    assert missing.status_code == 422
    assert missing.json()["field"] == "description"
    assert _idea_count(db_session) == 0


def test_ac023_rejects_a_title_over_the_limit_and_saves_nothing(
    auth_client: TestClient, db_session: Session
) -> None:
    response = auth_client.post("/ideas", json={"title": "x" * 121, "description": "Text"})

    assert response.status_code == 422
    assert response.json()["code"] == "TITLE_TOO_LONG"
    assert response.json()["field"] == "title"
    assert "120" in response.json()["message"]
    assert _idea_count(db_session) == 0


def test_ac023_rejects_a_description_over_the_limit_and_saves_nothing(
    auth_client: TestClient, db_session: Session
) -> None:
    response = auth_client.post("/ideas", json={"title": "Title", "description": "x" * 501})

    assert response.status_code == 422
    assert response.json()["code"] == "DESCRIPTION_TOO_LONG"
    assert response.json()["field"] == "description"
    assert "500" in response.json()["message"]
    assert _idea_count(db_session) == 0


def test_ac023_accepts_a_title_and_description_exactly_at_the_limit(
    auth_client: TestClient, db_session: Session
) -> None:
    response = auth_client.post("/ideas", json={"title": "t" * 120, "description": "d" * 500})

    assert response.status_code == 201
    assert _idea_count(db_session) == 1


def test_nfr004_posting_is_refused_without_login_and_saves_nothing(
    client: TestClient, db_session: Session
) -> None:
    response = client.post("/ideas", json={"title": "Title", "description": "Text"})

    assert response.status_code == 401
    assert _idea_count(db_session) == 0


def test_nfr004_posting_is_refused_with_an_unknown_token(
    client: TestClient, db_session: Session
) -> None:
    response = client.post(
        "/ideas",
        json={"title": "Title", "description": "Text"},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
    assert _idea_count(db_session) == 0


def test_ac025_a_visitor_who_posts_is_told_to_log_in_and_no_idea_is_created(
    client: TestClient, db_session: Session
) -> None:
    response = client.post("/ideas", json={"title": "Title", "description": "Text"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert _idea_count(db_session) == 0
    assert client.get("/ideas").json() == []


def test_ac025_a_visitor_with_an_invalid_post_is_asked_to_log_in_first(
    client: TestClient, db_session: Session
) -> None:
    response = client.post("/ideas", json={"title": "", "description": ""})

    assert response.status_code == 401
    assert _idea_count(db_session) == 0


def test_ac025_the_profile_check_reports_a_visitor_as_not_logged_in(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_ac025_the_profile_check_reports_a_logged_in_user(auth_client: TestClient) -> None:
    response = auth_client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["email"]


def test_ac024_no_edit_or_delete_endpoint_is_offered(auth_client: TestClient) -> None:
    created = auth_client.post("/ideas", json={"title": "Title", "description": "Text"}).json()

    for method in ("put", "patch", "delete"):
        response = getattr(auth_client, method)(f"/ideas/{created['id']}")
        assert response.status_code in (404, 405)

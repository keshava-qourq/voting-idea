"""Upvoting an idea (US-010), one test per criterion."""

import secrets
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import USER_ROLE, ensure_user, find_user
from app.main import app
from app.models import Idea, Vote

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _foreign_idea(db_session: Session, title: str = "idea") -> Idea:
    email = f"author-{uuid4().hex[:12]}@example.com"
    ensure_user(db_session, email=email, password=secrets.token_urlsafe(), role=USER_ROLE)
    author = find_user(db_session, email)
    assert author is not None
    idea = Idea(
        id=str(uuid4()),
        user_id=author.id,
        title=title,
        description=f"About {title}",
        created_at=NOW,
    )
    db_session.add(idea)
    db_session.commit()
    return idea


def _votes_in_store(db_session: Session, idea_id: str) -> int:
    count = select(func.count(Vote.id)).where(Vote.idea_id == idea_id)
    return db_session.scalar(count) or 0


def test_ac027_a_first_vote_adds_exactly_one(auth_client: TestClient, db_session: Session) -> None:
    idea = _foreign_idea(db_session)

    response = auth_client.post(f"/ideas/{idea.id}/vote")

    assert response.status_code == 200
    assert response.json() == {"ideaId": idea.id, "voteCount": 1, "voted": True}
    assert _votes_in_store(db_session, idea.id) == 1


def test_ac027_the_board_order_follows_the_new_vote(
    client: TestClient, auth_client: TestClient, db_session: Session
) -> None:
    older = _foreign_idea(db_session, "older")
    newer = _foreign_idea(db_session, "newer")
    newer.created_at = datetime(2026, 1, 2, tzinfo=UTC)
    db_session.commit()
    assert [i["title"] for i in client.get("/ideas").json()] == ["newer", "older"]

    auth_client.post(f"/ideas/{older.id}/vote")

    board = auth_client.get("/ideas").json()
    assert [(i["title"], i["voteCount"], i["voted"]) for i in board] == [
        ("older", 1, True),
        ("newer", 0, False),
    ]


def test_ac027_a_repeat_vote_changes_nothing(auth_client: TestClient, db_session: Session) -> None:
    idea = _foreign_idea(db_session)
    auth_client.post(f"/ideas/{idea.id}/vote")

    again = auth_client.post(f"/ideas/{idea.id}/vote")

    assert again.status_code == 200
    assert again.json()["voteCount"] == 1
    assert _votes_in_store(db_session, idea.id) == 1


def test_ac027_different_users_each_add_one(auth_client: TestClient, db_session: Session) -> None:
    idea = _foreign_idea(db_session)
    other = Vote(
        id=str(uuid4()),
        user_id=idea.user_id,
        idea_id=idea.id,
        created_at=NOW,
    )
    db_session.add(other)
    db_session.commit()

    response = auth_client.post(f"/ideas/{idea.id}/vote")

    assert response.json()["voteCount"] == 2


def test_ac027_an_unknown_idea_is_a_404(auth_client: TestClient) -> None:
    response = auth_client.post(f"/ideas/{uuid4()}/vote")

    assert response.status_code == 404
    assert response.json()["code"] == "IDEA_NOT_FOUND"


def test_ac028_the_author_can_vote_on_their_own_idea(auth_client: TestClient) -> None:
    posted = auth_client.post("/ideas", json={"title": "Mine", "description": "My own idea"})
    assert posted.status_code == 201
    idea_id = posted.json()["id"]

    response = auth_client.post(f"/ideas/{idea_id}/vote")

    assert response.status_code == 200
    assert response.json() == {"ideaId": idea_id, "voteCount": 1, "voted": True}


def test_ac029_no_remove_or_downvote_endpoint_is_offered() -> None:
    vote_paths = {path: set(ops) for path, ops in app.openapi()["paths"].items() if "vote" in path}

    assert vote_paths == {"/ideas/{idea_id}/vote": {"post"}}


def test_ac029_a_vote_cannot_be_removed_by_other_methods(
    auth_client: TestClient, db_session: Session
) -> None:
    idea = _foreign_idea(db_session)
    auth_client.post(f"/ideas/{idea.id}/vote")

    for method in ("delete", "put", "patch"):
        response = getattr(auth_client, method)(f"/ideas/{idea.id}/vote")
        assert response.status_code == 405

    assert _votes_in_store(db_session, idea.id) == 1


def test_nfr004_a_vote_is_refused_without_login_and_records_nothing(
    client: TestClient, db_session: Session
) -> None:
    idea = _foreign_idea(db_session)

    response = client.post(f"/ideas/{idea.id}/vote")
    bad_token = client.post(
        f"/ideas/{idea.id}/vote", headers={"Authorization": "Bearer not-a-token"}
    )

    assert response.status_code == 401
    assert bad_token.status_code == 401
    assert _votes_in_store(db_session, idea.id) == 0

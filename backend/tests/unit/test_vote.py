"""Upvoting an idea (US-010), one test per criterion."""

import secrets
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
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


def _first_call_finds_nothing(real: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap `session.scalar` so the first query on votes (the "already voted?" check) is empty."""
    calls = {"n": 0}

    def scalar(statement: Any, *args: Any, **kwargs: Any) -> Any:
        if "FROM votes" in str(statement):
            calls["n"] += 1
            if calls["n"] == 1:
                return None
        return real(statement, *args, **kwargs)

    return scalar


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


def test_ac031_a_double_click_stores_one_vote_and_keeps_the_count(
    auth_client: TestClient, db_session: Session
) -> None:
    idea = _foreign_idea(db_session)

    responses = [auth_client.post(f"/ideas/{idea.id}/vote") for _ in range(3)]

    assert [r.status_code for r in responses] == [200, 200, 200]
    assert [r.json()["voteCount"] for r in responses] == [1, 1, 1]
    assert _votes_in_store(db_session, idea.id) == 1
    board = auth_client.get("/ideas").json()
    assert [(i["id"], i["voteCount"]) for i in board] == [(idea.id, 1)]


def test_ac031_the_data_refuses_a_duplicate_vote_when_two_requests_race(
    auth_client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    idea = _foreign_idea(db_session)
    assert auth_client.post(f"/ideas/{idea.id}/vote").status_code == 200
    # Both requests passed the "already voted?" check before either stored its vote.
    monkeypatch.setattr(db_session, "scalar", _first_call_finds_nothing(db_session.scalar))

    response = auth_client.post(f"/ideas/{idea.id}/vote")

    assert response.status_code == 200
    assert response.json() == {"ideaId": idea.id, "voteCount": 1, "voted": True}
    assert _votes_in_store(db_session, idea.id) == 1


def test_ac032_a_vote_on_a_different_idea_is_accepted(
    auth_client: TestClient, db_session: Session
) -> None:
    first = _foreign_idea(db_session, "first")
    second = _foreign_idea(db_session, "second")
    assert auth_client.post(f"/ideas/{first.id}/vote").status_code == 200

    response = auth_client.post(f"/ideas/{second.id}/vote")

    assert response.status_code == 200
    assert response.json() == {"ideaId": second.id, "voteCount": 1, "voted": True}
    assert _votes_in_store(db_session, first.id) == 1
    assert _votes_in_store(db_session, second.id) == 1


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


def test_ac033_a_visitor_vote_is_refused_and_the_count_is_unchanged(
    client: TestClient, auth_client: TestClient, db_session: Session
) -> None:
    idea = _foreign_idea(db_session)
    assert auth_client.post(f"/ideas/{idea.id}/vote").status_code == 200

    response = client.post(f"/ideas/{idea.id}/vote")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert _votes_in_store(db_session, idea.id) == 1
    board = client.get("/ideas").json()
    assert [(i["id"], i["voteCount"]) for i in board] == [(idea.id, 1)]


def test_ac033_a_visitor_is_asked_to_log_in_before_the_idea_is_looked_up(
    client: TestClient,
) -> None:
    response = client.post(f"/ideas/{uuid4()}/vote")

    assert response.status_code == 401


def test_ac033_a_visitor_vote_is_refused_with_an_expired_or_forged_token(
    client: TestClient, db_session: Session
) -> None:
    idea = _foreign_idea(db_session)
    forged = secrets.token_urlsafe()

    response = client.post(f"/ideas/{idea.id}/vote", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401
    assert _votes_in_store(db_session, idea.id) == 0


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

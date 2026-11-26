"""Ideas with equal votes are listed newest first (US-006), one test per criterion."""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import USER_ROLE, ensure_user, find_user
from app.models import Idea, User, Vote

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _user(db_session: Session) -> User:
    email = f"tie-{uuid4().hex[:12]}@example.com"
    ensure_user(db_session, email=email, password=secrets.token_urlsafe(), role=USER_ROLE)
    user = find_user(db_session, email)
    assert user is not None
    return user


def _idea(db_session: Session, author: User, title: str, age_minutes: int) -> Idea:
    idea = Idea(
        id=str(uuid4()),
        user_id=author.id,
        title=title,
        description=f"About {title}",
        created_at=NOW - timedelta(minutes=age_minutes),
    )
    db_session.add(idea)
    db_session.commit()
    return idea


def _vote(db_session: Session, idea: Idea, count: int) -> None:
    for _ in range(count):
        voter = _user(db_session)
        db_session.add(Vote(id=str(uuid4()), user_id=voter.id, idea_id=idea.id, created_at=NOW))
    db_session.commit()


def _titles(client: TestClient) -> list[str]:
    response = client.get("/ideas")
    assert response.status_code == 200
    return [idea["title"] for idea in response.json()]


def test_ac017_tied_ideas_are_ordered_newest_first(client: TestClient, db_session: Session) -> None:
    author = _user(db_session)
    oldest = _idea(db_session, author, "oldest", age_minutes=60)
    newest = _idea(db_session, author, "newest", age_minutes=1)
    middle = _idea(db_session, author, "middle", age_minutes=30)
    for idea in (oldest, newest, middle):
        _vote(db_session, idea, 2)

    assert _titles(client) == ["newest", "middle", "oldest"]


def test_ac017_ideas_with_no_votes_are_ordered_newest_first(
    client: TestClient, db_session: Session
) -> None:
    author = _user(db_session)
    _idea(db_session, author, "old", age_minutes=20)
    _idea(db_session, author, "new", age_minutes=2)

    assert _titles(client) == ["new", "old"]


def test_ac017_votes_rank_before_posting_time(client: TestClient, db_session: Session) -> None:
    author = _user(db_session)
    old_popular = _idea(db_session, author, "old popular", age_minutes=50)
    _idea(db_session, author, "new unvoted", age_minutes=1)
    new_tied_a = _idea(db_session, author, "tied a", age_minutes=5)
    new_tied_b = _idea(db_session, author, "tied b", age_minutes=10)
    _vote(db_session, old_popular, 2)
    _vote(db_session, new_tied_a, 1)
    _vote(db_session, new_tied_b, 1)

    assert _titles(client) == ["old popular", "tied a", "tied b", "new unvoted"]


def test_ac018_a_newer_idea_that_gains_a_vote_is_listed_above_the_older_one(
    client: TestClient, auth_client: TestClient, db_session: Session
) -> None:
    author = _user(db_session)
    older = _idea(db_session, author, "older", age_minutes=30)
    newer = _idea(db_session, author, "newer", age_minutes=5)
    _vote(db_session, older, 1)
    _vote(db_session, newer, 0)
    assert _titles(client) == ["older", "newer"]  # older leads with more votes

    assert auth_client.post(f"/ideas/{newer.id}/vote").status_code == 200

    body = client.get("/ideas").json()
    assert [(i["title"], i["voteCount"]) for i in body] == [("newer", 1), ("older", 1)]

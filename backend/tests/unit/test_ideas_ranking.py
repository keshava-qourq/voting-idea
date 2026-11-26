"""The public board ranked by votes (US-005), one test per criterion."""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import USER_ROLE, ensure_user, find_user
from app.models import Idea, User, Vote

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _user(db_session: Session) -> User:
    email = f"board-{uuid4().hex[:12]}@example.com"
    ensure_user(db_session, email=email, password=secrets.token_urlsafe(), role=USER_ROLE)
    user = find_user(db_session, email)
    assert user is not None
    return user


def _idea(db_session: Session, author: User, title: str, age_minutes: int = 0) -> Idea:
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


def _titles(client: TestClient, **kwargs: object) -> list[str]:
    response = client.get("/ideas", **kwargs)  # type: ignore[arg-type]
    assert response.status_code == 200
    return [idea["title"] for idea in response.json()]


def test_ac014_lists_ideas_by_descending_vote_count_without_login(
    client: TestClient, db_session: Session
) -> None:
    author = _user(db_session)
    low = _idea(db_session, author, "low")
    high = _idea(db_session, author, "high")
    mid = _idea(db_session, author, "mid")
    none = _idea(db_session, author, "none")
    _vote(db_session, low, 1)
    _vote(db_session, high, 3)
    _vote(db_session, mid, 2)

    response = client.get("/ideas")

    assert response.status_code == 200
    body = response.json()
    assert [(i["title"], i["voteCount"]) for i in body] == [
        ("high", 3),
        ("mid", 2),
        ("low", 1),
        ("none", 0),
    ]
    assert none.id == body[-1]["id"]
    assert all(i["voted"] is False for i in body)


def test_ac014_ties_are_listed_newest_first(client: TestClient, db_session: Session) -> None:
    author = _user(db_session)
    old = _idea(db_session, author, "old", age_minutes=30)
    new = _idea(db_session, author, "new", age_minutes=1)
    middle = _idea(db_session, author, "middle", age_minutes=10)
    for idea in (old, new, middle):
        _vote(db_session, idea, 1)

    assert _titles(client) == ["new", "middle", "old"]


def test_ac014_never_includes_author_emails(client: TestClient, db_session: Session) -> None:
    author = _user(db_session)
    _idea(db_session, author, "private")

    response = client.get("/ideas")

    assert author.email not in response.text
    assert set(response.json()[0]) == {
        "id",
        "title",
        "description",
        "voteCount",
        "createdAt",
        "voted",
    }


def test_ac014_marks_the_ideas_the_signed_in_user_voted_on(
    client: TestClient, auth_client: TestClient, db_session: Session
) -> None:
    author = _user(db_session)
    mine = _idea(db_session, author, "mine")
    other = _idea(db_session, author, "other")
    voted = auth_client.post(f"/ideas/{mine.id}/vote")
    assert voted.status_code == 200
    _vote(db_session, other, 0)

    flags = {i["title"]: i["voted"] for i in auth_client.get("/ideas").json()}
    anonymous = {i["title"]: i["voted"] for i in client.get("/ideas").json()}
    bad_token = client.get("/ideas", headers={"Authorization": "Bearer not-a-token"})

    assert flags == {"mine": True, "other": False}
    assert anonymous == {"mine": False, "other": False}
    assert bad_token.status_code == 200
    assert all(i["voted"] is False for i in bad_token.json())


def test_ac015_a_new_vote_moves_the_idea_to_its_new_position(
    client: TestClient, auth_client: TestClient, db_session: Session
) -> None:
    author = _user(db_session)
    first = _idea(db_session, author, "first", age_minutes=20)
    second = _idea(db_session, author, "second", age_minutes=10)
    _vote(db_session, first, 1)
    assert _titles(client) == ["first", "second"]

    _vote(db_session, second, 1)
    assert _titles(client) == ["second", "first"]  # a tie: newest first

    assert auth_client.post(f"/ideas/{first.id}/vote").status_code == 200
    body = client.get("/ideas").json()
    assert [(i["title"], i["voteCount"]) for i in body] == [("first", 2), ("second", 1)]


def test_ac016_no_ideas_gives_an_empty_list(client: TestClient) -> None:
    response = client.get("/ideas")

    assert response.status_code == 200
    assert response.json() == []

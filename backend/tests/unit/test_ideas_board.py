"""Each idea on the board shows its title, description and vote count (US-007)."""

import secrets
from datetime import UTC, datetime
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


def _idea(db_session: Session, author: User, title: str, description: str) -> Idea:
    idea = Idea(
        id=str(uuid4()),
        user_id=author.id,
        title=title,
        description=description,
        created_at=NOW,
    )
    db_session.add(idea)
    db_session.commit()
    return idea


def test_ac019_each_idea_shows_its_title_description_and_vote_count(
    client: TestClient, db_session: Session
) -> None:
    author = _user(db_session)
    idea = _idea(db_session, author, "Solar bench", "A bench with a phone charger")
    for _ in range(2):
        voter = _user(db_session)
        db_session.add(Vote(id=str(uuid4()), user_id=voter.id, idea_id=idea.id, created_at=NOW))
    db_session.commit()

    response = client.get("/ideas")

    assert response.status_code == 200
    [item] = response.json()
    assert item["id"] == idea.id
    assert item["title"] == "Solar bench"
    assert item["description"] == "A bench with a phone charger"
    assert item["voteCount"] == 2


def test_ac019_an_idea_with_no_votes_shows_a_count_of_zero(
    client: TestClient, db_session: Session
) -> None:
    author = _user(db_session)
    _idea(db_session, author, "Quiet idea", "Nobody voted yet")

    response = client.get("/ideas")

    assert response.status_code == 200
    [item] = response.json()
    assert item["title"] == "Quiet idea"
    assert item["description"] == "Nobody voted yet"
    assert item["voteCount"] == 0
    assert item["voted"] is False

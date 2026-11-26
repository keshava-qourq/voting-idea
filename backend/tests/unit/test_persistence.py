"""US-014: accounts, ideas and votes are kept in permanent storage, one vote per pair."""

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import USER_ROLE, ensure_user, find_user
from app.models import Idea, User, Vote

_BACKEND = Path(__file__).resolve().parent.parent.parent


def _migrate(url: str) -> None:
    config = Config(str(_BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(_BACKEND / "alembic"))
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(config, "head")


def _new_user(session: Session) -> User:
    email = f"{uuid4().hex[:12]}@example.com"
    ensure_user(session, email=email, password=uuid4().hex, role=USER_ROLE)
    user = find_user(session, email)
    assert user is not None
    return user


def _new_idea(session: Session, author: User, title: str = "An idea") -> Idea:
    idea = Idea(
        id=str(uuid4()),
        user_id=author.id,
        title=title,
        description="Short description",
        created_at=datetime.now(UTC),
    )
    session.add(idea)
    session.flush()
    return idea


def _vote(session: Session, user: User, idea: Idea) -> Vote:
    vote = Vote(id=str(uuid4()), user_id=user.id, idea_id=idea.id, created_at=datetime.now(UTC))
    session.add(vote)
    session.flush()
    return vote


def _ranking(session: Session) -> list[tuple[str, int]]:
    count = func.count(Vote.id)
    rows = session.execute(
        select(Idea.title, count)
        .outerjoin(Vote, Vote.idea_id == Idea.id)
        .group_by(Idea.id, Idea.title)
        .order_by(count.desc(), Idea.title)
    ).all()
    return [(title, votes) for title, votes in rows]


@pytest.fixture
def file_engine(tmp_path: Path) -> Iterator[Engine]:
    """A database in a file, migrated: what the app keeps on disk between runs."""
    url = f"sqlite:///{tmp_path / 'restart.db'}"
    _migrate(url)
    engine = create_engine(url, future=True)
    yield engine
    engine.dispose()


def test_ac038_accounts_ideas_and_votes_survive_a_restart(file_engine: Engine) -> None:
    url = file_engine.url
    with Session(file_engine) as session:
        author, voter = _new_user(session), _new_user(session)
        first = _new_idea(session, author, "First")
        second = _new_idea(session, author, "Second")
        _vote(session, voter, second)
        _vote(session, author, second)
        _vote(session, voter, first)
        session.commit()
        emails = sorted(u.email for u in (author, voter))
        before = _ranking(session)
    assert before == [("Second", 2), ("First", 1)]

    file_engine.dispose()  # the app stops
    restarted = create_engine(url, future=True)  # the app starts again
    try:
        _migrate(url.render_as_string(hide_password=False))  # start-up migrates: no change
        with Session(restarted) as session:
            assert sorted(session.scalars(select(User.email)).all()) == emails
            assert session.scalar(select(func.count(Idea.id))) == 2
            assert session.scalar(select(func.count(Vote.id))) == 3
            assert _ranking(session) == before
    finally:
        restarted.dispose()


def test_ac038_sessions_are_part_of_the_stored_tables(file_engine: Engine) -> None:
    assert {"users", "sessions", "ideas", "votes"} <= set(inspect(file_engine).get_table_names())


def test_ac039_the_migration_makes_the_user_idea_pair_unique(file_engine: Engine) -> None:
    constraints = inspect(file_engine).get_unique_constraints("votes")
    assert [c["column_names"] for c in constraints] == [["user_id", "idea_id"]]


def test_ac039_rejects_a_second_vote_by_the_same_user_on_the_same_idea(
    db_session: Session,
) -> None:
    author, voter = _new_user(db_session), _new_user(db_session)
    idea = _new_idea(db_session, author)
    _vote(db_session, voter, idea)
    with pytest.raises(IntegrityError), db_session.begin_nested():
        _vote(db_session, voter, idea)
    assert db_session.scalar(select(func.count(Vote.id)).where(Vote.idea_id == idea.id)) == 1


def test_ac039_the_same_user_may_vote_on_other_ideas_and_others_on_the_same_idea(
    db_session: Session,
) -> None:
    author, voter = _new_user(db_session), _new_user(db_session)
    first, second = _new_idea(db_session, author), _new_idea(db_session, author)
    _vote(db_session, voter, first)
    _vote(db_session, voter, second)
    _vote(db_session, author, first)
    assert db_session.scalar(select(func.count(Vote.id))) == 3

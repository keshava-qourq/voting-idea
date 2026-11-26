"""Tied ideas ordered newest first (US-006): GET /ideas, proved on the test database."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient

DARK = ("Add dark mode", "Switch the board to a dark theme")
DEMO = ("Weekly demo day", "Show finished work every Friday")
COFFEE = ("Free coffee Fridays", "Coffee for the whole office")
LUNCH = ("Team lunch", "Monthly lunch for all teams")
OLDER = ("Older idea: Add dark mode", "Switch the board to a dark theme")
NEWER = ("Newer idea: Weekly demo day", "Show finished work every Friday")


def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def _sign_up(client: TestClient, name: str) -> str:
    """Sign up a new user with a unique email; return the session token."""
    pw = secrets.token_urlsafe(16)
    email = f"{name}-{uuid4().hex[:10]}@example.com"
    response = client.post("/auth/signup", json={"email": email, "password": pw})
    assert response.status_code == 201, response.text
    tok = response.json()["token"]
    assert tok
    return tok


def _post_idea(client: TestClient, tok: str, idea: tuple[str, str]) -> str:
    title, description = idea
    response = client.post(
        "/ideas",
        json={"title": title, "description": description},
        headers=_bearer(tok),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["voteCount"] == 0
    return body["id"]


def _vote(client: TestClient, tok: str, idea_id: str) -> None:
    response = client.post(f"/ideas/{idea_id}/vote", headers=_bearer(tok))
    assert response.status_code == 200, response.text


def _board(client: TestClient, ids: set[str]) -> list[dict]:
    """The public board, read with no login, narrowed to the ideas this test made."""
    response = client.get("/ideas")
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    return [idea for idea in body if idea["id"] in ids]


def test_tc074_ideas_with_no_votes_are_listed_newest_first(client: TestClient) -> None:
    alice = _sign_up(client, "alice")
    ids = {
        title: _post_idea(client, alice, idea)
        for title, idea in [(DARK[0], DARK), (DEMO[0], DEMO), (COFFEE[0], COFFEE)]
    }

    board = _board(client, set(ids.values()))

    assert [idea["title"] for idea in board] == [COFFEE[0], DEMO[0], DARK[0]]
    assert {idea["voteCount"] for idea in board} == {0}

    again = _board(client, set(ids.values()))
    assert [idea["title"] for idea in again] == [COFFEE[0], DEMO[0], DARK[0]]


def test_tc075_ties_are_ordered_newest_first_inside_each_vote_count(
    client: TestClient,
) -> None:
    alice = _sign_up(client, "alice")
    ids = {idea[0]: _post_idea(client, alice, idea) for idea in [DARK, DEMO, COFFEE, LUNCH]}
    bob = _sign_up(client, "bob")
    _vote(client, bob, ids[DARK[0]])
    _vote(client, bob, ids[COFFEE[0]])

    board = _board(client, set(ids.values()))

    assert [idea["title"] for idea in board] == [
        COFFEE[0],
        DARK[0],
        LUNCH[0],
        DEMO[0],
    ]
    assert [idea["voteCount"] for idea in board] == [1, 1, 0, 0]

    again = _board(client, set(ids.values()))
    assert [idea["title"] for idea in again] == [idea["title"] for idea in board]


def test_tc078_newer_idea_that_gains_a_vote_moves_above_the_older_idea(
    client: TestClient,
) -> None:
    alice = _sign_up(client, "alice")
    older_id = _post_idea(client, alice, OLDER)
    newer_id = _post_idea(client, alice, NEWER)
    ids = {older_id, newer_id}
    bob = _sign_up(client, "bob")

    _vote(client, bob, older_id)
    before = _board(client, ids)
    assert [idea["id"] for idea in before] == [older_id, newer_id]
    assert [idea["voteCount"] for idea in before] == [1, 0]

    _vote(client, bob, newer_id)
    after = _board(client, ids)
    assert [idea["id"] for idea in after] == [newer_id, older_id]
    assert [idea["voteCount"] for idea in after] == [1, 1]

    later = _board(client, ids)
    assert [idea["id"] for idea in later] == [newer_id, older_id]


def test_tc079_repeat_vote_attempt_on_the_older_idea_leaves_the_tie_unchanged(
    client: TestClient,
) -> None:
    alice = _sign_up(client, "alice")
    older_id = _post_idea(client, alice, OLDER)
    newer_id = _post_idea(client, alice, NEWER)
    ids = {older_id, newer_id}
    bob = _sign_up(client, "bob")

    _vote(client, bob, older_id)
    _vote(client, bob, newer_id)
    # The second attempt is answered; how it is answered is not checked in this case.
    client.post(f"/ideas/{older_id}/vote", headers=_bearer(bob))

    board = _board(client, ids)

    assert [idea["id"] for idea in board] == [newer_id, older_id]
    assert [idea["voteCount"] for idea in board] == [1, 1]

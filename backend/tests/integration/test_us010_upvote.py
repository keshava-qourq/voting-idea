"""Upvote an idea (US-010): POST /ideas/{idea_id}/vote adds one permanent vote per user."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient


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


def _post_idea(client: TestClient, tok: str, title: str, description: str) -> dict:
    response = client.post(
        "/ideas",
        json={"title": title, "description": description},
        headers=_bearer(tok),
    )
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["voteCount"] == 0
    return created


def _board(client: TestClient, tok: str | None = None) -> list[dict]:
    headers = _bearer(tok) if tok else {}
    response = client.get("/ideas", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def _by_id(board: list[dict], idea_id: str) -> dict:
    matching = [idea for idea in board if idea["id"] == idea_id]
    assert len(matching) == 1
    return matching[0]


def _position(board: list[dict], idea_id: str) -> int:
    return [idea["id"] for idea in board].index(idea_id)


def test_tc056_upvote_adds_exactly_one_vote_and_reorders_the_board(
    client: TestClient,
) -> None:
    maya = _sign_up(client, "maya")
    dark = _post_idea(client, maya, "Dark mode", "Add a dark theme")
    offline = _post_idea(client, maya, "Offline mode", "Work without internet")
    ben = _sign_up(client, "ben")

    before = _board(client, ben)
    assert _by_id(before, dark["id"])["voteCount"] == 0
    assert _by_id(before, offline["id"])["voteCount"] == 0
    assert _by_id(before, dark["id"])["voted"] is False
    assert _by_id(before, offline["id"])["voted"] is False
    assert _position(before, offline["id"]) < _position(before, dark["id"])

    vote = client.post(f"/ideas/{dark['id']}/vote", headers=_bearer(ben))
    assert vote.status_code == 200, vote.text

    after = _board(client, ben)
    assert _by_id(after, dark["id"])["voteCount"] == 1
    assert _by_id(after, dark["id"])["voted"] is True
    assert _by_id(after, offline["id"])["voteCount"] == 0
    assert _position(after, dark["id"]) < _position(after, offline["id"])


def test_tc058_vote_without_login_is_refused(client: TestClient) -> None:
    nora = _sign_up(client, "nora")
    idea = _post_idea(client, nora, "Dark mode", "Add a dark theme")

    response = client.post(f"/ideas/{idea['id']}/vote")

    assert response.status_code == 401, response.text
    assert _by_id(_board(client), idea["id"])["voteCount"] == 0


def test_tc060_vote_on_an_idea_that_does_not_exist(client: TestClient) -> None:
    carl = _sign_up(client, "carl")

    response = client.post("/ideas/99999/vote", headers=_bearer(carl))

    assert response.status_code == 404, response.text


def test_tc061_user_votes_on_their_own_idea(client: TestClient) -> None:
    olive = _sign_up(client, "olive")
    idea = _post_idea(client, olive, "Calendar export", "Export ideas to a calendar")

    vote = client.post(f"/ideas/{idea['id']}/vote", headers=_bearer(olive))
    assert vote.status_code == 200, vote.text

    mine = _by_id(_board(client, olive), idea["id"])
    assert mine["voteCount"] == 1
    assert mine["voted"] is True


def test_tc063_repeat_vote_cannot_remove_or_double_the_vote(client: TestClient) -> None:
    vera = _sign_up(client, "vera")
    idea = _post_idea(client, vera, "Search filters", "Filter ideas by keyword")
    walt = _sign_up(client, "walt")

    first = client.post(f"/ideas/{idea['id']}/vote", headers=_bearer(walt))
    assert first.status_code == 200, first.text

    repeat = client.post(f"/ideas/{idea['id']}/vote", headers=_bearer(walt))
    assert repeat.status_code == 200, repeat.text

    mine = _by_id(_board(client, walt), idea["id"])
    assert mine["voteCount"] == 1
    assert mine["voted"] is True

"""Voting needs a login (US-012): a visitor's vote is refused, the board stays readable."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient

DARK_TITLE = "Add dark mode"
DARK_DESC = "Add a dark colour theme."
SEARCH_TITLE = "Faster search"
SEARCH_DESC = "Make the search answer faster."


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
    return response.json()


def _idea_with_votes(client: TestClient, title: str, description: str, votes: int) -> dict:
    author = _sign_up(client, "author")
    idea = _post_idea(client, author, title, description)
    for index in range(votes):
        voter = _sign_up(client, f"voter{index}")
        vote = client.post(f"/ideas/{idea['id']}/vote", headers=_bearer(voter))
        assert vote.status_code == 200, vote.text
    return idea


def _board(client: TestClient) -> list[dict]:
    """Read the board with no login token."""
    response = client.get("/ideas")
    assert response.status_code == 200, response.text
    return response.json()


def _by_id(board: list[dict], idea_id: str) -> dict:
    matching = [idea for idea in board if idea["id"] == idea_id]
    assert len(matching) == 1
    return matching[0]


def test_tc104_vote_without_login_is_refused_and_count_stays_the_same(
    client: TestClient,
) -> None:
    dark = _idea_with_votes(client, DARK_TITLE, DARK_DESC, 3)

    before = _by_id(_board(client), dark["id"])
    assert before["title"] == DARK_TITLE
    assert before["voteCount"] == 3

    response = client.post(f"/ideas/{dark['id']}/vote")

    assert response.status_code == 401, response.text

    after = _by_id(_board(client), dark["id"])
    assert after["voteCount"] == 3


def test_tc105_vote_with_an_invalid_login_token_is_refused(client: TestClient) -> None:
    dark = _idea_with_votes(client, DARK_TITLE, DARK_DESC, 3)

    response = client.post(
        f"/ideas/{dark['id']}/vote",
        headers=_bearer("not-a-real-token-123"),
    )

    assert response.status_code == 401, response.text

    after = _by_id(_board(client), dark["id"])
    assert after["voteCount"] == 3


def test_tc108_visitor_can_read_the_board_with_vote_counts(client: TestClient) -> None:
    dark = _idea_with_votes(client, DARK_TITLE, DARK_DESC, 3)
    search = _idea_with_votes(client, SEARCH_TITLE, SEARCH_DESC, 0)

    response = client.get("/ideas")

    assert response.status_code == 200, response.text
    board = response.json()
    dark_idea = _by_id(board, dark["id"])
    search_idea = _by_id(board, search["id"])
    assert dark_idea["title"] == DARK_TITLE
    assert dark_idea["voteCount"] == 3
    assert search_idea["title"] == SEARCH_TITLE
    assert search_idea["voteCount"] == 0
    ids = [idea["id"] for idea in board]
    assert ids.index(dark["id"]) < ids.index(search["id"])

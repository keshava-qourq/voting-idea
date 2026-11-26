"""Vote count on every idea (US-007): GET /ideas shows title, description and vote count."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient

DARK_TITLE = "Dark mode for dashboard"
DARK_DESC = "Add a dark colour theme to the dashboard for night use."
DIGEST_TITLE = "Weekly digest email"
DIGEST_DESC = "Send a weekly summary of the top ideas."


def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def _sign_up(client: TestClient, name: str) -> tuple[str, str]:
    """Sign up a new user with a unique email; return (session token, email)."""
    pw = secrets.token_urlsafe(16)
    email = f"{name}-{uuid4().hex[:10]}@example.com"
    response = client.post("/auth/signup", json={"email": email, "password": pw})
    assert response.status_code == 201, response.text
    tok = response.json()["token"]
    assert tok
    return tok, email


def _post_idea(client: TestClient, tok: str, title: str, description: str) -> dict:
    response = client.post(
        "/ideas",
        json={"title": title, "description": description},
        headers=_bearer(tok),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_tc065_new_idea_is_listed_with_title_description_and_zero_votes(
    client: TestClient,
) -> None:
    alice, _ = _sign_up(client, "alice")
    created = _post_idea(client, alice, DARK_TITLE, DARK_DESC)

    response = client.get("/ideas")

    assert response.status_code == 200, response.text
    board = response.json()
    assert len(board) == 1
    assert board[0]["id"] == created["id"]
    assert board[0]["title"] == DARK_TITLE
    assert board[0]["description"] == DARK_DESC
    assert board[0]["voteCount"] == 0


def test_tc066_vote_count_in_the_list_follows_real_votes(client: TestClient) -> None:
    alice, _ = _sign_up(client, "alice")
    dark = _post_idea(client, alice, DARK_TITLE, DARK_DESC)
    digest = _post_idea(client, alice, DIGEST_TITLE, DIGEST_DESC)
    bob, _ = _sign_up(client, "bob")

    vote = client.post(f"/ideas/{dark['id']}/vote", headers=_bearer(bob))
    assert vote.status_code == 200, vote.text

    response = client.get("/ideas")

    assert response.status_code == 200, response.text
    by_id = {idea["id"]: idea for idea in response.json()}
    assert set(by_id) == {dark["id"], digest["id"]}
    assert by_id[dark["id"]]["title"] == DARK_TITLE
    assert by_id[dark["id"]]["description"] == DARK_DESC
    assert by_id[dark["id"]]["voteCount"] == 1
    assert by_id[digest["id"]]["title"] == DIGEST_TITLE
    assert by_id[digest["id"]]["description"] == DIGEST_DESC
    assert by_id[digest["id"]]["voteCount"] == 0


def test_tc067_empty_board_returns_no_ideas(client: TestClient) -> None:
    response = client.get("/ideas")

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_tc071_public_list_offers_only_title_description_and_vote_count(
    client: TestClient,
) -> None:
    alice, email = _sign_up(client, "alice")
    created = _post_idea(client, alice, DARK_TITLE, DARK_DESC)

    response = client.get("/ideas", headers=_bearer(alice))

    assert response.status_code == 200, response.text
    board = response.json()
    assert len(board) == 1
    idea = board[0]
    assert idea["id"] == created["id"]
    assert idea["title"] == DARK_TITLE
    assert idea["description"] == DARK_DESC
    assert idea["voteCount"] == 0
    for key in idea:
        assert "comment" not in key.lower(), key
        assert "categor" not in key.lower(), key
    assert email not in response.text

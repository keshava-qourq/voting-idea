"""Ranked public board (US-005): GET /ideas, proved on the test database."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient


def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def _sign_up(client: TestClient, name: str = "voter") -> str:
    """Sign up a new user with a unique email; return the session token."""
    pw = secrets.token_urlsafe(16)
    email = f"{name}-{uuid4().hex[:10]}@example.com"
    response = client.post("/auth/signup", json={"email": email, "password": pw})
    assert response.status_code == 201, response.text
    tok = response.json()["token"]
    assert tok
    return tok


def _post_idea(client: TestClient, tok: str, title: str, description: str = "A good idea") -> dict:
    response = client.post(
        "/ideas",
        json={"title": title, "description": description},
        headers=_bearer(tok),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _vote(client: TestClient, tok: str, idea_id: str) -> dict:
    response = client.post(f"/ideas/{idea_id}/vote", headers=_bearer(tok))
    assert response.status_code == 200, response.text
    return response.json()


def _ideas_with_votes(client: TestClient, spec: list[tuple[str, int]]) -> dict[str, str]:
    """Make one idea per (title, votes) with that many distinct voters; return title -> id."""
    author = _sign_up(client, "author")
    most = max(votes for _, votes in spec)
    voters = [_sign_up(client) for _ in range(most)]
    ids: dict[str, str] = {}
    for title, votes in spec:
        idea = _post_idea(client, author, title)
        ids[title] = idea["id"]
        for tok in voters[:votes]:
            _vote(client, tok, idea["id"])
    return ids


def _board(client: TestClient) -> list[dict]:
    """The public board, read with no login."""
    response = client.get("/ideas")
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    return body


def _mine(board: list[dict], ids: dict[str, str]) -> list[dict]:
    """Only the ideas this test made, in board order."""
    wanted = set(ids.values())
    return [idea for idea in board if idea["id"] in wanted]


def test_tc081_board_lists_ideas_by_vote_count_highest_first_with_no_login(
    client: TestClient,
) -> None:
    ids = _ideas_with_votes(client, [("Free lunch", 2), ("Standing desks", 9), ("Dark mode", 5)])

    board = _mine(_board(client), ids)

    assert [idea["title"] for idea in board] == ["Standing desks", "Dark mode", "Free lunch"]
    assert [idea["voteCount"] for idea in board] == [9, 5, 2]


def test_tc083_ideas_with_equal_votes_stay_between_higher_and_lower_counts(
    client: TestClient,
) -> None:
    ids = _ideas_with_votes(
        client,
        [("Quiet room", 1), ("Dark mode", 3), ("Standing desks", 9), ("Free lunch", 3)],
    )

    board = _mine(_board(client), ids)

    assert len(board) == 4
    assert board[0]["title"] == "Standing desks"
    assert board[-1]["title"] == "Quiet room"
    assert {board[1]["title"], board[2]["title"]} == {"Dark mode", "Free lunch"}
    counts = [idea["voteCount"] for idea in board]
    assert counts == [9, 3, 3, 1]
    assert counts == sorted(counts, reverse=True)


def test_tc084_new_votes_move_an_idea_to_its_new_position(client: TestClient) -> None:
    ids = _ideas_with_votes(client, [("Dark mode", 5), ("Free lunch", 4)])
    alice = _sign_up(client, "alice")
    bob = _sign_up(client, "bob")

    before = _mine(_board(client), ids)
    assert [(i["title"], i["voteCount"]) for i in before] == [("Dark mode", 5), ("Free lunch", 4)]

    first = _vote(client, alice, ids["Free lunch"])
    assert first["voteCount"] == 5

    second = _vote(client, bob, ids["Free lunch"])
    assert second["voteCount"] == 6

    after = _mine(_board(client), ids)
    assert [(i["title"], i["voteCount"]) for i in after] == [("Free lunch", 6), ("Dark mode", 5)]


def test_tc085_repeat_vote_by_the_same_user_does_not_change_the_count(
    client: TestClient,
) -> None:
    ids = _ideas_with_votes(client, [("Dark mode", 5), ("Free lunch", 4)])
    alice = _sign_up(client, "alice")

    first = _vote(client, alice, ids["Free lunch"])
    assert first["voteCount"] == 5

    again = _vote(client, alice, ids["Free lunch"])
    assert again["voteCount"] == 5

    board = _mine(_board(client), ids)
    by_title = {idea["title"]: idea["voteCount"] for idea in board}
    assert by_title["Free lunch"] == 5
    assert by_title["Dark mode"] == 5


def test_tc087_empty_board_returns_no_ideas(client: TestClient) -> None:
    response = client.get("/ideas")

    assert response.status_code == 200, response.text
    assert response.json() == []


def test_tc089_board_is_no_longer_empty_once_the_first_idea_is_posted(
    client: TestClient,
) -> None:
    carol = _sign_up(client, "carol")

    created = _post_idea(
        client,
        carol,
        "Standing desks",
        "Let us have adjustable desks in the office.",
    )
    assert created["voteCount"] == 0

    board = _board(client)

    assert len(board) == 1
    assert board[0]["id"] == created["id"]
    assert board[0]["title"] == "Standing desks"
    assert board[0]["voteCount"] == 0

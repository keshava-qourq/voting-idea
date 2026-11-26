"""US-014: accounts, ideas and votes are kept (AC-038, AC-039, AC-040).

A test cannot stop and start the app, so the "restart" cases drop everything the app
could hold in memory: the test's session cache is expired, and every client and token is
new (new TestClient, new login). What is read afterwards can only come from the stored
data.
"""

import secrets
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app

_VOTE_KEYS = ("voteCount", "votes", "votesCount", "voteTotal", "score")
_VOTED_KEYS = ("hasVoted", "votedByMe", "voted", "viewerHasVoted", "votedByCurrentUser")
_OK = (200, 201, 204)


def _suffix() -> str:
    return uuid4().hex[:10]


def _password() -> str:
    return secrets.token_urlsafe(16)


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _signup(client: TestClient, name: str) -> dict[str, str]:
    email = f"{name}-{_suffix()}@example.com"
    password = _password()
    response = client.post("/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 201, response.text
    token = response.json()["token"]
    assert token
    return {"email": email, "password": password, "token": token}


def _login(email: str, password: str) -> dict[str, str]:
    """A brand new client with no memory of earlier requests, signed in through /auth/login."""
    fresh = TestClient(app)
    response = fresh.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return _bearer(response.json()["token"])


def _create_idea(client: TestClient, user: dict[str, str], title: str, description: str) -> str:
    response = client.post(
        "/ideas",
        json={"title": title, "description": description},
        headers=_bearer(user["token"]),
    )
    assert response.status_code in (200, 201), response.text
    idea = response.json()
    assert _votes(idea) == 0, response.text
    return str(idea["id"])


def _vote(client: TestClient, idea_id: str, headers: dict[str, str]) -> None:
    response = client.post(f"/ideas/{idea_id}/vote", headers=headers)
    assert response.status_code in _OK, response.text


def _votes(idea: dict[str, Any]) -> int:
    for key in _VOTE_KEYS:
        if key in idea:
            return int(idea[key])
    raise AssertionError(f"No vote count in {idea}")


def _voted(idea: dict[str, Any]) -> bool:
    for key in _VOTED_KEYS:
        if key in idea:
            return bool(idea[key])
    raise AssertionError(f"No voted-by-me flag in {idea}")


def _board(client: TestClient, headers: dict[str, str] | None = None) -> list[dict[str, Any]]:
    response = client.get("/ideas", headers=headers or {})
    assert response.status_code == 200, response.text
    body = response.json()
    if isinstance(body, dict):
        for key in ("items", "ideas", "data"):
            if key in body:
                body = body[key]
                break
    assert isinstance(body, list), response.text
    return body


def _mine(board: list[dict[str, Any]], *idea_ids: str) -> list[dict[str, Any]]:
    """Only this test's ideas, in the order the board lists them."""
    wanted = set(idea_ids)
    return [idea for idea in board if str(idea["id"]) in wanted]


def _restart(db_session: Session) -> None:
    """Forget everything held in memory; only stored data is left to read."""
    db_session.flush()
    db_session.expire_all()


def _make_ranked_board(client: TestClient) -> dict[str, Any]:
    alice = _signup(client, "alice")
    bob = _signup(client, "bob")
    dark = _create_idea(client, alice, f"Dark mode {_suffix()}", "Add a dark theme to the board")
    demo = _create_idea(client, alice, f"Weekly demo {_suffix()}", "Hold a short demo every Friday")
    _vote(client, demo, _bearer(alice["token"]))
    _vote(client, demo, _bearer(bob["token"]))
    return {"alice": alice, "bob": bob, "dark": dark, "demo": demo}


def test_tc040_create_accounts_ideas_and_votes_before_a_restart(client: TestClient) -> None:
    data = _make_ranked_board(client)

    board = _mine(_board(client), data["demo"], data["dark"])

    assert [str(i["id"]) for i in board] == [data["demo"], data["dark"]]
    assert [_votes(i) for i in board] == [2, 0]


def test_tc041_accounts_ideas_votes_and_ranking_survive_a_restart(
    client: TestClient, db_session: Session
) -> None:
    data = _make_ranked_board(client)
    before = [str(i["id"]) for i in _mine(_board(client), data["demo"], data["dark"])]
    assert before == [data["demo"], data["dark"]]

    _restart(db_session)

    health = client.get("/health")
    assert health.status_code == 200, health.text
    assert health.json()["status"] == "ok"

    for user in (data["alice"], data["bob"]):
        headers = _login(user["email"], user["password"])
        board = _mine(_board(client, headers), data["demo"], data["dark"])

        assert [str(i["id"]) for i in board] == [data["demo"], data["dark"]]
        assert [_votes(i) for i in board] == [2, 0]
        assert _voted(board[0]) is True
        assert _voted(board[1]) is False


def test_tc043_repeated_votes_by_one_user_count_only_once(client: TestClient) -> None:
    dave = _signup(client, "dave")
    idea_id = _create_idea(
        client, dave, f"Standing desks {_suffix()}", "Offer standing desks in the office"
    )
    headers = _bearer(dave["token"])

    _vote(client, idea_id, headers)
    _vote(client, idea_id, headers)
    _vote(client, idea_id, headers)

    board = _mine(_board(client, headers), idea_id)
    assert len(board) == 1
    assert _votes(board[0]) == 1
    assert _voted(board[0]) is True


def test_tc044_different_users_can_each_vote_on_the_same_idea(client: TestClient) -> None:
    erin = _signup(client, "erin")
    frank = _signup(client, "frank")
    idea_id = _create_idea(
        client, erin, f"Open roadmap {_suffix()}", "Share the product roadmap with the team"
    )

    _vote(client, idea_id, _bearer(erin["token"]))
    _vote(client, idea_id, _bearer(frank["token"]))
    _vote(client, idea_id, _bearer(frank["token"]))

    board = _mine(_board(client), idea_id)
    assert len(board) == 1
    assert _votes(board[0]) == 2


def test_tc045_a_stored_vote_still_blocks_a_repeat_vote_after_a_restart(
    client: TestClient, db_session: Session
) -> None:
    data = _make_ranked_board(client)

    _restart(db_session)

    alice = data["alice"]
    headers = _login(alice["email"], alice["password"])
    _vote(client, data["demo"], headers)

    board = _mine(_board(client, headers), data["demo"])
    assert len(board) == 1
    assert _votes(board[0]) == 2


def test_tc047_all_features_work_with_no_external_service_or_key(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200, health.text
    assert health.json()["status"] == "ok"

    hana = _signup(client, "hana")
    idea_id = _create_idea(
        client, hana, f"Fruit basket {_suffix()}", "Fresh fruit in the kitchen every week"
    )
    headers = _bearer(hana["token"])

    _vote(client, idea_id, headers)

    board = _mine(_board(client, headers), idea_id)
    assert len(board) == 1
    assert _votes(board[0]) == 1
    assert _voted(board[0]) is True

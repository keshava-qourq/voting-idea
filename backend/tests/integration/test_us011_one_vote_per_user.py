"""One vote per user per idea (US-011): a repeat vote changes nothing, other votes count."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient


def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def _sign_up(client: TestClient, name: str) -> tuple[str, str, str]:
    """Sign up a new user with a unique email; return (email, pw, token)."""
    pw = secrets.token_urlsafe(16)
    email = f"{name}-{uuid4().hex[:10]}@example.com"
    response = client.post("/auth/signup", json={"email": email, "password": pw})
    assert response.status_code == 201, response.text
    tok = response.json()["token"]
    assert tok
    return email, pw, tok


def _log_in(client: TestClient, email: str, pw: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": pw})
    assert response.status_code == 200, response.text
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


def _vote(client: TestClient, tok: str, idea_id: str) -> None:
    response = client.post(f"/ideas/{idea_id}/vote", headers=_bearer(tok))
    assert response.status_code == 200, response.text


def test_tc121_board_data_marks_an_idea_i_have_voted_on(client: TestClient) -> None:
    _, _, alice = _sign_up(client, "alice")
    idea = _post_idea(client, alice, "Dark mode", "Add a dark theme to the app")

    before = _by_id(_board(client, alice), idea["id"])
    assert before["title"] == "Dark mode"
    assert before["voteCount"] == 0
    assert before["voted"] is False

    _vote(client, alice, idea["id"])

    after = _by_id(_board(client, alice), idea["id"])
    assert after["voteCount"] == 1
    assert after["voted"] is True


def test_tc122_another_user_and_a_visitor_do_not_see_my_vote_marker(
    client: TestClient,
) -> None:
    _, _, alice = _sign_up(client, "alice")
    bob_email, bob_pw, _ = _sign_up(client, "bob")
    idea = _post_idea(client, alice, "Dark mode", "Add a dark theme to the app")
    _vote(client, alice, idea["id"])

    bob = _log_in(client, bob_email, bob_pw)

    for_bob = _by_id(_board(client, bob), idea["id"])
    assert for_bob["voteCount"] == 1
    assert for_bob["voted"] is False

    for_visitor = _by_id(_board(client), idea["id"])
    assert for_visitor["voteCount"] == 1
    assert not for_visitor.get("voted")

    for_alice = _by_id(_board(client, alice), idea["id"])
    assert for_alice["voteCount"] == 1
    assert for_alice["voted"] is True


def test_tc124_repeating_the_same_vote_changes_nothing(client: TestClient) -> None:
    _, _, carol = _sign_up(client, "carol")
    idea = _post_idea(client, carol, "Weekly demo", "Hold a demo every Friday")

    _vote(client, carol, idea["id"])
    _vote(client, carol, idea["id"])

    mine = _by_id(_board(client, carol), idea["id"])
    assert mine["voteCount"] == 1
    assert mine["voted"] is True


def test_tc125_several_repeated_requests_in_a_row_create_one_vote(
    client: TestClient,
) -> None:
    _, _, dave = _sign_up(client, "dave")
    idea = _post_idea(client, dave, "Team lunch", "Monthly team lunch")

    _vote(client, dave, idea["id"])
    _vote(client, dave, idea["id"])
    _vote(client, dave, idea["id"])

    mine = _by_id(_board(client, dave), idea["id"])
    assert mine["voteCount"] == 1
    assert mine["voted"] is True


def test_tc126_second_session_of_the_same_user_cannot_vote_twice(
    client: TestClient,
) -> None:
    erin_email, erin_pw, owner = _sign_up(client, "erin")
    idea = _post_idea(client, owner, "Quiet room", "Set aside a quiet room")

    first_tab = _log_in(client, erin_email, erin_pw)
    second_tab = _log_in(client, erin_email, erin_pw)

    _vote(client, first_tab, idea["id"])
    _vote(client, second_tab, idea["id"])

    mine = _by_id(_board(client, second_tab), idea["id"])
    assert mine["voteCount"] == 1
    assert mine["voted"] is True


def test_tc127_different_users_can_each_vote_once_on_the_same_idea(
    client: TestClient,
) -> None:
    _, _, alice = _sign_up(client, "alice")
    bob_email, bob_pw, _ = _sign_up(client, "bob")
    idea = _post_idea(client, alice, "Dark mode", "Add a dark theme to the app")
    _vote(client, alice, idea["id"])

    bob = _log_in(client, bob_email, bob_pw)
    _vote(client, bob, idea["id"])
    _vote(client, bob, idea["id"])

    for_bob = _by_id(_board(client, bob), idea["id"])
    assert for_bob["voteCount"] == 2
    assert for_bob["voted"] is True


def test_tc130_voting_on_a_different_idea_is_accepted(client: TestClient) -> None:
    _, _, frank = _sign_up(client, "frank")
    desks = _post_idea(client, frank, "Standing desks", "Offer standing desks")
    bikes = _post_idea(client, frank, "Bike storage", "Add a covered bike rack")

    _vote(client, frank, desks["id"])
    _vote(client, frank, bikes["id"])

    board = _board(client, frank)
    for idea in (desks, bikes):
        mine = _by_id(board, idea["id"])
        assert mine["voteCount"] == 1
        assert mine["voted"] is True

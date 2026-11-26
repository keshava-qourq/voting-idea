"""Setup and usage guide (US-016): the app runs on its own and the usage steps work."""

import secrets

from fastapi.testclient import TestClient


def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def _sign_up(client: TestClient, email: str, pw: str) -> str:
    response = client.post("/auth/signup", json={"email": email, "password": pw})
    assert response.status_code == 201, response.text
    tok = response.json()["token"]
    assert tok
    return tok


def test_tc132_fresh_app_reports_healthy_and_serves_an_empty_board(
    client: TestClient,
) -> None:
    health = client.get("/health")
    assert health.status_code == 200, health.text
    assert health.json() == {"status": "ok"}

    board = client.get("/ideas")
    assert board.status_code == 200, board.text
    assert board.json() == []


def test_tc135_usage_steps_work_from_sign_up_to_upvote(client: TestClient) -> None:
    email = "dana@example.com"
    pw = secrets.token_urlsafe(16)

    signup = client.post("/auth/signup", json={"email": email, "password": pw})
    assert signup.status_code == 201, signup.text
    first_tok = signup.json()["token"]
    assert first_tok
    assert signup.json()["email"] == email
    me = client.get("/auth/me", headers=_bearer(first_tok))
    assert me.status_code == 200, me.text

    logout = client.post("/auth/logout", headers=_bearer(first_tok))
    assert logout.status_code == 200, logout.text
    assert logout.json()["loggedOut"] is True

    login = client.post("/auth/login", json={"email": email, "password": pw})
    assert login.status_code == 200, login.text
    tok = login.json()["token"]
    assert tok

    created = client.post(
        "/ideas",
        json={"title": "Add dark mode", "description": "A dark theme for late-night use."},
        headers=_bearer(tok),
    )
    assert created.status_code == 201, created.text
    idea = created.json()
    assert idea["voteCount"] == 0
    assert idea["title"] == "Add dark mode"

    vote = client.post(f"/ideas/{idea['id']}/vote", headers=_bearer(tok))
    assert vote.status_code == 200, vote.text

    board = client.get("/ideas", headers=_bearer(tok))
    assert board.status_code == 200, board.text
    mine = [i for i in board.json() if i["id"] == idea["id"]]
    assert len(mine) == 1
    assert mine[0]["title"] == "Add dark mode"
    assert mine[0]["voteCount"] == 1
    assert mine[0]["voted"] is True


def test_tc136_a_vote_is_not_taken_back_by_voting_again(client: TestClient) -> None:
    ivan_pw = secrets.token_urlsafe(16)
    ivan = _sign_up(client, "ivan@example.com", ivan_pw)
    posted = client.post(
        "/ideas",
        json={"title": "Free coffee on Fridays", "description": "Coffee for the team."},
        headers=_bearer(ivan),
    )
    assert posted.status_code == 201, posted.text
    idea_id = posted.json()["id"]
    assert posted.json()["voteCount"] == 0

    pw = secrets.token_urlsafe(16)
    tok = _sign_up(client, "erin@example.com", pw)

    before = client.get("/ideas", headers=_bearer(tok))
    assert before.status_code == 200, before.text
    listed = [i for i in before.json() if i["id"] == idea_id]
    assert len(listed) == 1
    assert listed[0]["title"] == "Free coffee on Fridays"
    assert listed[0]["voteCount"] == 0

    first = client.post(f"/ideas/{idea_id}/vote", headers=_bearer(tok))
    assert first.status_code == 200, first.text

    repeat = client.post(f"/ideas/{idea_id}/vote", headers=_bearer(tok))
    assert repeat.status_code == 200, repeat.text
    assert repeat.json()["voteCount"] == 1

    after = client.get("/ideas", headers=_bearer(tok))
    assert after.status_code == 200, after.text
    final = [i for i in after.json() if i["id"] == idea_id]
    assert len(final) == 1
    assert final[0]["voteCount"] == 1
    assert final[0]["voted"] is True


def test_tc137_no_email_verification_and_generic_message_for_wrong_password(
    client: TestClient,
) -> None:
    email = "frank@example.com"
    pw = secrets.token_urlsafe(16)
    wrong = secrets.token_urlsafe(16)

    tok = _sign_up(client, email, pw)

    me = client.get("/auth/me", headers=_bearer(tok))
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email

    refused = client.post("/auth/login", json={"email": email, "password": wrong})
    assert refused.status_code == 401, refused.text
    body = refused.json()
    assert body["code"]
    assert body["message"]

    # The refusal is the same as for an unknown email: it does not say which part was wrong.
    unknown = client.post(
        "/auth/login",
        json={"email": "nobody-frank@example.com", "password": wrong},
    )
    assert unknown.status_code == 401, unknown.text
    assert unknown.json() == body


def test_tc140_app_runs_with_self_chosen_values_in_place_of_placeholders(
    client: TestClient,
) -> None:
    health = client.get("/health")
    assert health.status_code == 200, health.text
    assert health.json() == {"status": "ok"}

    email = "henry@example.com"
    pw = secrets.token_urlsafe(16)
    tok = _sign_up(client, email, pw)

    me = client.get("/auth/me", headers=_bearer(tok))
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email

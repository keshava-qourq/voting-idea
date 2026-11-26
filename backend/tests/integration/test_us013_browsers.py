"""Board and forms on desktop and mobile (US-013): the API behind every browser flow."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient


def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def _sign_up(client: TestClient, name: str) -> tuple[str, str, str]:
    """Sign up a new user with a unique email; return (email, pw, tok)."""
    pw = secrets.token_urlsafe(16)
    email = f"{name}-{uuid4().hex[:10]}@example.com"
    response = client.post("/auth/signup", json={"email": email, "password": pw})
    assert response.status_code == 201, response.text
    tok = response.json()["token"]
    assert tok
    return email, pw, tok


def _post_idea(client: TestClient, tok: str, title: str, description: str) -> dict:
    response = client.post(
        "/ideas",
        json={"title": title, "description": description},
        headers=_bearer(tok),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _vote(client: TestClient, tok: str, idea_id: str) -> None:
    response = client.post(f"/ideas/{idea_id}/vote", headers=_bearer(tok))
    assert response.status_code == 200, response.text


def _board(client: TestClient, tok: str | None = None) -> list[dict]:
    headers = _bearer(tok) if tok else {}
    response = client.get("/ideas", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    return body


def test_tc142_long_idea_title_is_returned_whole_for_the_phone_board(
    client: TestClient,
) -> None:
    _, _, tok = _sign_up(client, "mia")
    title = "Replace the old meeting room projectors with wireless screens"
    description = (
        "Wall-mounted wireless screens would save about ten minutes at the start of every meeting."
    )

    created = _post_idea(client, tok, title, description)
    assert created["voteCount"] == 0

    listed = [idea for idea in _board(client) if idea["id"] == created["id"]]
    assert len(listed) == 1
    assert listed[0]["title"] == title
    assert listed[0]["description"] == description
    assert listed[0]["voteCount"] == 0


def test_tc146_posting_without_a_title_is_refused(client: TestClient) -> None:
    _, _, tok = _sign_up(client, "mia")
    description = "Wall-mounted wireless screens would save time."
    before = _board(client)

    response = client.post(
        "/ideas",
        json={"title": "", "description": description},
        headers=_bearer(tok),
    )
    assert response.status_code == 422, response.text

    after = _board(client)
    assert all(idea["description"] != description for idea in after)
    assert len(after) == len(before)


def test_tc147_board_data_comes_back_complete_and_ranked_for_the_desktop_layout(
    client: TestClient,
) -> None:
    author_email, _, author = _sign_up(client, "author")
    voters = [_sign_up(client, "voter")[2] for _ in range(3)]

    bikes = _post_idea(client, author, "Add bike racks near the entrance", "Covered racks.")
    quiet = _post_idea(client, author, "Add a quiet room to the office", "A room for focus.")
    fruit = _post_idea(client, author, "Offer free fruit on Fridays", "Fresh fruit.")
    for tok in voters:
        _vote(client, tok, bikes["id"])
    _vote(client, voters[0], quiet["id"])

    response = client.get("/ideas")
    assert response.status_code == 200, response.text
    board = response.json()

    wanted = [bikes["id"], quiet["id"], fruit["id"]]
    mine = [idea for idea in board if idea["id"] in wanted]
    assert [idea["id"] for idea in mine] == wanted
    assert [idea["voteCount"] for idea in mine] == [3, 1, 0]
    assert [idea["title"] for idea in mine] == [
        "Add bike racks near the entrance",
        "Add a quiet room to the office",
        "Offer free fruit on Fridays",
    ]

    counts = [idea["voteCount"] for idea in board]
    assert counts == sorted(counts, reverse=True)
    for idea in board:
        assert "email" not in idea
        assert "authorEmail" not in idea
    assert author_email not in response.text


def test_tc150_sign_up_log_in_post_and_vote_all_work_in_one_run(client: TestClient) -> None:
    email = f"noah-{uuid4().hex[:10]}@example.com"
    pw = secrets.token_urlsafe(16)

    signup = client.post("/auth/signup", json={"email": email, "password": pw})
    assert signup.status_code == 201, signup.text

    login = client.post("/auth/login", json={"email": email, "password": pw})
    assert login.status_code == 200, login.text
    tok = login.json()["token"]
    assert tok

    created = _post_idea(
        client,
        tok,
        "Add a quiet room to the office",
        "A small room without phones for focused work.",
    )
    assert created["voteCount"] == 0

    vote = client.post(f"/ideas/{created['id']}/vote", headers=_bearer(tok))
    assert vote.status_code == 200, vote.text

    listed = [idea for idea in _board(client, tok) if idea["id"] == created["id"]]
    assert len(listed) == 1
    assert listed[0]["voteCount"] == 1
    assert listed[0]["voted"] is True


def test_tc153_log_in_with_a_wrong_password_is_refused(client: TestClient) -> None:
    email, _, _ = _sign_up(client, "noah")
    wrong = secrets.token_urlsafe(16)

    response = client.post("/auth/login", json={"email": email, "password": wrong})

    assert response.status_code == 401, response.text
    body = response.json()
    assert "token" not in body
    assert body.get("message")

    unknown = client.post(
        "/auth/login",
        json={"email": f"nobody-{uuid4().hex[:10]}@example.com", "password": wrong},
    )
    assert unknown.status_code == 401, unknown.text
    assert unknown.json()["message"] == body["message"]


def test_tc155_voting_twice_on_the_same_idea_counts_once(client: TestClient) -> None:
    _, _, tok = _sign_up(client, "noah")
    idea = _post_idea(client, tok, "Weekly demo", "Hold a demo every Friday")
    assert idea["voteCount"] == 0

    first = client.post(f"/ideas/{idea['id']}/vote", headers=_bearer(tok))
    assert first.status_code == 200, first.text
    second = client.post(f"/ideas/{idea['id']}/vote", headers=_bearer(tok))
    assert second.status_code == 200, second.text

    listed = [i for i in _board(client, tok) if i["id"] == idea["id"]]
    assert len(listed) == 1
    assert listed[0]["voteCount"] == 1
    assert listed[0]["voted"] is True

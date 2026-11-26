"""Post an idea (US-008): POST /ideas saves with zero votes, refuses bad input and no login."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient


def _bearer(tok: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tok}"}


def _login_as_new_user(client: TestClient) -> tuple[str, str]:
    """Make an account, log in through POST /auth/login; return (session token, email)."""
    pw = secrets.token_urlsafe(16)
    email = f"alice-{uuid4().hex[:10]}@example.com"
    signup = client.post("/auth/signup", json={"email": email, "password": pw})
    assert signup.status_code == 201, signup.text
    login = client.post("/auth/login", json={"email": email, "password": pw})
    assert login.status_code == 200, login.text
    tok = login.json()["token"]
    assert tok
    return tok, email


def _board(client: TestClient, tok: str | None = None) -> list[dict]:
    headers = _bearer(tok) if tok else {}
    response = client.get("/ideas", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_tc090_logged_in_user_posts_an_idea_and_it_appears_on_the_board(
    client: TestClient,
) -> None:
    title = "Shared team lunch"
    description = "Once a month the whole team eats lunch together."
    tok, email = _login_as_new_user(client)

    response = client.post(
        "/ideas",
        json={"title": title, "description": description},
        headers=_bearer(tok),
    )

    assert response.status_code == 201, response.text
    created = response.json()
    assert created["title"] == title
    assert created["description"] == description
    assert created["voteCount"] == 0

    listing = client.get("/ideas")
    assert listing.status_code == 200, listing.text
    matching = [idea for idea in listing.json() if idea["title"] == title]
    assert len(matching) == 1
    assert matching[0]["id"] == created["id"]
    assert matching[0]["description"] == description
    assert matching[0]["voteCount"] == 0
    assert email not in listing.text


def test_tc092_posting_an_idea_without_login_is_refused(client: TestClient) -> None:
    title = "Sneaky idea"

    response = client.post(
        "/ideas",
        json={"title": title, "description": "Posted without logging in."},
    )

    assert response.status_code == 401, response.text
    assert all(idea["title"] != title for idea in _board(client))


def test_tc094_idea_with_an_empty_title_is_rejected(client: TestClient) -> None:
    description = "Free coffee on Fridays for everyone."
    tok, _ = _login_as_new_user(client)

    response = client.post(
        "/ideas",
        json={"title": "", "description": description},
        headers=_bearer(tok),
    )

    assert response.status_code == 422, response.text
    assert response.json()["field"] == "title"
    assert all(idea["description"] != description for idea in _board(client))


def test_tc095_idea_with_an_empty_description_is_rejected(client: TestClient) -> None:
    title = "Free coffee Fridays"
    tok, _ = _login_as_new_user(client)

    response = client.post(
        "/ideas",
        json={"title": title, "description": ""},
        headers=_bearer(tok),
    )

    assert response.status_code == 422, response.text
    assert response.json()["field"] == "description"
    assert all(idea["title"] != title for idea in _board(client))


def test_tc098_idea_with_a_title_that_is_too_long_is_rejected(client: TestClient) -> None:
    long_title = "a" * 121
    tok, _ = _login_as_new_user(client)

    response = client.post(
        "/ideas",
        json={"title": long_title, "description": "Short and valid description."},
        headers=_bearer(tok),
    )

    assert response.status_code == 422, response.text
    assert response.json()["field"] == "title"
    assert all(idea["title"] != long_title for idea in _board(client))


def test_tc099_idea_with_a_description_that_is_too_long_is_rejected(
    client: TestClient,
) -> None:
    title = "Long description test"
    tok, _ = _login_as_new_user(client)

    response = client.post(
        "/ideas",
        json={"title": title, "description": "b" * 501},
        headers=_bearer(tok),
    )

    assert response.status_code == 422, response.text
    assert response.json()["field"] == "description"
    assert all(idea["title"] != title for idea in _board(client))


def test_tc102_posting_a_second_idea_does_not_change_the_first_posted_idea(
    client: TestClient,
) -> None:
    first_title = "Bike storage"
    first_desc = "Add a covered rack near the entrance."
    second_title = "Bike lockers"
    second_desc = "Add lockers for helmets too."
    tok, _ = _login_as_new_user(client)

    first = client.post(
        "/ideas",
        json={"title": first_title, "description": first_desc},
        headers=_bearer(tok),
    )
    assert first.status_code == 201, first.text
    second = client.post(
        "/ideas",
        json={"title": second_title, "description": second_desc},
        headers=_bearer(tok),
    )
    assert second.status_code == 201, second.text
    assert second.json()["id"] != first.json()["id"]

    board = _board(client, tok)

    firsts = [idea for idea in board if idea["title"] == first_title]
    seconds = [idea for idea in board if idea["title"] == second_title]
    assert len(firsts) == 1
    assert firsts[0]["id"] == first.json()["id"]
    assert firsts[0]["description"] == first_desc
    assert firsts[0]["voteCount"] == 0
    assert len(seconds) == 1
    assert seconds[0]["id"] == second.json()["id"]
    assert seconds[0]["description"] == second_desc
    assert seconds[0]["voteCount"] == 0

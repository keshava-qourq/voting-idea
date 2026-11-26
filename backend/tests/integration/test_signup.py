"""Sign-up (US-001): POST /auth/signup, proved on the test database."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient


def _local(name: str) -> str:
    """A local part unique to this run: the database may already hold other users."""
    return f"{name}-{uuid4().hex[:10]}"


def _password() -> str:
    return secrets.token_urlsafe(16)


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_tc001_sign_up_with_a_new_email_logs_the_visitor_in(client: TestClient) -> None:
    email = f"{_local('alice')}@example.com"
    password = _password()

    response = client.post("/auth/signup", json={"email": email, "password": password})

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["token"]
    assert body["email"].lower() == email.lower()
    assert password not in response.text

    me = client.get("/auth/me", headers=_bearer(body["token"]))

    assert me.status_code == 200, me.text
    assert me.json()["email"].lower() == email.lower()


def test_tc003_same_email_in_different_letter_case_is_refused(client: TestClient) -> None:
    local = _local("bob")
    email = f"{local}@example.com"
    other_case = f"{local.upper()}@Example.com"
    original_password = _password()
    other_password = _password()

    first = client.post("/auth/signup", json={"email": email, "password": original_password})
    assert first.status_code == 201, first.text

    second = client.post("/auth/signup", json={"email": other_case, "password": other_password})
    assert second.status_code == 409, second.text

    refused = client.post("/auth/login", json={"email": email, "password": other_password})
    assert refused.status_code == 401, refused.text

    accepted = client.post("/auth/login", json={"email": email, "password": original_password})
    assert accepted.status_code == 200, accepted.text


def test_tc005_invalid_email_format_is_rejected(client: TestClient) -> None:
    password = _password()

    response = client.post("/auth/signup", json={"email": "not-an-email", "password": password})

    assert response.status_code == 422, response.text
    assert response.json()["field"] == "email"

    login = client.post("/auth/login", json={"email": "not-an-email", "password": password})
    assert login.status_code == 401, login.text


def test_tc006_empty_password_is_rejected(client: TestClient) -> None:
    email = f"{_local('gina')}@example.com"

    response = client.post("/auth/signup", json={"email": email, "password": ""})

    assert response.status_code == 422, response.text
    assert response.json()["field"] == "password"

    login = client.post("/auth/login", json={"email": email, "password": ""})
    assert login.status_code in (401, 422), login.text


def test_tc009_emails_at_different_domains_are_all_accepted(client: TestClient) -> None:
    first = client.post(
        "/auth/signup",
        json={"email": f"{_local('ivan')}@gmail.com", "password": _password()},
    )
    assert first.status_code == 201, first.text

    second = client.post(
        "/auth/signup",
        json={
            "email": f"{_local('judy')}@small-bakery.example.org",
            "password": _password(),
        },
    )
    assert second.status_code == 201, second.text


def test_tc011_new_account_can_post_an_idea_with_no_verification(client: TestClient) -> None:
    email = f"{_local('liam')}@example.com"

    signup = client.post("/auth/signup", json={"email": email, "password": _password()})
    assert signup.status_code == 201, signup.text
    token = signup.json()["token"]
    assert token

    idea = client.post(
        "/ideas",
        json={"title": "Add dark mode", "description": "A dark theme for night time use"},
        headers=_bearer(token),
    )

    assert idea.status_code in (200, 201), idea.text

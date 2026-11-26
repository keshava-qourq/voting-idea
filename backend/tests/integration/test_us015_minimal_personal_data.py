"""US-015: only the email address is kept as personal data (AC-041, AC-042)."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient

_ALLOWED_USER_KEYS = {"id", "email", "role"}
_ALLOWED_SIGNUP_KEYS = {"token", "userId", "email"}
_CREDENTIAL_WORDS = ("password", "passwd", "hash", "secret", "salt")


def _local(name: str) -> str:
    """A local part unique to this run: the database may already hold other users."""
    return f"{name}-{uuid4().hex[:10]}"


def _pw() -> str:
    return secrets.token_urlsafe(16)


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_tc049_sign_up_keeps_only_the_email_address(client: TestClient) -> None:
    email = f"{_local('alice')}@example.com"
    pw = _pw()

    signup = client.post("/auth/signup", json={"email": email, "password": pw})

    assert signup.status_code == 201, signup.text
    created = signup.json()
    assert created["token"]
    assert created["email"].lower() == email.lower()
    assert set(created) <= _ALLOWED_SIGNUP_KEYS, created
    assert pw not in signup.text

    me = client.get("/auth/me", headers=_bearer(created["token"]))

    assert me.status_code == 200, me.text
    body = me.json()
    assert body["email"].lower() == email.lower()
    assert set(body) <= _ALLOWED_USER_KEYS, body
    for key in body:
        assert not any(word in key.lower() for word in _CREDENTIAL_WORDS), body
    for personal in ("name", "phone", "address", "birthDate", "birthdate", "dateOfBirth"):
        assert personal not in body
    assert pw not in me.text


def test_tc050_sign_up_without_a_password_creates_no_account(client: TestClient) -> None:
    email = f"{_local('dana')}@example.com"
    pw = _pw()

    signup = client.post("/auth/signup", json={"email": email, "password": ""})

    assert signup.status_code == 422, signup.text

    login = client.post("/auth/login", json={"email": email, "password": pw})

    assert login.status_code == 401, login.text


def test_tc053_board_response_hides_other_users_email_addresses(client: TestClient) -> None:
    bob_email = f"{_local('bob')}@example.com"
    alice_email = f"{_local('alice')}@example.com"
    bob_pw = _pw()
    alice_pw = _pw()
    title = f"Add dark mode {uuid4().hex[:8]}"

    bob = client.post("/auth/signup", json={"email": bob_email, "password": bob_pw})
    assert bob.status_code == 201, bob.text
    bob_token = bob.json()["token"]
    assert bob_token

    idea = client.post(
        "/ideas",
        json={"title": title, "description": "A dark theme for evening use."},
        headers=_bearer(bob_token),
    )
    assert idea.status_code in (200, 201), idea.text
    idea_id = str(idea.json()["id"])

    alice = client.post("/auth/signup", json={"email": alice_email, "password": alice_pw})
    assert alice.status_code == 201, alice.text
    alice_token = alice.json()["token"]
    assert alice_token

    visitor_board = client.get("/ideas")

    assert visitor_board.status_code == 200, visitor_board.text
    assert idea_id in {str(i["id"]) for i in visitor_board.json()}
    assert title in {i["title"] for i in visitor_board.json()}
    assert bob_email.lower() not in visitor_board.text.lower()
    assert alice_email.lower() not in visitor_board.text.lower()

    alice_board = client.get("/ideas", headers=_bearer(alice_token))

    assert alice_board.status_code == 200, alice_board.text
    assert idea_id in {str(i["id"]) for i in alice_board.json()}
    assert title in {i["title"] for i in alice_board.json()}
    assert bob_email.lower() not in alice_board.text.lower()
    assert alice_email.lower() not in alice_board.text.lower()

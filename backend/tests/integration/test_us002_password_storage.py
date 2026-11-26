"""Password storage (US-002): passwords are kept only as salted hashes and never shown."""

import hashlib
import logging
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import column, inspect, select, table
from sqlalchemy.orm import Session


def _local(name: str) -> str:
    """A local part unique to this run: the database may already hold other users."""
    return f"{name}-{uuid4().hex[:10]}"


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _stored_passwords(db_session: Session, email: str) -> list[str]:
    """Read the stored password value(s) of the account with this email straight from the
    test database. The API has no endpoint for stored records, so the tables are found
    through the schema: the one with an `email` column and a password column."""
    inspector = inspect(db_session.connection())
    for table_name in inspector.get_table_names():
        names = [c["name"] for c in inspector.get_columns(table_name)]
        if "email" not in names:
            continue
        password_columns = [n for n in names if "password" in n.lower() or "hash" in n.lower()]
        if not password_columns:
            continue
        users = table(table_name, column("email"), *[column(n) for n in password_columns])
        rows = db_session.execute(
            select(*[users.c[n] for n in password_columns]).where(users.c.email.ilike(email))
        ).all()
        return [str(value) for row in rows for value in row if value is not None]
    pytest.fail("No table with an email column and a password column was found")


def _assert_salted_hash(stored: str, password: str) -> None:
    assert stored, "the stored password value is empty"
    assert stored != password
    assert password not in stored
    # A salted hash is not the bare digest of the password...
    data = password.encode()
    for digest in (hashlib.md5, hashlib.sha1, hashlib.sha256, hashlib.sha512):  # noqa: S324
        assert stored.lower() != digest(data).hexdigest()
    # ...and it carries its salt, in a structured value such as `$id$salt$hash`.
    assert "$" in stored or ":" in stored, "the stored value shows no stored salt"
    assert len(stored) > len(password)


def test_tc033_new_account_works_and_is_stored_only_as_a_salted_hash(
    client: TestClient, db_session: Session, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    email = f"{_local('alice')}@example.com"
    password = "Sunny-Day-42!"

    signup = client.post("/auth/signup", json={"email": email, "password": password})
    assert signup.status_code == 201, signup.text
    assert password not in signup.text

    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    assert password not in login.text
    token = login.json()["token"]
    assert token

    me = client.get("/auth/me", headers=_bearer(token))
    assert me.status_code == 200, me.text
    body = me.json()
    assert body["email"].lower() == email.lower()
    assert password not in me.text
    assert not any("password" in key.lower() or "hash" in key.lower() for key in body)

    stored = _stored_passwords(db_session, email)
    assert len(stored) >= 1
    for value in stored:
        assert value not in me.text
        _assert_salted_hash(value, password)

    assert password not in caplog.text


def test_tc034_password_that_differs_only_slightly_is_rejected(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    email = f"{_local('alice')}@example.com"
    password = "Sunny-Day-42!"
    near_match = "sunny-day-42!"

    signup = client.post("/auth/signup", json={"email": email, "password": password})
    assert signup.status_code == 201, signup.text

    response = client.post("/auth/login", json={"email": email, "password": near_match})

    assert response.status_code == 401, response.text
    assert near_match not in response.text
    assert password not in response.text
    assert "token" not in response.text.lower()
    assert near_match not in caplog.text
    assert password not in caplog.text


def test_tc035_two_accounts_with_the_same_password_each_get_their_own_salted_hash(
    client: TestClient, db_session: Session, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    bob = f"{_local('bob')}@example.com"
    carol = f"{_local('carol')}@example.com"
    password = "Shared-Pass-77!"

    first = client.post("/auth/signup", json={"email": bob, "password": password})
    assert first.status_code == 201, first.text
    assert password not in first.text

    second = client.post("/auth/signup", json={"email": carol, "password": password})
    assert second.status_code == 201, second.text
    assert password not in second.text

    bob_login = client.post("/auth/login", json={"email": bob, "password": password})
    assert bob_login.status_code == 200, bob_login.text

    carol_login = client.post("/auth/login", json={"email": carol, "password": password})
    assert carol_login.status_code == 200, carol_login.text

    bob_stored = _stored_passwords(db_session, bob)
    carol_stored = _stored_passwords(db_session, carol)
    assert len(bob_stored) >= 1
    assert len(carol_stored) >= 1
    for value in (*bob_stored, *carol_stored):
        _assert_salted_hash(value, password)
    assert bob_stored != carol_stored
    assert set(bob_stored).isdisjoint(carol_stored)

    assert password not in caplog.text


def test_tc037_no_response_echoes_a_password_including_error_responses(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    local = _local("erin")
    email = f"{local}@example.com"
    other_case = f"{local.upper()}@example.com"
    password = "Green-Hill-31!"
    wrong = "Wrong-Guess-99!"

    signup = client.post("/auth/signup", json={"email": email, "password": password})
    assert signup.status_code == 201, signup.text
    assert password not in signup.text
    token = signup.json()["token"]

    duplicate = client.post("/auth/signup", json={"email": other_case, "password": password})
    assert duplicate.status_code == 409, duplicate.text
    assert password not in duplicate.text

    refused = client.post("/auth/login", json={"email": email, "password": wrong})
    assert refused.status_code == 401, refused.text
    assert wrong not in refused.text
    assert password not in refused.text

    me = client.get("/auth/me", headers=_bearer(token))
    assert me.status_code == 200, me.text
    assert me.json()["email"].lower() == email.lower()
    assert password not in me.text
    assert wrong not in me.text

    ideas = client.get("/ideas", headers=_bearer(token))
    assert ideas.status_code == 200, ideas.text
    assert password not in ideas.text
    assert wrong not in ideas.text
    assert email.lower() not in ideas.text.lower()

    assert password not in caplog.text
    assert wrong not in caplog.text


def test_tc038_invalid_sign_up_requests_do_not_echo_or_log_the_password(
    client: TestClient, db_session: Session, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    password = "Red-Door-64!"

    response = client.post("/auth/signup", json={"email": "not-an-email", "password": password})

    assert response.status_code == 422, response.text
    assert response.json()["field"] == "email"
    assert password not in response.text

    assert _stored_passwords(db_session, "not-an-email") == []
    login = client.post("/auth/login", json={"email": "not-an-email", "password": password})
    assert login.status_code == 401, login.text
    assert password not in login.text

    assert password not in caplog.text

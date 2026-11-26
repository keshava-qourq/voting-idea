"""Sign-up (US-001), one test per criterion."""

import secrets
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User


def _email(domain: str = "example.com") -> str:
    return f"signup-{uuid4().hex[:12]}@{domain}"


def _count(session: Session, email: str) -> int:
    return (
        session.scalar(
            select(func.count()).select_from(User).where(func.lower(User.email) == email.lower())
        )
        or 0
    )


def test_ac001_creates_the_account_and_logs_in(client: TestClient, db_session: Session) -> None:
    email = _email()
    password = secrets.token_urlsafe()

    response = client.post("/auth/signup", json={"email": email, "password": password})

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert body["userId"]
    assert _count(db_session, email) == 1
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == email
    # The password is stored only as a salted hash.
    stored = db_session.scalars(select(User).where(User.email == email)).one()
    assert stored.password_hash != password
    assert password not in response.text
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200


def test_ac002_rejects_a_duplicate_email_ignoring_case(
    client: TestClient, db_session: Session
) -> None:
    email = _email()
    first = client.post("/auth/signup", json={"email": email, "password": secrets.token_urlsafe()})
    assert first.status_code == 201

    again = client.post(
        "/auth/signup", json={"email": email.upper(), "password": secrets.token_urlsafe()}
    )

    assert again.status_code == 409
    assert again.json()["code"] == "EMAIL_ALREADY_REGISTERED"
    assert again.json()["field"] == "email"
    assert _count(db_session, email) == 1


def test_ac003_rejects_an_invalid_email(client: TestClient, db_session: Session) -> None:
    for bad in ["", "no-at-sign", "a@b", "two@@example.com", "spa ce@example.com"]:
        response = client.post(
            "/auth/signup", json={"email": bad, "password": secrets.token_urlsafe()}
        )

        assert response.status_code == 422, bad
        assert response.json()["code"] == "EMAIL_INVALID"
        assert response.json()["field"] == "email"
        assert _count(db_session, bad) == 0


def test_ac003_rejects_an_empty_password(client: TestClient, db_session: Session) -> None:
    email = _email()

    for bad in ["", "   "]:
        response = client.post("/auth/signup", json={"email": email, "password": bad})

        assert response.status_code == 422
        assert response.json()["code"] == "PASSWORD_REQUIRED"
        assert response.json()["field"] == "password"
    assert _count(db_session, email) == 0


def test_ac004_accepts_any_email_domain(client: TestClient) -> None:
    for domain in ["example.com", "gmail.com", "tiny.example.org", "company.co.uk"]:
        response = client.post(
            "/auth/signup", json={"email": _email(domain), "password": secrets.token_urlsafe()}
        )

        assert response.status_code == 201, domain


def test_ac005_needs_no_verification_step(client: TestClient) -> None:
    response = client.post(
        "/auth/signup", json={"email": _email(), "password": secrets.token_urlsafe()}
    )

    token = response.json()["token"]
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200

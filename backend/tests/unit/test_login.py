"""Log in (US-003), one test per criterion."""

import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import SESSION_LIFETIME, USER_ROLE, ensure_user
from app.models import UserSession


def _account(db_session: Session) -> tuple[str, str]:
    email = f"login-{uuid4().hex[:12]}@example.com"
    password = secrets.token_urlsafe()
    ensure_user(db_session, email=email, password=password, role=USER_ROLE)
    return email, password


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_ac008_correct_credentials_log_the_user_in(client: TestClient, db_session: Session) -> None:
    email, password = _account(db_session)

    response = client.post("/auth/login", json={"email": email, "password": password})

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == email
    assert body["user"]["role"] == USER_ROLE
    assert password not in response.text
    me = client.get("/auth/me", headers=_bearer(body["token"]))
    assert me.status_code == 200
    assert me.json()["email"] == email
    assert me.json()["id"] == body["user"]["id"]


def test_ac008_the_email_is_matched_ignoring_letter_case(
    client: TestClient, db_session: Session
) -> None:
    email, password = _account(db_session)

    response = client.post("/auth/login", json={"email": email.upper(), "password": password})

    assert response.status_code == 200


def test_ac008_login_creates_a_session_with_the_set_lifetime(
    client: TestClient, db_session: Session
) -> None:
    email, password = _account(db_session)

    response = client.post("/auth/login", json={"email": email, "password": password})

    user_id = response.json()["user"]["id"]
    stored = db_session.scalars(select(UserSession).where(UserSession.user_id == user_id)).one()
    assert stored.expires_at - stored.created_at == SESSION_LIFETIME


def test_ac009_wrong_password_and_unknown_email_get_the_same_401(
    client: TestClient, db_session: Session
) -> None:
    email, _ = _account(db_session)

    wrong_password = client.post(
        "/auth/login", json={"email": email, "password": secrets.token_urlsafe()}
    )
    stranger = f"nobody-{uuid4().hex[:12]}@example.com"
    unknown_email = client.post(
        "/auth/login", json={"email": stranger, "password": secrets.token_urlsafe()}
    )

    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["code"] == "INVALID_CREDENTIALS"
    assert "token" not in wrong_password.json()


def test_ac009_a_failed_login_starts_no_session(client: TestClient, db_session: Session) -> None:
    email, _ = _account(db_session)
    before = len(db_session.scalars(select(UserSession)).all())

    client.post("/auth/login", json={"email": email, "password": secrets.token_urlsafe()})

    assert len(db_session.scalars(select(UserSession)).all()) == before


def test_ac009_without_a_token_the_profile_is_refused(client: TestClient) -> None:
    for headers in [{}, _bearer("not-a-token")]:
        response = client.get("/auth/me", headers=headers)

        assert response.status_code == 401
        assert response.json()["code"] == "NOT_AUTHENTICATED"


def test_ac010_an_expired_session_is_refused(client: TestClient, db_session: Session) -> None:
    email, password = _account(db_session)
    login = client.post("/auth/login", json={"email": email, "password": password}).json()
    assert client.get("/auth/me", headers=_bearer(login["token"])).status_code == 200

    stored = db_session.scalars(
        select(UserSession).where(UserSession.user_id == login["user"]["id"])
    ).one()
    stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db_session.commit()

    response = client.get("/auth/me", headers=_bearer(login["token"]))
    assert response.status_code == 401
    assert response.json()["code"] == "NOT_AUTHENTICATED"


def test_ac010_a_token_without_a_session_is_refused(
    client: TestClient, db_session: Session
) -> None:
    email, password = _account(db_session)
    login = client.post("/auth/login", json={"email": email, "password": password}).json()
    stored = db_session.scalars(
        select(UserSession).where(UserSession.user_id == login["user"]["id"])
    ).one()
    db_session.delete(stored)
    db_session.commit()

    assert client.get("/auth/me", headers=_bearer(login["token"])).status_code == 401


def test_ac011_no_password_reset_endpoint_is_offered(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert not [path for path in paths if "reset" in path or "forgot" in path]

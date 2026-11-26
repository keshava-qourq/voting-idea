"""Log out (US-004), one test per criterion."""

import secrets
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import USER_ROLE, current_user, ensure_user
from app.database import get_db
from app.main import app
from app.models import User, UserSession


def _login(client: TestClient, db_session: Session) -> dict[str, str]:
    email = f"logout-{uuid4().hex[:12]}@example.com"
    password = secrets.token_urlsafe()
    ensure_user(db_session, email=email, password=password, role=USER_ROLE)
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['token']}"}


def test_ac012_logout_ends_the_session(client: TestClient, db_session: Session) -> None:
    headers = _login(client, db_session)
    assert client.get("/auth/me", headers=headers).status_code == 200

    response = client.post("/auth/logout", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"loggedOut": True}
    assert db_session.scalars(select(UserSession)).all() == []


def test_ac012_logout_ends_only_the_current_session(
    client: TestClient, db_session: Session
) -> None:
    first = _login(client, db_session)
    other = _login(client, db_session)

    client.post("/auth/logout", headers=first)

    assert client.get("/auth/me", headers=other).status_code == 200


def test_ac013_the_token_is_refused_after_logout(client: TestClient, db_session: Session) -> None:
    headers = _login(client, db_session)
    client.post("/auth/logout", headers=headers)

    for response in [
        client.get("/auth/me", headers=headers),
        client.post("/auth/logout", headers=headers),
    ]:
        assert response.status_code == 401
        assert response.json()["code"] == "NOT_AUTHENTICATED"


def test_ac013_a_guarded_route_refuses_a_revoked_or_missing_session(
    client: TestClient, db_session: Session
) -> None:
    guarded = FastAPI()

    @guarded.post("/act")
    def act(user: User = Depends(current_user)) -> dict[str, str]:  # noqa: B008
        return {"email": user.email}

    guarded.dependency_overrides[get_db] = app.dependency_overrides[get_db]
    probe = TestClient(guarded)
    headers = _login(client, db_session)
    assert probe.post("/act", headers=headers).status_code == 200

    client.post("/auth/logout", headers=headers)

    assert probe.post("/act", headers=headers).status_code == 401
    assert probe.post("/act").status_code == 401


def test_ac013_logout_without_a_login_is_refused(client: TestClient) -> None:
    for headers in [{}, {"Authorization": "Bearer not-a-token"}]:
        response = client.post("/auth/logout", headers=headers)

        assert response.status_code == 401
        assert response.json()["code"] == "NOT_AUTHENTICATED"

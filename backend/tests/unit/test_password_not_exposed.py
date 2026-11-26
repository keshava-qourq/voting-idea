"""Passwords stay out of responses and logs (US-002, AC-007)."""

import logging
import secrets

import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_ac007_no_response_schema_has_a_password_field() -> None:
    schemas = app.openapi()["components"]["schemas"]

    for name, schema in schemas.items():
        if name.endswith("Request"):
            continue
        for prop in schema.get("properties", {}):
            assert "password" not in prop.lower(), f"{name}.{prop}"


def test_ac007_responses_never_carry_the_password(client: TestClient) -> None:
    email = f"expose-{secrets.token_hex(6)}@example.com"
    password = secrets.token_urlsafe()

    signup = client.post("/auth/signup", json={"email": email, "password": password})
    token = signup.json()["token"]
    login = client.post("/auth/login", json={"email": email, "password": password})
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    wrong = client.post("/auth/login", json={"email": email, "password": password + "x"})
    bad_email = client.post("/auth/signup", json={"email": "nope", "password": password})

    for response in (signup, login, me, wrong, bad_email):
        assert password not in response.text
        assert "passwordHash" not in response.text
        assert "password_hash" not in response.text


def test_ac007_no_password_is_written_to_the_log(
    client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    email = f"logs-{secrets.token_hex(6)}@example.com"
    password = secrets.token_urlsafe()

    with caplog.at_level(logging.DEBUG):
        client.post("/auth/signup", json={"email": email, "password": password})
        client.post("/auth/signup", json={"email": email, "password": password})
        client.post("/auth/login", json={"email": email, "password": password})
        client.post("/auth/login", json={"email": email, "password": password + "x"})

    assert password not in caplog.text

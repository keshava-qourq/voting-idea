"""Salted password hashing (US-002, AC-006)."""

import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import USER_ROLE, ensure_user, hash_password, verify_password
from app.models import User


def test_ac006_hash_differs_from_the_plain_password() -> None:
    password = secrets.token_urlsafe()

    hashed = hash_password(password)

    assert hashed != password
    assert password not in hashed


def test_ac006_hash_is_salted() -> None:
    password = secrets.token_urlsafe()

    first = hash_password(password)
    second = hash_password(password)

    assert first != second
    assert first.startswith("$2")
    assert verify_password(password, first)
    assert verify_password(password, second)


def test_ac006_a_wrong_password_does_not_verify() -> None:
    hashed = hash_password(secrets.token_urlsafe())

    assert not verify_password(secrets.token_urlsafe(), hashed)
    assert not verify_password("anything", "not-a-hash")


def test_ac006_the_stored_account_record_holds_only_a_salted_hash(db_session: Session) -> None:
    email = f"hash-{secrets.token_hex(6)}@example.com"
    password = secrets.token_urlsafe()

    assert ensure_user(db_session, email=email, password=password, role=USER_ROLE)

    stored = db_session.scalars(select(User).where(User.email == email)).one()
    assert stored.password_hash != password
    assert password not in stored.password_hash
    assert stored.password_hash.startswith("$2")
    assert verify_password(password, stored.password_hash)
    assert not hasattr(stored, "password")

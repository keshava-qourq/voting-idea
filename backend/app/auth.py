"""Sign-in: an email and a password in, a bearer token out.

Part of the scaffold's test kit, so the seed script, the signed-in test client and the
smoke check have a real login from the first commit. The frontend and the API are on
different origins once deployed, so the token travels in the response body and comes back
as `Authorization: Bearer <token>`, never as a cookie.

A token names a session row (table `sessions`). The row ends at its expiry, so a token whose
session has expired is refused even when the token itself is still well formed.

JWT_SECRET_KEY signs the tokens. Without it (local runs, tests) a random key is made per
process, so tokens stop working on restart: fine anywhere except a deployed app, where the
platform always sets it.
"""

import os
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any
from uuid import uuid4

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import errors
from app.database import get_db
from app.models import User, UserSession

ADMIN_ROLE = "admin"
USER_ROLE = "user"
SESSION_LIFETIME = timedelta(hours=12)

_ALGORITHM = "HS256"
_SECRET = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
bearer = HTTPBearer(auto_error=False)
_EMAIL_FORMAT = re.compile(r"[^@\s]+@[^@\s.]+(\.[^@\s.]+)+")
_EMAIL_MAX_LENGTH = 255
# The users table may come from the approved data model, so its key is read, not assumed:
# an integer key is made by the database, a text key here.
_KEY_COLUMN = User.__mapper__.primary_key[0]
_KEY = User.__mapper__.get_property_by_column(_KEY_COLUMN).key


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:  # not a bcrypt hash
        return False


def find_user(session: Session, email: str) -> User | None:
    """The user with this email, ignoring letter case."""
    return session.scalars(select(User).where(func.lower(User.email) == email.lower())).first()


def ensure_user(session: Session, *, email: str, password: str, role: str) -> bool:
    """Create the user unless one with this email exists. True when it was created."""
    if find_user(session, email) is not None:
        return False
    values: dict[str, Any] = {
        "email": email,
        "password_hash": hash_password(password),
        "role": role,
    }
    if _KEY_COLUMN.type.python_type is str:
        values[_KEY] = str(uuid4())
    session.add(User(**values))
    session.flush()
    return True


class SignupError(Exception):
    """A sign-up the logic refuses: the error code and the request field to correct."""

    def __init__(self, error: errors.ApiError, field: str) -> None:
        super().__init__(error.message)
        self.error = error
        self.field = field


def create_account(session: Session, *, email: str, password: str) -> User:
    """Validate, then create a user with a salted password hash. Any email domain is accepted.

    No verification step: the caller logs the new user in with `issue_token` at once.
    """
    email = email.strip()
    if len(email) > _EMAIL_MAX_LENGTH or not _EMAIL_FORMAT.fullmatch(email):
        raise SignupError(errors.EMAIL_INVALID, "email")
    if not password.strip():
        raise SignupError(errors.PASSWORD_REQUIRED, "password")
    taken = SignupError(errors.EMAIL_ALREADY_REGISTERED, "email")
    try:
        with session.begin_nested():
            created = ensure_user(session, email=email, password=password, role=USER_ROLE)
    except IntegrityError:  # a concurrent sign-up with the same email won the race
        raise taken from None
    if not created:
        raise taken
    session.commit()
    user = find_user(session, email)
    assert user is not None
    return user


def issue_token(session: Session, user: User) -> str:
    """Start a session for the user, and return the token that names it."""
    now = datetime.now(UTC)
    expires_at = now + SESSION_LIFETIME
    session_id = str(uuid4())
    user_key = getattr(user, _KEY)
    session.add(
        UserSession(id=session_id, user_id=str(user_key), created_at=now, expires_at=expires_at)
    )
    session.commit()
    claims = {
        "sub": str(user_key),
        "sid": session_id,
        "role": user.role,
        "iat": now,
        "exp": expires_at,
    }
    return jwt.encode(claims, _SECRET, algorithm=_ALGORITHM)


def _live_session(
    session: Session, credentials: HTTPAuthorizationCredentials | None
) -> tuple[User, UserSession] | None:
    """The user and the live session row the token names, or None (missing, invalid, expired)."""
    if credentials is None:
        return None
    try:
        claims = jwt.decode(credentials.credentials, _SECRET, algorithms=[_ALGORITHM])
        key = _KEY_COLUMN.type.python_type(claims["sub"])
        session_id = str(claims["sid"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None
    login = session.get(UserSession, session_id)
    if login is None or str(login.user_id) != str(key) or login.expires_at <= datetime.now(UTC):
        return None
    user = session.get(User, key)
    if user is None:
        return None
    return user, login


def user_of_token(
    session: Session, credentials: HTTPAuthorizationCredentials | None
) -> User | None:
    """The user whose live session the token names, or None (missing, invalid or expired)."""
    found = _live_session(session, credentials)
    return found[0] if found else None


def revoke_token(session: Session, credentials: HTTPAuthorizationCredentials | None) -> bool:
    """End the session the token names, at once. False when it names no live session.

    The session row is deleted, so the token is refused from then on, back button or not.
    """
    found = _live_session(session, credentials)
    if found is None:
        return False
    session.delete(found[1])
    session.commit()
    return True


def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_db)],
) -> User:
    """The signed-in user. Add `Depends(current_user)` to any route that needs one."""
    user = user_of_token(session, credentials)
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            errors.NOT_AUTHENTICATED.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

"""Sign-up, login and current-user routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app import errors
from app.auth import (
    SignupError,
    bearer,
    create_account,
    find_user,
    issue_token,
    revoke_token,
    user_of_token,
    verify_password,
)
from app.database import get_db
from app.schemas import (
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    SignupRequest,
    SignupResponse,
    UserRead,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _error(error: errors.ApiError) -> JSONResponse:
    content = ErrorResponse(code=error.code, message=error.message)
    return JSONResponse(status_code=error.status, content=content.model_dump(by_alias=True))


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SignupResponse,
    responses={
        errors.EMAIL_ALREADY_REGISTERED.status: {
            "model": ErrorResponse,
            "description": errors.EMAIL_ALREADY_REGISTERED.message,
        },
        errors.EMAIL_INVALID.status: {
            "model": ErrorResponse,
            "description": f"{errors.EMAIL_INVALID.message} {errors.PASSWORD_REQUIRED.message}",
        },
    },
)
def signup(
    body: SignupRequest, session: Annotated[Session, Depends(get_db)]
) -> SignupResponse | JSONResponse:
    """Create an account and log in immediately. Any email domain is accepted."""
    try:
        user = create_account(session, email=body.email, password=body.password)
    except SignupError as refused:
        content = ErrorResponse(
            code=refused.error.code, message=refused.error.message, field=refused.field
        )
        return JSONResponse(
            status_code=refused.error.status, content=content.model_dump(by_alias=True)
        )
    return SignupResponse(token=issue_token(session, user), user_id=str(user.id), email=user.email)


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        errors.INVALID_CREDENTIALS.status: {
            "model": ErrorResponse,
            "description": errors.INVALID_CREDENTIALS.message,
        },
    },
)
def login(
    body: LoginRequest, session: Annotated[Session, Depends(get_db)]
) -> LoginResponse | JSONResponse:
    """Log in with email and password. An unknown email and a wrong password get the same 401."""
    user = find_user(session, body.email.strip())
    if user is None or not verify_password(body.password, user.password_hash or ""):
        return _error(errors.INVALID_CREDENTIALS)
    return LoginResponse(
        token=issue_token(session, user),
        user=UserRead(id=str(user.id), email=user.email, role=user.role),
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={
        errors.NOT_AUTHENTICATED.status: {
            "model": ErrorResponse,
            "description": errors.NOT_AUTHENTICATED.message,
        },
    },
)
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_db)],
) -> LogoutResponse | JSONResponse:
    """End the current session at once: its token stops working for every later request."""
    if not revoke_token(session, credentials):
        return _error(errors.NOT_AUTHENTICATED)
    return LogoutResponse(logged_out=True)


@router.get(
    "/me",
    response_model=UserRead,
    responses={
        errors.NOT_AUTHENTICATED.status: {
            "model": ErrorResponse,
            "description": errors.NOT_AUTHENTICATED.message,
        },
    },
)
def me(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_db)],
) -> UserRead | JSONResponse:
    """The current user. A missing, invalid or expired session gets a 401."""
    user = user_of_token(session, credentials)
    if user is None:
        return _error(errors.NOT_AUTHENTICATED)
    return UserRead(id=str(user.id), email=user.email, role=user.role)

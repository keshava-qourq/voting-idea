"""Sign-up route."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app import errors
from app.auth import SignupError, create_account, issue_token
from app.database import get_db
from app.schemas import ErrorResponse, SignupRequest, SignupResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


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
    return SignupResponse(token=issue_token(user), user_id=str(user.id), email=user.email)

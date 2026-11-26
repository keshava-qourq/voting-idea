"""The idea board: list ideas by votes, post an idea, upvote an idea."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import errors
from app.api_model import ApiModel
from app.auth import bearer, current_user, user_of_token
from app.database import get_db
from app.models import Idea, User, Vote
from app.schemas import ErrorResponse, IdeaRead

router = APIRouter(prefix="/ideas", tags=["Ideas"])

TITLE_MAX_LENGTH = 120
DESCRIPTION_MAX_LENGTH = 500

TITLE_REQUIRED = errors.ApiError("TITLE_REQUIRED", 422, "Enter a title.")
TITLE_TOO_LONG = errors.ApiError(
    "TITLE_TOO_LONG", 422, f"The title can have at most {TITLE_MAX_LENGTH} characters."
)
DESCRIPTION_REQUIRED = errors.ApiError("DESCRIPTION_REQUIRED", 422, "Enter a description.")
DESCRIPTION_TOO_LONG = errors.ApiError(
    "DESCRIPTION_TOO_LONG",
    422,
    f"The description can have at most {DESCRIPTION_MAX_LENGTH} characters.",
)
IDEA_NOT_FOUND = errors.ApiError("IDEA_NOT_FOUND", 404, "This idea does not exist.")


class IdeaCreate(ApiModel):
    # Plain strings with defaults: the logic checks them and names the field to correct.
    title: str = ""
    description: str = ""


class VoteResponse(ApiModel):
    idea_id: str
    vote_count: int
    voted: bool


def _error(error: errors.ApiError, field: str | None = None) -> JSONResponse:
    content = ErrorResponse(code=error.code, message=error.message, field=field)
    return JSONResponse(status_code=error.status, content=content.model_dump(by_alias=True))


def _vote_count(session: Session, idea_id: str) -> int:
    return session.scalar(select(func.count(Vote.id)).where(Vote.idea_id == idea_id)) or 0


@router.get("", response_model=list[IdeaRead])
def list_ideas(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    session: Annotated[Session, Depends(get_db)],
) -> list[IdeaRead]:
    """Public board, most votes first, ties newest first. Never shows author emails."""
    count = func.count(Vote.id)
    rows = session.execute(
        select(Idea, count)
        .outerjoin(Vote, Vote.idea_id == Idea.id)
        .group_by(Idea.id)
        .order_by(count.desc(), Idea.created_at.desc(), Idea.id)
    ).all()
    user = user_of_token(session, credentials)
    voted_ids: set[str] = set()
    if user is not None:
        voted_ids = set(session.scalars(select(Vote.idea_id).where(Vote.user_id == user.id)))
    return [
        IdeaRead(
            id=idea.id,
            title=idea.title,
            description=idea.description,
            vote_count=votes,
            created_at=idea.created_at,
            voted=idea.id in voted_ids,
        )
        for idea, votes in rows
    ]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=IdeaRead,
    responses={422: {"model": ErrorResponse}},
)
def post_idea(
    body: IdeaCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> IdeaRead | JSONResponse:
    """Post an idea with zero votes. Logged-in users only."""
    title = body.title.strip()
    description = body.description.strip()
    if not title:
        return _error(TITLE_REQUIRED, "title")
    if len(title) > TITLE_MAX_LENGTH:
        return _error(TITLE_TOO_LONG, "title")
    if not description:
        return _error(DESCRIPTION_REQUIRED, "description")
    if len(description) > DESCRIPTION_MAX_LENGTH:
        return _error(DESCRIPTION_TOO_LONG, "description")
    idea = Idea(
        id=str(uuid4()),
        user_id=user.id,
        title=title,
        description=description,
        created_at=datetime.now(UTC),
    )
    session.add(idea)
    session.commit()
    return IdeaRead(
        id=idea.id,
        title=idea.title,
        description=idea.description,
        vote_count=0,
        created_at=idea.created_at,
        voted=False,
    )


@router.post(
    "/{idea_id}/vote",
    response_model=VoteResponse,
    responses={404: {"model": ErrorResponse}},
)
def vote(
    idea_id: str,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[Session, Depends(get_db)],
) -> VoteResponse | JSONResponse:
    """Upvote an idea. A repeat vote by the same user changes nothing."""
    if session.get(Idea, idea_id) is None:
        return _error(IDEA_NOT_FOUND)
    existing = session.scalar(
        select(Vote.id).where(Vote.user_id == user.id, Vote.idea_id == idea_id)
    )
    if existing is None:
        try:
            with session.begin_nested():
                session.add(
                    Vote(
                        id=str(uuid4()),
                        user_id=user.id,
                        idea_id=idea_id,
                        created_at=datetime.now(UTC),
                    )
                )
        except IntegrityError:  # the same vote arrived at the same time: it counts once
            pass
        session.commit()
    return VoteResponse(idea_id=idea_id, vote_count=_vote_count(session, idea_id), voted=True)

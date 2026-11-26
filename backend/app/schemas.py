"""Pydantic request and response models.

One pair per entity in the approved data model, plus the placeholder every
generated route returns until it has been implemented. Every model is an ApiModel,
so its JSON uses camelCase names (app/api_model.py).
"""

from app.api_model import ApiModel


class StubResponse(ApiModel):
    """What a generated route returns until someone implements it.

    A stub that returns a typed body rather than raising keeps the service
    startable and its OpenAPI document complete, so the frontend can be built
    against the agreed shape while the handlers are still being written.
    """

    endpoint: str
    status: str = "not_implemented"
    detail: str = "Scaffolded from the approved API spec; no behaviour yet."


class ErrorResponse(ApiModel):
    """Body of every error an endpoint returns on purpose."""

    code: str
    message: str
    # The request field that needs correcting (email or password), when there is one.
    field: str | None = None


class SignupRequest(ApiModel):
    # Plain strings: the logic checks them and answers with an error code that names the field.
    email: str
    password: str


class SignupResponse(ApiModel):
    """The new account and the token that logs it in at once."""

    token: str
    user_id: str
    email: str


class UserCreate(ApiModel):
    email: str
    role: str


class UserRead(ApiModel):
    id: str
    email: str
    role: str


class LoginRequest(ApiModel):
    # Plain strings: a wrong or unknown pair gets the same generic 401, whatever its shape.
    email: str
    password: str


class LogoutResponse(ApiModel):
    """Confirms the session token no longer works."""

    logged_out: bool


class LoginResponse(ApiModel):
    """The session token and the user it belongs to."""

    # "token", not "access_token": one word reads the same in camelCase, and it is a name
    # the platform's smoke check looks for.
    token: str
    user: UserRead

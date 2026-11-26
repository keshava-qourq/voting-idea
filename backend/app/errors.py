"""Error codes the endpoints return: one constant per error, with its HTTP status and message."""

from typing import NamedTuple


class ApiError(NamedTuple):
    code: str
    status: int
    message: str


EMAIL_INVALID = ApiError("EMAIL_INVALID", 422, "Enter a valid email address.")
PASSWORD_REQUIRED = ApiError("PASSWORD_REQUIRED", 422, "Enter a password.")
INVALID_CREDENTIALS = ApiError("INVALID_CREDENTIALS", 401, "Wrong email or password.")
NOT_AUTHENTICATED = ApiError("NOT_AUTHENTICATED", 401, "Sign in first.")
EMAIL_ALREADY_REGISTERED = ApiError(
    "EMAIL_ALREADY_REGISTERED", 409, "This email is already registered."
)
TITLE_REQUIRED = ApiError("TITLE_REQUIRED", 422, "Enter a title.")
TITLE_TOO_LONG = ApiError("TITLE_TOO_LONG", 422, "The title can have at most 120 characters.")
DESCRIPTION_REQUIRED = ApiError("DESCRIPTION_REQUIRED", 422, "Enter a description.")
DESCRIPTION_TOO_LONG = ApiError(
    "DESCRIPTION_TOO_LONG", 422, "The description can have at most 500 characters."
)
IDEA_NOT_FOUND = ApiError("IDEA_NOT_FOUND", 404, "This idea does not exist.")

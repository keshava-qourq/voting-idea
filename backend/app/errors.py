"""Error codes the endpoints return: one constant per error, with its HTTP status and message."""

from typing import NamedTuple


class ApiError(NamedTuple):
    code: str
    status: int
    message: str


EMAIL_INVALID = ApiError("EMAIL_INVALID", 422, "Enter a valid email address.")
PASSWORD_REQUIRED = ApiError("PASSWORD_REQUIRED", 422, "Enter a password.")
EMAIL_ALREADY_REGISTERED = ApiError(
    "EMAIL_ALREADY_REGISTERED", 409, "This email is already registered."
)

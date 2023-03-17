from fastapi import HTTPException
from fastapi_sessions.frontends.implementations import CookieParameters
from src.backend.database import engine
from src.backend.sessions import SQLBackend, FastSessionVerifier, FastSessionCookie
from os import environ

cookie_params = CookieParameters()
"""Cookie parameters."""

# Uses UUID
cookie = FastSessionCookie(
    cookie_name=environ.get("SESSION_COOKIE_NAME"),
    identifier=environ.get("SESSION_IDENTIFIER"),
    auto_error=True,
    secret_key=environ.get("SESSION_SECRET_KEY"),
    cookie_params=cookie_params,
)
"""Session cookie."""

backend = SQLBackend(engine)
"""Session backend."""

verifier = FastSessionVerifier(
    identifier=environ.get("SESSION_IDENTIFIER"),
    auto_error=True,
    backend=backend,
    auth_http_exception=HTTPException(status_code=403, detail="Invalid session"),
)
"""Session verifier."""

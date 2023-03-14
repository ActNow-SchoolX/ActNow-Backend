from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException, Request
from fastapi_sessions.frontends.implementations import SessionCookie
from fastapi_sessions.frontends.session_frontend import FrontendError, ID
from fastapi_sessions.session_verifier import SessionVerifier, SessionBackend
from itsdangerous import BadSignature, SignatureExpired
from pydantic import validator
from sqlmodel import SQLModel, Session, Field
from uuid import UUID, uuid4
from os import environ


def get_expiration(
        delta: timedelta = timedelta(minutes=int(environ.get('SESSION_MINUTES_TO_LIVE')))
) -> float:
    """Get expiration time in seconds from now.

    Args:
        delta (timedelta, optional): Time delta. Defaults to timedelta(minutes=5).

    Returns:
        float: Expiration time in seconds from now.
    """
    return (datetime.now() + delta).timestamp()


class FastSessionCookie(SessionCookie):
    def get_last_cookie(self, request: Request) -> Union[UUID, FrontendError]:
        signed_session_id = request.cookies.get(self.model.name)

        if not signed_session_id:
            error = FrontendError("No session cookie attached to request")
            super().attach_id_state(request, error)
            return error

        # Verify and timestamp the signed session id
        try:
            session_id = UUID(
                self.signer.loads(
                    signed_session_id,
                    max_age=self.cookie_params.max_age,
                    return_timestamp=False,
                )
            )
        except (SignatureExpired, BadSignature):
            error = FrontendError("Session cookie has invalid signature")
            super().attach_id_state(request, error)
            return error

        super().attach_id_state(request, session_id)
        return session_id


class SessionData(SQLModel, table=True):
    """Session data model.

    Args:
        SQLModel (SQLModel): SQLModel base class.

    Attributes:
        uuid (UUID): Session UUID.
        user_id (int): User ID.
        nickname (str): User nickname.
        expires_in (float): Expiration time in seconds from now.

    Raises:
        ValueError: If user_id is not positive.
        ValueError: If nickname is empty.

    Returns:
        SessionData: Session data model.
    """
    __tablename__ = "sessions"
    uuid: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int
    nickname: str
    expires_in: float = Field(default_factory=get_expiration)

    @validator("user_id")
    def user_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("user_id must be positive")
        return v

    @validator("nickname")
    def nickname_must_be_nonempty(cls, v):
        if len(v) == 0:
            raise ValueError("nickname must be nonempty")
        return v


# create sql backend for sessions
class SQLBackend(SessionBackend):
    """SQL backend for sessions.

    Args:
        SessionBackend (SessionBackend): Session backend base class.

    Attributes:
        engine (Engine): SQLAlchemy engine.

    Returns:
        SQLBackend: SQL backend for sessions.
        """
    def __init__(self, _engine):
        self.engine = _engine

    async def create(self, session_id: UUID, data: SessionData) -> None:
        """Create session.

        Args:
            session_id (UUID): Session UUID.
            data (SessionData): Session data.
        """
        with Session(self.engine) as session:
            session.add(data)
            session.commit()
            session.refresh(data)

    async def read(self, session_id: UUID) -> SessionData | None:
        """Read session.

        Args:
            session_id (UUID): Session UUID.

        Returns:
            SessionData | None: Session data.
        """
        with Session(self.engine) as session:
            return session.get(SessionData, session_id)

    async def update(self, session_id: UUID, data: SessionData) -> None:
        """Update session.

        Args:
            session_id (UUID): Session UUID.
            data (SessionData): Session data.

        Returns:
            SessionData | None: Session data.
        """
        with Session(self.engine) as session:
            session.add(data)
            session.commit()
            session.refresh(data)

    async def delete(self, session_id: UUID) -> None:
        """Delete session.

        Args:
            session_id (UUID): Session UUID.

        Returns:
            SessionData | None: Session data.
        """
        with Session(self.engine) as session:
            data = session.get(SessionData, session_id)
            session.delete(data)
            session.commit()


class FastSessionVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: SessionBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        """Basic session verifier.

        Attributes:
            identifier (str): Session identifier.
            auto_error (bool): Auto error.
            backend (SessionBackend[UUID, SessionData]): Session backend.
            auth_http_exception (HTTPException): Auth HTTP exception.

        Returns:
            FastSessionVerifier: Basic session verifier.
        """
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    async def get_last_session(self, request: Request):
        try:
            session_id: Union[ID, FrontendError] = request.state.session_ids[
                self.identifier
            ]
        except Exception:
            return None

        if isinstance(session_id, FrontendError):
            return None

        session_data = await self.backend.read(session_id)
        if not session_data or not self.verify_session(session_data):
            if self.auto_error:
                raise self.auth_http_exception
            return None

        return session_data

    def verify_session(self, model: SessionData) -> bool:
        """Verify session.

        Args:
            model (SessionData): Session data.

        Returns:
            bool: True if session is valid, False otherwise.
        """
        # check if session is expired
        if model.expires_in <= datetime.now().timestamp():
            return False

        return True

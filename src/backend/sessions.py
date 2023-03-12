from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi_sessions.session_verifier import SessionVerifier, SessionBackend
from pydantic import validator
from sqlmodel import SQLModel, Session, Field
from uuid import UUID, uuid4


def get_expiration(delta: timedelta = timedelta(minutes=5)) -> float:
    """Get expiration time in seconds from now.

    Args:
        delta (timedelta, optional): Time delta. Defaults to timedelta(minutes=5).

    Returns:
        float: Expiration time in seconds from now.
    """
    return (datetime.now() + delta).timestamp()


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


class BasicVerifier(SessionVerifier[UUID, SessionData]):
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
            BasicVerifier: Basic session verifier.
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

    def verify_session(self, model: SessionData) -> bool:
        """Verify session.

        Args:
            model (SessionData): Session data.

        Returns:
            bool: True if session is valid, False otherwise.
        """
        # check if session is existing in the database
        if self._backend.read(model.uuid) is None:
            return False

        # check if session is expired
        if model.expires_in <= datetime.now().timestamp():
            # delete if expired
            self._backend.delete(model.uuid)
            return False

        return True

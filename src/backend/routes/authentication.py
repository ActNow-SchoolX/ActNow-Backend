from fastapi import Depends, APIRouter, HTTPException
from fastapi.openapi.models import Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, validator
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import User
from src.backend.dependencies import cookie, backend, verifier
from src.backend.internals.users import get_password_hash
from src.backend.sessions import SessionData

app = APIRouter()
security = HTTPBasic()


class UserAuth(BaseModel):
    nickname = str
    password = str

def verify_credentials(nickname: str, password: str) -> User | HTTPException:
    with Session(engine) as session:
        user = User.get_by_nickname(session, nickname)
        if user is None:
            return HTTPException(status_code=401, detail="Invalid username or password")
        if get_password_hash(password) != user.password:
            return HTTPException(status_code=401, detail="Invalid username or password")

    return user



@app.post("/login", dependencies=[Depends(cookie.get_last_cookie)])
async def login(
        response: Response,
        credentials: HTTPBasicCredentials = Depends(app_security),
        old_session: SessionData | None = Depends(verifier.get_last_session),
):
    if old_session is not None:
        return {"message": "Already logged in"}

    user = verify_credentials(credentials.username, credentials.password)

    if isinstance(user, HTTPException):
        raise user

    session = SessionData(user_id=user.id, nickname=user.nickname)

    await backend.create(session.uuid, session)

    cookie.attach_to_response(response, session.uuid)

    return {"message": "Logged in"}

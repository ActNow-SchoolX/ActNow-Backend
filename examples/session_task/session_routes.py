from fastapi import FastAPI, Depends, Response
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.exceptions import HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from src.backend.sessions import SessionData
from src.backend.dependencies import cookie, backend, verifier
from src.backend.database import engine
from src.backend.database.orm import User, UserMetadata

app = FastAPI()
app_security = HTTPBasic()

# Create table
User.metadata.create_all(engine)


class UserRequest(BaseModel):
    nickname: str
    password: str
    photo: str


class UserResponse(BaseModel):
    id: int
    nickname: str


def register_fake_user() -> User:
    with Session(engine) as session:
        user = User(nickname="user1", password="password1")

        if user_ := User.get_by_nickname(session, 'user1') is not None:
            return user_

        session.add(user)
        session.commit()
        session.refresh(user)

        user_metadata = UserMetadata(
            user_id=user.id,
            photo='https://example.com/photo.jpg',
            description='This is a fake user'
        )

        session.add(user_metadata)
        session.commit()
        session.refresh(user_metadata)

        return user


def register_new_user(nickname, password, photo) -> User:
    with Session(engine) as session:
        user = User(
            nickname=nickname,
            password=password
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


def verify_credentials(nickname: str, password: str) -> User | HTTPException:
    with Session(engine) as session:
        user = User.get_by_nickname(session, nickname)
        if user is None:
            return HTTPException(status_code=401, detail="Invalid username or password")
        if password != user.password:
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


@app.get("/me", dependencies=[Depends(cookie)], response_model=UserResponse)
async def me(session: SessionData = Depends(verifier)):
    with Session(engine) as ass:
        user = User.get_by_id(ass, _id=session.user_id)

        return user

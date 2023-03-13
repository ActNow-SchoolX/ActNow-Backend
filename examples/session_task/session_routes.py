from fastapi import FastAPI, Depends, Response
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.exceptions import HTTPException
from sqlmodel import Session
from pydantic import Field, BaseModel

from src.backend.sessions import SessionData
from src.backend.dependencies import cookie, backend, verifier
from src.backend.database import engine
from src.backend.database.orm import User, UserMetadata

app = FastAPI()
app_security = HTTPBasic()

# Create table
User.metadata.create_all(engine)


class UserResponse(BaseModel):
    id: int
    nickname: str
    metadata: UserMetadata


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


def verify_credentials(nickname: str, password: str) -> User | HTTPException:
    with Session(engine) as session:
        user = User.get_by_nickname(session, nickname)
        if user is None:
            return HTTPException(status_code=401, detail="Invalid username or password")
        if password != user.password:
            return HTTPException(status_code=401, detail="Invalid username or password")

    return user


@app.post('/login')
async def login(
        response: Response,
        credentials: HTTPBasicCredentials = Depends(app_security)
) -> dict:
    register_fake_user()

    user = verify_credentials(credentials.username, credentials.password)

    if isinstance(user, HTTPException):
        raise user

    # create session
    session_data = SessionData(
        user_id=user.id,
        nickname=user.nickname
    )

    await backend.create(session_data.uuid, session_data)
    cookie.attach_to_response(response, session_data.uuid)

    return {"success": True, "message": "Logged in successfully!"}


@app.get('/user',
         dependencies=[Depends(cookie)],
         response_model=UserResponse
         )
async def get_user(session_data: SessionData = Depends(verifier)):
    # get user from database
    with Session(engine) as session:
        user = User.get_by_id(session, session_data.user_id)

        print(user.user_metadata)

        return UserResponse(
            id=user.id,
            nickname=user.nickname,
            metadata=user.user_metadata[0]
        )


@app.post('/logout')
async def logout(response: Response, session_uuid: SessionData = Depends(cookie)) -> dict:
    await backend.delete(session_uuid)
    cookie.delete_from_response(response)

    return {"success": True, "message": "Logged out successfully!"}

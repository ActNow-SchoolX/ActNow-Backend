from typing import Union
from uuid import UUID

from fastapi import FastAPI, Depends, Request, Response
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.exceptions import HTTPException
from fastapi_sessions.frontends.session_frontend import ID, FrontendError
from itsdangerous import SignatureExpired, BadSignature
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


def get_session_id(request: Request, some_var: str = 'var') -> Union[UUID, FrontendError, BadSignature]:
        signed_session_id = request.cookies.get(cookie.model.name)

        if not signed_session_id:
            error = FrontendError("No session cookie attached to request")
            cookie.attach_id_state(request, error)
            return error

        # Verify and timestamp the signed session id
        try:
            session_id = UUID(
                cookie.signer.loads(
                    signed_session_id,
                    max_age=cookie.cookie_params.max_age,
                    return_timestamp=False,
                )
            )
        except (SignatureExpired, BadSignature):
            error = BadSignature("Session cookie has invalid signature")
            cookie.attach_id_state(request, error)
            return error

        cookie.attach_id_state(request, session_id)
        return session_id


async def get_current_session(request: Request):
    try:
        session_id: Union[ID, FrontendError, BadSignature] = request.state.session_ids[
            verifier.identifier
        ]
    except Exception:
        return None

    if isinstance(session_id, FrontendError):
        return None

    if isinstance(session_id, BadSignature):
        if verifier.auto_error:
            raise session_id

    session_data = await verifier.backend.read(session_id)
    if not session_data or not verifier.verify_session(session_data):
        if verifier.auto_error:
            raise verifier.auth_http_exception
        return None

    return session_data


@app.post('/login', dependencies=[Depends(get_session_id)])
async def login(
        response: Response,
        credentials: HTTPBasicCredentials = Depends(app_security),
        old_session=Depends(get_current_session)
) -> dict:
    register_fake_user()

    user = verify_credentials(credentials.username, credentials.password)

    if isinstance(user, HTTPException):
        raise user

    print(old_session)
    if old_session is not None:
        return {"success": False, "message": "Already logged in!"}

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


@app.post('/register')
def register(user: UserRequest):
    new_user = register_new_user(user.nickname, user.password, user.photo)

    return UserResponse(nickname=new_user.nickname, id=new_user.id)


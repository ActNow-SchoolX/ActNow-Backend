from typing import Annotated

from fastapi import UploadFile, APIRouter, HTTPException, Depends, Form
from src.backend.internals.users import (
    UserRequest,
    UserResponse,
    UserPatchRequest,
    UserPatchResponse,
    get_password_hash,
    validate_photo,
    user_registrate,
    user_metadata_create,
)
from pathlib import Path
from uuid import uuid4

from sqlmodel import Session
from src.backend.database import engine
from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData
from src.backend.database.orm import User, UserMetadata
from src.backend.routes.nickname_validation import validate_nickname

app = APIRouter()


@app.post('/users', response_model=UserResponse, status_code=201)
def post_user(item: UserRequest):
    item.password = get_password_hash(item.password)

    new_user = user_registrate(item)

    new_user_metadata = user_metadata_create(item, new_user.id)

    return UserResponse(id=new_user.id,
                        nickname=new_user.nickname,
                        profile_photo=new_user_metadata.photo,
                        profile_description=new_user_metadata.description)


@app.post('/user/upload_file')
def post_photo(file: UploadFile | None = None):
    if validate_photo(file.content_type, file.size):
        ...
    else:

        raise HTTPException(
            status_code=400,
            detail='Загружаемый файл не соответствует условиям'
        )

    filename = f'{str(uuid4())}.{file.filename.split(".")[-1]}'

    upload_dir = Path(__file__).parent.parent.parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / filename

    with file_path.open("wb+") as file_object:
        file_object.write(file.file.read())

    return str(file_path)


@app.get('/user', dependencies=[Depends(cookie)], response_model=UserResponse)
def read_user(
        user_id: Annotated[int, Form()] = None,
        nickname: Annotated[str, Form()] = None,
        _: SessionData = Depends(verifier)
):
    # check if all fields are not None
    if user_id is not None and nickname is not None:
        raise HTTPException(
            status_code=400,
            detail='Неверный запрос'
        )

    # check if not form_data [nickname, user_id] is None
    if user_id is None and nickname is None:
        raise HTTPException(
            status_code=400,
            detail='Неверный запрос'
        )

    # pick any not none field
    field = user_id if user_id is not None else nickname

    with Session(engine) as transaction:
        if user_id is not None:
            user = User.get_by_id(transaction, field)
        else:
            user = User.get_by_nickname(transaction, field)

        if user is None:
            raise HTTPException(status_code=404, detail="User with specified id is not found.")

        if user.deleted:
            raise HTTPException(status_code=404, detail="User with specified id is not found.")

        user_metadata = UserMetadata.get_by_user_id(transaction, user.id)

        return UserResponse(nickname=user.nickname,
                            description=user_metadata.description,
                            id=user.id,
                            photo=user_metadata.photo)


@app.patch("/user", dependencies=[Depends(cookie)], status_code=200, response_model=UserPatchResponse)
def update_user(update_data: UserPatchRequest, session: SessionData = Depends(verifier)):
    with Session(engine) as transaction:

        updated_user = User.get_by_id(transaction, session.user_id)
        updated_metadata = UserMetadata.get_by_user_id(transaction, session.user_id)

        if validate_nickname(update_data.nickname) is not True:
            raise HTTPException(
                status_code=400,
                detail='Никнейм занят'
            )

        if update_data.nickname is not None:
            updated_user.nickname = update_data.nickname
        if update_data.user_metadata.photo is not None:
            updated_metadata.photo = update_data.user_metadata.photo
        if update_data.user_metadata.description is not None:
            updated_metadata.description = update_data.user_metadata.description

        updated_user.update(transaction)
        updated_metadata.update(transaction)

        updated_user.user_metadata = [updated_metadata]

        return updated_user


@app.delete("/user", dependencies=[Depends(cookie)], status_code=204)
def delete_user(session: SessionData = Depends(verifier)):
    with Session(engine) as transaction:
        current_user = User.get_by_id(transaction, session.user_id)

        if current_user.deleted:
            raise HTTPException(status_code=404, detail='User not found.')

        current_user.delete(transaction)


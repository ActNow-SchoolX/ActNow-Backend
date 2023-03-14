from fastapi import UploadFile, APIRouter, HTTPException
from src.backend.internals.users import UserModel, get_password_hash, validate_photo
from src.backend.database.orm import User, UserMetadata
from sqlmodel import Session, SQLModel
from src.backend.database import engine
import json

app = APIRouter()

@app.post('/users')
def post_user(item: UserModel):

    item.password = get_password_hash(item.password)

    new_user = User(
        nickname = item.nickname,
        password = item.password,
    )

    with Session(engine) as session:
        User.create(new_user, session)
        UserMetadata.create(
            session, 
            new_user.id, 
            description=item.profile_description, 
            photo=item.profile_photo)

    response = {
        "nickname": item.nickname,
        "description": item.profile_description
    }

    return response


@app.post('/UploadFile')
def post_user(file: UploadFile | None = None):

    if validate_photo(file.content_type, file.size):
        ...
    else:

        raise HTTPException(
            status_code=400,
            detail='Загружаемый файл не соответствует условиям'
        )
    
    file_path = rf'{file.filename}'

    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())

    return file_path


    

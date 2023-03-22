from fastapi import UploadFile, APIRouter, HTTPException, Depends
from src.backend.internals.users import (
    UserRequest,
    UserResponse,
    UserPatch,
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

app = APIRouter()


@app.post('/users', response_model=UserResponse)
def post_user(item: UserRequest):

    item.password = get_password_hash(item.password)

    new_user = user_registrate(item)

    new_user_metadata = user_metadata_create(item, new_user.id)

    return UserResponse(id=new_user.id,
                        nickname=new_user.nickname,
                        profile_photo=new_user_metadata.photo,
                        profile_description=new_user_metadata.description)


@app.post('/upload_file')
def post_user(file: UploadFile | None = None):

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


@app.get("/get_user", dependencies=[Depends(cookie)])
def read_user(user_id: int | None = None, nickname: str | None = None):

    with Session(engine) as transaction:
        if user_id != None and nickname != None:

            raise HTTPException(
                "Необходимо передать только один параметр: айди пользователя или его никнейм"
            )
        
        elif user_id != None and nickname == None:

            user = User.get_by_id(transaction, user_id)
            return user
        
        elif user_id == None and nickname != None:

            user = User.get_by_nickname(transaction, nickname)
            return user
        
        else:

            raise HTTPException (
                "Необходимо передать айди или никнейм"
            )
        

@app.patch("/update_user", dependencies=[Depends(cookie)], status_code=201, response_model=UserPatch)
def update_user(update: UserPatch, session: SessionData = Depends(verifier)):

    with Session(engine) as transaction:

        updated_user = User.get_by_id(transaction, session.user_id)
        updated_metadata = UserMetadata.get_by_user_id(transaction, session.user_id)

        updated_user.nickname = update.nickname

        updated_metadata.description = update.profile_description
        updated_metadata.photo = update.profile_photo

        User.update(updated_user, transaction)
        UserMetadata.update(updated_metadata, transaction)

        return update
    

@app.delete("/delete_user", dependencies=[Depends(cookie)])
def delete_user(session: SessionData = Depends(verifier)):

    with Session(engine) as transaction:

        current_user = User.get_by_id(transaction, session.user_id)

        User.delete(current_user, transaction)

        


    

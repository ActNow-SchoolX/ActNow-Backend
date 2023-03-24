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


@app.get("/get_user/{user_id}", dependencies=[Depends(cookie)])
def read_user(user_id: int):

    with Session(engine) as transaction:
            
            user = User.get_by_id(transaction, user_id)
            user_metadata = UserMetadata.get_by_user_id(transaction, user_id)

            if user is not None and user.deleted is not True:

               return UserResponse(nickname=user.nickname,
                                    profile_description=user_metadata.description,
                                    id=user.id,
                                    profile_photo=user_metadata.photo)
            
            else: 
                raise HTTPException(status_code=404)


@app.get("/get_user_by_nickname/{nickname}", dependencies=[Depends(cookie)])
def read_user(nickname: str):

    with Session(engine) as transaction:
            
            user = User.get_by_nickname(transaction, nickname)
            user_metadata = UserMetadata.get_by_user_id(transaction, user.id)

            if user is not None and user.deleted is not True:

                return UserResponse(nickname=user.nickname,
                                    profile_description=user_metadata.description,
                                    id=user.id,
                                    profile_photo=user_metadata.photo)
            
            else: 
                raise HTTPException(status_code=404)
        

@app.patch("/update_user/me", dependencies=[Depends(cookie)], status_code=201, response_model=UserPatch)
def update_user(update_data: UserPatch, session: SessionData = Depends(verifier)):

    with Session(engine) as transaction:

        updated_user = User.get_by_id(transaction, session.user_id)
        updated_metadata = UserMetadata.get_by_user_id(transaction, session.user_id)

        if validate_nickname(update_data.nickname) is not True:
            raise HTTPException(
                status_code=400,
                detail='Никнейм занят'
            )

        updated_data = update_data.dict(exclude_unset=True)
        
        if update_data.nickname is not None:
            updated_user.nickname = update_data.nickname
        if update_data.profile_photo is not None:
            updated_metadata.photo = update_data.profile_photo
        if update_data.profile_description is not None:
            updated_metadata.description = update_data.profile_description

        User.update(updated_user, transaction)
        UserMetadata.update(updated_metadata, transaction)

        return updated_data
    

@app.delete("/delete_user", dependencies=[Depends(cookie)], status_code=204)
def delete_user(session: SessionData = Depends(verifier)):

    with Session(engine) as transaction:

        current_user = User.get_by_id(transaction, session.user_id)
        
        if current_user.deleted is not True:
            User.delete(current_user, transaction)
        else:
            raise HTTPException(status_code=404)

        


    

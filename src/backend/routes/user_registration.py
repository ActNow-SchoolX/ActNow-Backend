from fastapi import UploadFile, APIRouter, HTTPException
from src.backend.internals.users import (UserRequest, 
                                         UserResponse, 
                                         get_password_hash, 
                                         validate_photo, 
                                         user_registrate, 
                                         user_metadata_create,)

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
    
    file_path = rf'{file.filename}'

    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())

    return file_path


    

from fastapi import FastAPI, UploadFile
from users import User, get_password_hash
from starlette.responses import JSONResponse
import json

app = FastAPI()

@app.post('/users')
def post_user(item: User):

    item.password = get_password_hash(item.password)
    
    with open(r'UserDataList.json', 'w') as outfile:
        json.dump(item.json(), outfile)

    return item


@app.post('/UploadFile')
def post_user(file: UploadFile | None = None):

    file_path = rf'{file.filename}'

    with open(file_path, "wb+") as file_object:
        file_object.write(file.file.read())

    return file_path


    



from fastapi import Request, HTTPException, APIRouter
from pydantic import BaseModel
# from fastapi.responses import JSONResponse

app = APIRouter()


class Nicknames(BaseModel):
    nickname: str


nicknames = ['bob', 'aboba', 'somebody', 'biba', "user"]


# логика типа
def validate_nickname(value, nicknames):
    for elem in nicknames:
        if elem == value:
            return False
    return True


@app.post("/validate_nickname")
def get_nickname(request: Nicknames):
    value = request.nickname
    if validate_nickname(value, nicknames):
        r = {"nickname": value, "available": True}
    else:
        r = {"nickname": value, "available": False}
    return r

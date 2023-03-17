from fastapi import Request, HTTPException, APIRouter
from pydantic import BaseModel
from src.backend.database.orm import User
from sqlmodel import Session, SQLModel, select
from src.backend.database import engine
# from fastapi.responses import JSONResponse

app = APIRouter()


class Nicknames(BaseModel):
    nickname: str


# логика типа
def validate_nickname(value, users):
    for elem in users:
        if elem == value:
            return False
    return True


@app.post("/validate_nickname")
def get_nickname(request: Nicknames):
    user1 = User(nickname="user1", password='password1')
    user2 = User(nickname="user2", password='password2')



    with Session(engine) as session:
        user1.create(session)
        user2.create(session)

        statement = select(User)
        users = session.exec(statement)
        # print(users)

    value = request.nickname
    if validate_nickname(value, users):
        r = {"nickname": value, "available": True}
    else:
        r = {"nickname": value, "available": False}
    return r

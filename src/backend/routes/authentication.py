from fastapi import Depends, APIRouter
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import User
from src.backend.routes.auth import security

app = APIRouter()


class UserAuth(BaseModel):
    nickname = str
    password = str


def user_auth(user_data):
    user = User(
        nickname=user_data.nickname,
        password=user_data.password
    )

    with Session(engine) as transaction:
        User.create(user, transaction)


@app.post("/login")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    user_auth(credentials.nickname)
    return {"success": True, "message": "Logged in successfully!"}



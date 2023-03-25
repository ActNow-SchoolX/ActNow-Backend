from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import User
from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData

app = APIRouter()


class Nicknames(BaseModel):
    nickname: str


# логика типа
def validate_nickname(requested_nickname: str):
    with Session(engine) as transaction:
        user = User.get_by_nickname(transaction, nickname=requested_nickname)

    if user is None:
        return True

    return False


@app.post("/user/validate_nickname", dependencies=[Depends(cookie)])
def get_nickname(request: Nicknames, _: SessionData = Depends(verifier)):
    if validate_nickname(request.nickname):
        return JSONResponse(
            status_code=200,
            content={"nickname": request.nickname, "available": True},
        )
    else:
        return JSONResponse(
            status_code=409,
            content={"nickname": request.nickname, "available": False},
        )


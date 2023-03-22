from fastapi import APIRouter, Depends

from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData
from src.backend.database.orm import Story

from sqlmodel import Session
from src.backend.database import engine

app = APIRouter()


@app.get("/get_story")
def get_by_user_id():
    pass


@app.get("/get_story", dependencies=[Depends(cookie)])
def get_story_by_id(user_id: int, session: SessionData = Depends(verifier)) -> Story:
    with Session(engine) as transaction:
        story = Story.get_by_user_id(transaction, user_id)

    return story

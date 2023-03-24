from fastapi import APIRouter, Depends

from src.backend.dependencies import cookie, verifier
from src.backend.internals.goals import GoalResponse
from src.backend.sessions import SessionData
from src.backend.database.orm import Story

from sqlmodel import Session
from src.backend.database import engine

app = APIRouter()


@app.get("/story/{user_id}", response_model=list(GoalResponse), dependencies=[Depends(cookie)])
def get_story_by_id(user_id: int, limit: int = 100, offset: int = 0, _: SessionData = Depends(verifier)):
    if limit > 100:
        limit = 100

    with Session(engine) as transaction:
        stories = Story.get_by_user_id(transaction, user_id, limit, offset)

        stories = [story for story in stories if not story.deleted]

        return stories

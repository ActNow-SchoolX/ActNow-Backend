from fastapi import APIRouter, Depends, HTTPException

from src.backend.dependencies import cookie, verifier
from src.backend.internals.stories import StoryResponse
from src.backend.sessions import SessionData
from src.backend.database.orm import Story

from sqlmodel import Session
from src.backend.database import engine

app = APIRouter()


@app.get("/stories/user/{user_id}", response_model=list[StoryResponse], dependencies=[Depends(cookie)])
def get_story_by_id(user_id: int, limit: int = 100, offset: int = 0, _: SessionData = Depends(verifier)):
    if offset < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Offset and limit must be positive.")

    if limit > 100:
        limit = 100

    with Session(engine) as transaction:
        stories = Story.get_by_user_id(transaction, user_id, limit, offset)

        stories = [story for story in stories if not story.deleted]

        for idx, story in enumerate(stories):
            stories[idx].date_create = story.date_create.timestamp()

        return stories


@app.get("/stories/goal/{goal_id}", response_model=list[StoryResponse], dependencies=[Depends(cookie)])
def get_story_by_id(goal_id: int, limit: int = 100, offset: int = 0, _: SessionData = Depends(verifier)):
    if offset < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Offset and limit must be positive.")

    if limit > 100:
        limit = 100

    with Session(engine) as transaction:
        stories = Story.get_by_goal_id(transaction, goal_id, limit, offset)

        stories = [story for story in stories if not story.deleted]

        for idx, story in enumerate(stories):
            stories[idx].date_create = story.date_create.timestamp()

        return stories

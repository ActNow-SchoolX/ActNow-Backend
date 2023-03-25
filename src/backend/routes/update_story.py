from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import Story
from src.backend.dependencies import cookie, verifier
from src.backend.internals.stories import StoryResponse, check_description
from src.backend.sessions import SessionData

app = APIRouter()


def validate_story_exists(story_id):
    with Session(engine) as transaction:
        if Story.get_by_id(transaction, story_id) is None:
            return False

        if Story.get_by_id(transaction, story_id).deleted:
            return False

        return True


@app.patch('/story', response_model=StoryResponse, dependencies=[Depends(cookie)], status_code=201)
def update_story(story_id: int, description: str, session: SessionData = Depends(verifier)):
    if not validate_story_exists(story_id):
        raise HTTPException(status_code=400, detail='История не найдена')

    with Session(engine) as transaction:
        story = Story.get_by_id(transaction, story_id)
        if not check_description(description):
            raise HTTPException(status_code=400, detail='Описание истории превышает возможное количество символов')

        story.summary = description
        story.update(transaction)

        story.date_create = story.date_create.timestamp()

    return story

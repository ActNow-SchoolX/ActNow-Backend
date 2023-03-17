from __future__ import annotations

from fastapi import UploadFile
from pydantic import BaseModel
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import Story


def check_description(description):
    if len(description) > 1000:
        raise ValueError('Описание истории превышает возможное количество символов')
    return description


class StoryResponse(BaseModel):
    id: int
    user_id: int
    goal_id: int
    photo: str
    summary: str
    date_create: float


def story_create(user_id, goal_id: int, photo: str, description: str) -> Story:
    story = Story(
        user_id=user_id,
        goal_id=goal_id,
        summary=description,
        photo=photo
    )

    with Session(engine) as transaction:
        story = Story.create(story, transaction)

        story.date_create = story.date_create.timestamp()

    return story

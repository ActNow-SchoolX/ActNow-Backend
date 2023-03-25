from __future__ import annotations

from datetime import datetime

from fastapi import File
from pydantic import BaseModel, parse, Field
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import Story, Goal


def check_description(description):
    if len(description) > 1000:
        raise ValueError('Описание истории превышает возможное количество символов')
    return description


def check_photo(photo: File):
    if photo.content_type not in ('image/png', 'image/jpg', 'image/jpeg'):
        raise TypeError('File content must be image.')
    elif int(photo.size) > 4194304:
        raise ValueError('File size must be < 4194304.')
    else:
        return photo


def validate_goal_exists(goal_id):
    with Session(engine) as transaction:
        if Goal.get_by_id(transaction, goal_id) is not None:
            return True

        return False


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

        if story.date_create is not None:
            story.date_create = story.date_create.timestamp()

    return story

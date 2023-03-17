from __future__ import annotations
from sqlmodel import Session
from src.backend.database import engine
from src.backend.database.orm import Story
from pydantic import BaseModel, validator


class StoryRequest(BaseModel):
    user_id: int
    goal_id: str
    photo: str
    description: str

    @validator('photo')
    def check_photo(cls, photo):
        if photo is None:
            raise NotADirectoryError('Изображение не найдено')
        return photo

    @validator('description')
    def check_description(cls, description):
        if len(description) > 1000:
            raise ValueError('Описание истории превышает возможное количество символов')
        return description


class StoryResponse(BaseModel):
    id: int
    user_id: int
    photo: str
    description: str


def story_create(story_data, user_id) -> Story:
    story = Story(
        story_id=story_data.id,
        description=story_data.description,
        photo=story_data.photo,
        user_id=user_id,
    )

    with Session(engine) as transaction:
        Story.create(story, transaction)
    return story

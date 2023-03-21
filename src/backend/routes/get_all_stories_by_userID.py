from __future__ import annotations
from pydantic import BaseModel, validator
from sqlmodel import Session, SQLModel
from src.backend.database.orm import Story
from src.backend.database import engine


class StoryRequest(BaseModel):
    id: int
    user_id: int
    goal_id: int
    deleted: bool

    @validator('deleted')
    def check_del(cls, deleted):
        if deleted == 0:
            raise ValueError('Story not found')
        return


def get_all_stories_by_userID(story_data) -> Story:
    story = Story(
        id=story_data.id,
        user_id=story_data.user_id,
        goal_id=story_data.goal_id
    )

    with Session(engine) as transaction:
        Story.get_all(story, transaction)

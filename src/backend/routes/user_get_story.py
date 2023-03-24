from typing import Any, Type
from fastapi import APIRouter, Depends, HTTPException
from src.backend.dependencies import cookie
from src.backend.internals.stories import StoryResponse
from src.backend.routes.stories_endpoint import app

App = APIRouter()


@app.get("./story,", response_model=StoryResponse, dependencies=[Depends(cookie)])
async def get_story(user_id, story_id: int, photo: str, story: str, summary=str) -> tuple[Any, int, str, Type[str]]:
    if story is None or story.deleted is True:
        raise HTTPException(
            status_code=404
        )
    else:
        return user_id, story_id, photo, summary

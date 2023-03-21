from fastapi import APIRouter

from src.backend.internals.stories import StoryResponse
from src.backend.routes.stories_endpoint import app

App = APIRouter()


@app.get("./story,", response_model=StoryResponse)
async def get_goal(user_id, goal_id: int, photo: str, description: str) -> tuple[int, int, str, str]:
    return user_id, goal_id, photo, description

from fastapi import HTTPException, Depends, APIRouter
from fastapi.openapi.models import Response

from src.backend.dependencies import verifier, cookie
from src.backend.internals.goals import GoalResponse
from src.backend.sessions import SessionData

app = APIRouter()


@app.patch("/goal/{goal_id}", response_model=Response, dependencies=[Depends(cookie)], status_code=201)
async def update_goal(item: GoalResponse, session: SessionData = Depends(verifier)):
    updated_goal = update_goal(item, session.user_id)
    if updated_goal is None:
        raise HTTPException(status_code=404, detail="Not found")

    return updated_goal

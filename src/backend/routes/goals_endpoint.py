from fastapi import APIRouter, Depends

from src.backend.dependencies import cookie, verifier
from src.backend.routes.goals import GoalRequest, GoalResponse, goal_create
from src.backend.sessions import SessionData

app = APIRouter()


@app.post('/goal', response_model=GoalResponse, dependencies=[Depends(cookie)], status_code=201)
async def create_goal(item: GoalRequest, session: SessionData = Depends(verifier)):

    new_goal = goal_create(item, session.user_id)

    return new_goal

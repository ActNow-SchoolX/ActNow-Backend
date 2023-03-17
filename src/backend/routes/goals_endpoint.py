from fastapi import APIRouter, HTTPException, Depends, Response
from src.backend.dependencies import cookie, backend, verifier
from sqlmodel import Session


from src.backend.routes.goals import GoalRequest, GoalResponse, goal_create
from src.backend.sessions import SessionData
from src.backend.dependencies import cookie, backend, verifier
from src.backend.database import engine
from src.backend.database.orm import User

app = APIRouter()

@app.post("/login", dependencies=[Depends(cookie.get_last_cookie)])

@app.post('/goal', response_model=GoalResponse, dependencies=[Depends(cookie)])
async def create_goal(item: GoalRequest, session: SessionData = Depends(verifier)):

    with Session(engine) as ass:

        new_goal = goal_create(item, session.user_id)

        if new_goal is not None:
            raise HTTPException(
                status_code=201,
                detail="Голс успешно создан!"
            )
        
        return GoalResponse(id=new_goal.id,
                            user_id=new_goal.user_id,
                            title=new_goal.title,
                            description=new_goal.description,
                            price=new_goal.price,
                            deadline=new_goal.deadline)
        

    

    
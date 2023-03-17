from fastapi import APIRouter, Depends, Response
from src.backend.dependencies import cookie, backend, verifier
from sqlmodel import Session
from pydantic import BaseModel


from src.backend.routes.goals_create import GoalsEntity
from src.backend.sessions import SessionData
from src.backend.dependencies import cookie, backend, verifier
from src.backend.database import engine
from src.backend.database.orm import User, UserMetadata

app = APIRouter()

class Goal(BaseModel):
    title: str
    description: str
    first_story: str
    price: float | None = None
    date: str | None = None

@app.post('/create_goal', dependencies=Depends[("cookie")])
async def create_goal(item: GoalsEntity, session: SessionData = Depends(verifier)):

    with Session(engine) as ass:
        
        user = User.get_by_id(ass, _id=session.user_id)

        response = {
        'user_id': user.id,
        'title': item.title,
        'description': item.description,
        'story': item.first_story,
        'price': item.price,
        'date': item.date
        }
        
        return response
        

    

    
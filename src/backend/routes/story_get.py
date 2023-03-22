from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.backend.database import engine
from src.backend.database.orm import Story
from src.backend.dependencies import cookie, verifier
from src.backend.sessions import SessionData

app = APIRouter()

@app.get("/story", dependencies=[Depends(cookie)])
def get_some_stories(limit: int, offset: int, _: SessionData = Depends(verifier)):
    with Session(engine) as transaction:
        stories = Story.get_all(transaction)
    # limit - количество историй, offset - сдвиг
    return stories[offset:][:limit]

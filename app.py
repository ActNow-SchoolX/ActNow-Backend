from fastapi import FastAPI
from sqlmodel import SQLModel

from src.backend.database import engine
from src.backend.routes import (
    nickname_validation,
    authentication,
    stories_endpoint,
    users_endpoint,
    goals_endpoint,
    deauthentication,
    likes,
    update_story,
    get_all_stories_by_userID,
    goal_update_endpoint
)

app = FastAPI()


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)


app.include_router(
    nickname_validation.app,
    tags=['User']
    )
app.include_router(
    deauthentication.app,
    tags=["Auth"]
)
app.include_router(
    users_endpoint.app,
    tags=["User"]
)
app.include_router(
    goals_endpoint.app,
    tags=["Goal"]
)
app.include_router(
    authentication.app,
    tags=["Auth"]
)
app.include_router(
    stories_endpoint.app,
    tags=["Story"]
)
app.include_router(
    likes.app,
    tags=["Story"]
)
app.include_router(
    update_story.app,
    tags=["Story"]
)
app.include_router(
    get_all_stories_by_userID.app,
    tags=["Story"]
)
app.include_router(
    goal_update_endpoint.app,
    tags=["Goal"]
)

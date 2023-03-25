from fastapi import FastAPI
from sqlmodel import SQLModel

from src.backend.database import engine
from src.backend.routes import (
    nickname_validation,
    authentication,
    stories_endpoint,
    users_endpoint,
    goals_endpoint,
    deauthentication
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

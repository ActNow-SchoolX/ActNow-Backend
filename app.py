from fastapi import FastAPI
from src.backend.routes import nickname_validation, story_endpoint
from src.backend.routes import auth
from src.backend.routes import user_registration
from src.backend.database import engine
from sqlmodel import SQLModel

app = FastAPI()


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)


app.include_router(nickname_validation.app)
app.include_router(auth.app)
app.include_router(user_registration.app)
app.include_router(story_endpoint.app)

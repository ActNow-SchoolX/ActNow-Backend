from fastapi import FastAPI
from src.backend.routes import nickname_validation
from src.backend.routes import auth
from src.backend.routes import user_registration
from src.backend.routes import user_de_authorization
from src.backend.database import engine
from sqlmodel import SQLModel

app = FastAPI()


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)


app.include_router(nickname_validation.app)
app.include_router(auth.app)
app.include_router(user_de_authorization.app)
app.include_router(user_registration.app)

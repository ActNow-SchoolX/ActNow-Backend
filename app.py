from fastapi import FastAPI
from src.backend.routes import nickname_validation
from src.backend.routes import auth
from src.backend.routes import user_registration

app = FastAPI()
app.include_router(nickname_validation.app)
app.include_router(auth.app)
app.include_router(user_registration.app)

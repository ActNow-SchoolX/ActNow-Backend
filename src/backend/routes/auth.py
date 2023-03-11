from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

users = {
    "user1": "password1",
    "user2": "password2",
}

def validate_user(username: str, password: str):
    if username not in users or password != users[username]:
        raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/login")
async def login(credentials: HTTPBasicCredentials = security):
    validate_user(credentials.username, credentials.password)
    return {"success": True, "message": "Logged in successfully!"}


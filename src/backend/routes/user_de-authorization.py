from fastapi import FastAPI, Depends
import fastapi.openapi.models
import src.backend.dependencies

app = FastAPI()


@app.post("/logout")
async def logout(response: fastapi.openapi.models.Response, session_uuid: Depends(src.backend.dependencies.cookie)):
    await src.backend.dependencies.backend.delete(session_uuid)
    src.backend.dependencies.cookie.delete_from_response(response)
    return {"message": "Logged out successfully"}

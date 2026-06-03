import uvicorn
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from routers import artitst,playlist,track,track_Record,user
from database import engine
import models
from python_client import sp

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='Statify', description='Statfy API', version='1.0.0')
app.include_router(user.router)
app.include_router(track_Record.router)
app.include_router(track.router)

app.include_router(artitst.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = error.get("loc")[-1]
        err_msg = error.get("msg")
        errors.append({"field": field, "message": err_msg})
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
        "status": "Validation Error",
        "errors": errors
    })

@app.get("/")
def root():
    return sp.current_user_recently_played(limit=1)


@app.get("/callback")
def callback():
    return {"message": "Authentification was not successful."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888)
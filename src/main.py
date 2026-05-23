import uvicorn
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from routers import artitst,genre,playlist,stats,track,track_Record
from database import engine
import models



models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='Statify', description='Statfy API', version='1.0.0')



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
    return {"Message": "Welcome to Statify go to /docs for the API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
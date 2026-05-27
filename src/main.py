import uvicorn
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status
from routers import artitst,genre,playlist,stats,track,track_Record,user
from database import engine
import models
from spotipy.oauth2 import SpotifyOAuth
import spotipy

# TODO: client_id and client_secret a .env file (.env file also in gitignore)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="1549b84275a94fb2892effbc257c06a3",
    client_secret="643062d2510446969d16dea9b9c53eba",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-recently-played user-top-read playlist-read-private"
))

# 
sp.current_user()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title='Statify', description='Statfy API', version='1.0.0')
app.include_router(user.router)



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
    return sp.current_user_recently_played(limit=10)
    #return {"Message": "Welcome to Statify go to /docs for the API"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888)
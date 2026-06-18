from fastapi import APIRouter, Request
from fastapi_restful.cbv import cbv
from fastapi.params import Depends
from pydantic import BaseModel
from starlette import status
from starlette.exceptions import HTTPException

from models import DBUser
from routers.base import BaseAPI
from database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import authenticate_user
from auth import ACCESS_TOKEN_EXPIRE_MINUTES
from auth import create_access_token


router = APIRouter(prefix="/token", tags=["token"])



class Token(BaseModel):
    access_token: str
    token_type: str

@cbv(router)
class TokenAPI(BaseAPI):
    db: Session = Depends(get_db)

    @router.post("/", response_model=Token)
    async def login_for_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()):
        auth = authenticate_user(self.db, form_data.username, form_data.password)
        if not auth:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        dbUser = self.db.query(DBUser).filter(DBUser.Name == form_data.username).first()
        access_token = create_access_token(data={"sub" : str(dbUser.Id)}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
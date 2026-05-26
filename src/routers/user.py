from pydantic import BaseModel, Field, field_validator, ValidationError
import models  as models
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from database import get_db
from passlib.context import CryptContext

from models import DBUser

router = APIRouter(prefix="/user", tags=["User"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
        return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UserLogin(BaseModel):
    Name: str = Field(...)
    Password: str = Field(..., min_length=8, max_length=72)
class UserCreate(UserLogin):
    Spotify_id: str =Field(...)

class UserResponse(BaseModel):
    UID: int = Field(...)
    Name: str = Field(...)
    Spotify_id: str = Field(...)


@cbv(router)
class UserAPI():
    db: Session = Depends(get_db)

    @router.post("/register", response_model=UserResponse)
    def register(self, user: UserCreate):
        hashed = hash_password(user.Password)
        db_user = DBUser(Name=user.Name, Password=hashed, Spotify_id=user.Spotify_id)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    @router.post("/login", response_model=UserResponse)
    def login(self, user: UserLogin):
        db_user = self.db.query(DBUser).filter(DBUser.Name == user.Name).first()
        if not db_user or not verify_password(user.Password, db_user.Password):
            raise HTTPException(status_code=401, detail="Ungültige Zugangsdaten")
        return db_user
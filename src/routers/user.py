import logging

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi_restful.cbv import cbv
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models as models
from auth import verify_api_key
from database import get_db
from models import DBUser
from routers.base import BaseAPI

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["User"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UserLogin(BaseModel):
    Name: str = Field(...)
    Password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    Id: int = Field(...)
    Name: str = Field(...)
    Image: str | None


@cbv(router)
class UserAPI(BaseAPI):
    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)

    @router.post("/register", response_model=UserResponse)
    def register(self, user: UserLogin):
        logger.info("POST /user/register called")
        try:
            existing_user = self.db.query(DBUser).filter(DBUser.Name == user.Name).first()
            Spotify_user = self.sp.current_user()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username bereits vergeben")
            hashed = hash_password(user.Password)
            image = Spotify_user["images"][0]["url"] if Spotify_user["images"] else None

            db_user = DBUser(Name=user.Name, Password=hashed, Image=image,RID=1)
            self.db.add(db_user)
            self.db.flush()
            # TODO: Anhand von password und Username schauen ob es ein Admin oder User ist
            db_role = models.DBRole(
                Role="User",
                CanGet=True,
                CanPost=True,
                CanDelete=False)

            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except Exception as e:
            logger.error("Error registering user: %s", str(e))
            raise HTTPException(status_code=500, detail="Error registering user")

    @router.post("/login", response_model=UserResponse)
    def login(self, user: UserLogin):
        logger.info("POST /user/login called")
        try:
            db_user = self.db.query(DBUser).filter(DBUser.Name == user.Name).first()
            if not db_user or not verify_password(user.Password, db_user.Password):
                raise HTTPException(status_code=401, detail="Ungültige Zugangsdaten")
            return db_user
        except Exception as e:
            logger.error("Error logging in user: %s", str(e))
            raise HTTPException(status_code=500, detail="Error logging in user")

    @router.delete("/logout/{user_id}", response_model=UserResponse)
    def logout(self, user_id: int):
        logger.info("DELETE /user/logout/%s called", user_id)
        try:
            db_user = self.db.query(DBUser).filter(DBUser.Id == user_id).first()
            self.db.delete(db_user)
            self.db.commit()
            return UserResponse(Id=db_user.Id, Name=db_user.Name)
        except Exception as e:
            logger.error("Error logging out user: %s", str(e))
            raise HTTPException(status_code=500, detail="Error logging out user")
import logging

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import helper
import models as models
from auth import verify_api_key
from database import get_db
from models import DBUser
from routers.base import BaseAPI

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["User"])


class UserLogin(BaseModel):
    Name: str = Field(...)
    Password: str = Field(..., min_length=8, max_length=72)

class UserUpdate(BaseModel):
    Id: int = Field(...)
    Name: str = Field(...)

class UserResponse(UserUpdate):
    Image: str | None


@cbv(router)
class UserAPI(BaseAPI):
    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)

    @router.post("/register", response_model=UserResponse)
    def register(self, user: UserLogin):
        logger.info("POST /user/register called")
        try:
            if not self.db.query(models.DBRole).first():
                self.db.add_all([
                    models.DBRole(Id=1, Role="admin", CanGet=True, CanPost=True, CanDelete=True),
                    models.DBRole(Id=2, Role="user", CanGet=True, CanDelete=False, CanPost=True),
                ])
                self.db.commit()
                logger.info("Made roles if didn't exists")
            existing_user = self.db.query(DBUser).filter(DBUser.Name == user.Name).first()
            Spotify_user = self.sp.current_user()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username bereits vergeben")
            hashed = helper.hash_password(user.Password)
            image = Spotify_user["images"][0]["url"] if Spotify_user["images"] else None

            # TODO: Anhand von password und Username schauen ob es ein Admin oder User ist
            db_user = DBUser(Name=user.Name, Password=hashed, Image=image,RID=2)
            self.db.add(db_user)
            self.db.flush()
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
            if not db_user or not helper.verify_password(user.Password, db_user.Password):
                raise HTTPException(status_code=401, detail="Ungültige Zugangsdaten")
            return db_user
        except Exception as e:
            logger.error("Error logging in user: %s", str(e))
            raise HTTPException(status_code=500, detail="Error logging in user")


    @router.put("/", response_model=UserUpdate)
    def update_user(self, db_user: UserUpdate):
        logger.info("Put /user/update called")
        updated_user = self.get_or_404(self.db,models.DBUser,db_user.Id)
        updated_user.Name=db_user.Name
        self.db.add(updated_user)
        self.db.commit()
        self.db.refresh(updated_user)

        return UserUpdate(Id=updated_user.Id, Name=updated_user.Name)


    @router.delete("/logout/{user_id}", response_model=UserResponse)
    def logout(self, user_id: int):
        logger.info("DELETE /user/logout/%s called", user_id)
        try:
            db_user = self.db.query(DBUser).filter(DBUser.Id == user_id).first()
            self.db.delete(db_user)
            self.db.commit()
            return UserResponse(Id=db_user.Id, Name=db_user.Name,Image=db_user.Image)
        except Exception as e:
            logger.error("Error logging out user: %s", str(e))
            raise HTTPException(status_code=500, detail="Error logging out user")
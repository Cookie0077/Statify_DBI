import logging

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import helper
import models as models
from auth import verify_api_key, get_User_id
from database import get_db
from models import DBUser
from routers.base import BaseAPI

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["User"])


class UserLogin(BaseModel):
    Name: str = Field(...)
    Password: str = Field(..., min_length=8, max_length=72)

class UpdateUser(BaseModel):
    Name: str = Field(...)

class UserResponse(UpdateUser):
    Id: int = Field(...)
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
                    models.DBRole(Id=2, Role="user", CanGet=True, CanDelete=True, CanPost=True),
                ])
                self.db.commit()
                logger.info("Made roles if didn't exists")
            existing_user = self.db.query(DBUser).filter(DBUser.Name == user.Name).first()
            Spotify_user = self.sp.current_user()
            if existing_user:
                raise HTTPException(status_code=400, detail="Username bereits vergeben")
            hashed = helper.hash_password(user.Password)
            image = Spotify_user["images"][0]["url"] if Spotify_user["images"] else None
            db_user = DBUser(Name=user.Name, Password=hashed, Image=image,RID=2)
            self.db.add(db_user)
            self.db.flush()
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


    @router.put("/", response_model=UserResponse)
    def update_user(self, User:UpdateUser,user_id_str: str=Depends(get_User_id)):
        user_id = int(user_id_str)
        logger.info("Put /user/update called")
        try:
            existing_user = self.db.query(DBUser).filter(DBUser.Id == user_id).first()
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")

            check_Username = self.db.query(DBUser).filter(User.Name == existing_user.Name).first()
            if check_Username:
                raise HTTPException(status_code=400, detail="Username already registered")
            updated_user = self.get_or_404(self.db,models.DBUser,user_id)
            updated_user.Name=User.Name
            self.db.add(updated_user)
            self.db.commit()
            self.db.refresh(updated_user)

            return UserResponse(Id=updated_user.Id, Name=updated_user.Name, Image=updated_user.Image)
        except Exception as e:
            logger.error("Error updating user: %s", str(e))


    @router.delete("/")
    def delete(self, user_id_str: str = Depends(get_User_id)):
        user_id = int(user_id_str)
        logger.info("DELETE /user/ %s called", user_id)
        try:
            db_user = self.db.query(DBUser).filter(DBUser.Id == user_id).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            self.db.query(models.DBTrack_Record).filter(models.DBTrack_Record.UID == user_id).delete(
                synchronize_session=False)
            deleted_playlist = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.UID == user_id).all()
            for playlist in deleted_playlist:
                self.db.query(models.DBPlaylist_Track).filter(models.DBPlaylist_Track.PID == playlist.Id).delete(
                synchronize_session=False)
                self.db.delete(playlist)
            self.db.query(models.DBRole).filter(models.DBRole.Id == db_user.RID).delete(synchronize_session=False)
            self.db.delete(db_user)
            self.db.commit()

            return {"message": "User successfully deleted"}
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Error deleting user: %s", str(e))
            raise HTTPException(status_code=500, detail="Error deleting user")
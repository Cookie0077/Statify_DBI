from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import count

import models
from auth import verify_api_key
from database import get_db
from routers.base import BaseAPI

router = APIRouter(prefix="/artist", tags=["Artist"])


class ArtistCreate(BaseModel):
    Name: str
    Spotify_id: str
    Image: str

    model_config = {"from_attributes": True}

class ArtistResponse(ArtistCreate):
    Id: int

@cbv(router)
class Artist(BaseAPI):
    db: Session = Depends(get_db)
    api_key:str = Depends(verify_api_key)

    @router.get("/{user_id}", response_model=list[ArtistResponse])
    def get_artists(self, user_id: int,limit: Optional[int] = None):
        artists = (
        self.db.query(models.DBArtist)
        .join(models.DBTrack, models.DBArtist.Id == models.DBTrack.AID)
        .join(models.DBTrack_Record, models.DBTrack_Record.TID == models.DBTrack.Id)
        .filter(models.DBTrack_Record.UID == user_id)
        .group_by(models.DBArtist)
        .order_by(count(models.DBTrack_Record.Timestamp).desc())
        .distinct()
        .limit(limit)
        .all())
        return artists
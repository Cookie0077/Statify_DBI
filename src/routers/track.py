import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from auth import verify_api_key
from database import get_db
from routers.base import BaseAPI

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/track", tags=["Track"])


# Pydentic Schemas
class TrackCreate(BaseModel):
    Spotify_id: str
    Name: str = Field(..., min_length=1, max_length=200)
    Image: str
    URL: str
    AID: int


class TrackResponse(TrackCreate):
    Id: int


@cbv(router)
class TrackAPI(BaseAPI):
    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)

    @router.get("/", response_model=list[TrackResponse])
    def get_all_tracks(self):
        logger.info("GET /track called")
        try:
            return self.db.query(models.DBTrack).all()
        except Exception as e:
            logger.error("Error getting tracks: %s", str(e))
            raise HTTPException(status_code=500, detail="Error getting tracks")

    @router.get("/{id}", response_model=TrackResponse)
    def get_track(self, id: int):
        logger.info("GET /track/%s called", id)
        try:
            return self.db.query(models.DBTrack).get(id)
        except Exception as e:
            logger.error("Error getting track %s: %s", id, str(e))
            raise HTTPException(status_code=500, detail="Error getting track")

    @router.delete("/{track_id}", response_model=TrackResponse)
    def delete_track(self, track_id: int):
        logger.info("DELETE /track/%s called", track_id)
        try:
            deleted_track = self.db.query(models.DBTrack).filter(models.DBTrack.Id == track_id).first()
            self.db.delete(deleted_track)
            self.db.commit()
            return TrackResponse(Id=deleted_track.Id, Name=deleted_track.Name, Spotify_id=deleted_track.Spotify_id,
                                 Image=deleted_track.Image, URL=deleted_track.URL, AID=deleted_track.AID)
        except Exception as e:
            logger.error("Error deleting track %s: %s", track_id, str(e))
            raise HTTPException(status_code=500, detail="Error deleting track")
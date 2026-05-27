from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
import models
from main import sp
from database import get_db
from routers.base import BaseAPI

router = APIRouter(prefix="/track_record", tags=["Track-Record"])


# Pydentic Schemas
class TrackCreate(BaseModel):
    Spotify_id: str
    Name: str = Field(..., min_length=1, max_length=200)
    Image: str
    UID: int
    TID: int


class TrackResponse(TrackCreate):
    id: int


@cbv(router)
class TrackAPI(BaseAPI):
    db: Session = Depends(get_db)

    @router.get("/", response_model=list[TrackResponse])
    def get_all_tracks(self):
        return self.db.query(models.DBTrack).all()

    @router.get("/{id}", response_model=TrackResponse)
    def get_track(self, id: int):
        return self.db.query(models.DBTrack).filter(models.DBTrack.TID == id).first()

    @router.post("/", response_model=TrackResponse)
    def add_tracks(self, listOfTracks: list[TrackCreate]):
        for track in listOfTracks:
            sp.track(track.Spotify_id)




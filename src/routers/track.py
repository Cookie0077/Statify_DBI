from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from auth import verify_api_key
from database import get_db
from routers.base import BaseAPI

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
        return self.db.query(models.DBTrack).all()

    @router.get("/{id}", response_model=TrackResponse)
    def get_track(self, id: int):
        return self.get_or_404(self.db, models.DBTrack, id)

    @router.post("/", response_model=TrackResponse)
    def add_tracks(self, listOfTracks: list[TrackCreate]):
        # TODO: Implement - needed after track_record call
        pass

    @router.delete("/{track_id}", response_model=TrackResponse)
    def delete_track(self, track_id: int):
        deleted_track = self.db.query(models.DBTrack).filter(models.DBTrack.Id == track_id).first()
        self.db.delete(deleted_track)
        self.db.commit()
        return TrackResponse(Id=deleted_track.Id, Name=deleted_track.Name, Spotify_id=deleted_track.Spotify_id,
                             Image=deleted_track.Image, URL=deleted_track.URL, AID=deleted_track.AID)

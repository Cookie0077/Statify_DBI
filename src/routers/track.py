from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
import models
from database import get_db
from routers.base import BaseAPI

router = APIRouter(prefix="/track", tags=["Track"])

# Pydentic Schemas
class TrackCreate(BaseModel):
    Spotify_id: str
    Name: str = Field(..., min_length=1, max_length=200)
    Image: str
    AID: int


class TrackResponse(TrackCreate):
    Id: int


@cbv(router)
class TrackAPI(BaseAPI):
    db: Session = Depends(get_db)
    @router.get("/", response_model=list[TrackResponse])
    def get_all_tracks(self):
        # TODO: Falls meherer user auf eine DB anders machen
        return self.db.query(models.DBTrack).all()

    @router.get("/{id}", response_model=TrackResponse)
    def get_track(self, id: int):
        return self.get_or_404(self.db, models.DBTrack, id)

    @router.post("/", response_model=TrackResponse)
    def add_tracks(self, listOfTracks: list[TrackCreate]):
        # TODO: Implement - needed after track_record call
        pass



        

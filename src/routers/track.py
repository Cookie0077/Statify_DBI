from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
import models
from database import get_db
from routers.base import BaseAPI

router = APIRouter(prefix="/hardware", tags=["Hardware"])

# Pydentic Schemas
class TrackCreate(BaseModel):
    Spotify_id: str
    Name: str = Field(..., min_length=1, max_length=200)
    Image: str
    AID: int


class TrackResponse(TrackCreate):
    TID: int


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
    def create_track(self, track: TrackCreate):
        self.db.add(track)
        self.db.commit()
        self.db.refresh(models.DBTrack)
        

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
import models
from database import get_db
from routers.base import BaseAPI

router = APIRouter(prefix="/track_record", tags=["Track-Record"])


class TrackRecordCreate(BaseModel):
    Timestamp: datetime
    Duration: int
    UID: int
    TID: int


class TrackRecordResponse(TrackRecordCreate):
    Id: int
    model_config = {"from_attributes": True}

class TrackRecordDetailResponse(TrackRecordResponse):
    Track_Name: str
    Track_Image: str
    Artist_Name: str


@cbv(router)
class TrackRecordAPI(BaseAPI):
    db: Session = Depends(get_db)

    @router.get("/{user_id}", response_model=list[TrackRecordDetailResponse])
    def get_all(self, user_id: int,limit: Optional[int] = None):
        if limit is None:
            tracks = self.db.query(models.DBTrack_Record).filter(models.DBTrack_Record.UID==user_id).all()
        else:
            tracks = self.db.query(models.DBTrack_Record).filter(models.DBTrack_Record.UID == user_id).limit(limit).all()

        result = []
        for track in tracks:
            result.append(TrackRecordDetailResponse(
                Id= int(track.Id),
                Timestamp= track.Timestamp,
                Duration= int(track.Duration),
                UID= int(track.UID),
                TID= int(track.TID),
                Track_Name=track.track_track_record.Name,
                Track_Image=track.track_track_record.Image,
                Artist_Name=track.track_track_record.artist_track.Name,
            ))
        return result

    @router.post("/sync/{user_id}", response_model=list[TrackRecordResponse])
    def sync_tracks(self, user_id: int):
        results = self.sp.current_user_recently_played(limit=50)
        timestamp = self.get_timestamp(user_id)
        saved = []


        for item in results["items"]:
            cleanplayed_at = item["played_at"][:19] # Cut off everything after seconds
            played_at = datetime.strptime(cleanplayed_at, "%Y-%m-%dT%H:%M:%S") # Turn the string into a correct Datetime

            if timestamp and played_at <= timestamp:# Check if already in db
                continue

            track = item["track"]
            artist = track["artists"][0]

            db_artist = self.db.query(models.DBArtist).filter(models.DBArtist.Spotify_id == artist["id"]).first()
            db_track = self.db.query(models.DBTrack).filter(models.DBTrack.Spotify_id == track["id"]).first()

            if not db_artist:
                db_artist = self.make_artist(artist)

            if not db_track:
                db_track = self.make_track(track, db_artist.Id)

            new_record = models.DBTrack_Record(
                Timestamp=played_at,
                Duration=track["duration_ms"],
                UID=user_id,
                TID=db_track.Id
            )
            self.db.add(new_record)
            saved.append(new_record)

        self.db.commit() # The objects get "stale" here so python doesn't know the id of the object yet
        for record in saved:
            self.db.refresh(record) # Now it asks for everything again - so now it knows the id

        return saved

    def get_timestamp(self, user_id: int):
        record = (self.db.query(models.DBTrack_Record)
            .filter(models.DBTrack_Record.UID == user_id)
            .order_by(models.DBTrack_Record.Timestamp.desc())
            .first())
        return record.Timestamp if record else None

    def make_artist(self, artist: dict):
        db_artist = models.DBArtist(
            Spotify_id=artist["id"],
            Name=artist["name"],
        )
        self.db.add(db_artist)
        self.db.flush()
        return db_artist

    def make_track(self, track: dict, aid: int):
        db_track = models.DBTrack(
            Spotify_id=track["id"],
            Name=track["name"],
            Image=track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            AID=aid
        )
        self.db.add(db_track)
        self.db.flush()  # Similar to a commit in git
        return db_track



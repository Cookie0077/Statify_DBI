from datetime import datetime
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
    Duration: float
    UID: int
    TID: int


class TrackRecordResponse(TrackRecordCreate):
    Id: int
    model_config = {"from_attributes": True}


@cbv(router)
class TrackRecordAPI(BaseAPI):
    db: Session = Depends(get_db)

    @router.get("/", response_model=list[TrackRecordResponse])
    def get_all(self):
        return self.db.query(models.DBTrack_Record).all()

    @router.get("/{id}", response_model=TrackRecordResponse)
    def get_one(self, id: int):
        return self.db.query(models.DBTrack_Record).filter(models.DBTrack_Record.Id == id).first()

    @router.post("/sync/{user_id}", response_model=list[TrackRecordResponse])
    def sync_tracks(self, user_id: int):
        results = self.sp.current_user_recently_played(limit=50)
        timestamp = self.get_timestamp(user_id)
        saved = []


        for item in results["items"]:
            cleanplayed_at = item["played_at"][:19]
            played_at = datetime.strptime(cleanplayed_at, "%Y-%m-%dT%H:%M:%S")

            if timestamp and played_at <= timestamp:# check if already in db
                continue

            track = item["track"]
            artist = track["artists"][0]

            db_artist = self.db.query(models.DBArtist).filter(models.DBArtist.Spotify_id == artist["id"]).first()
            db_track = self.db.query(models.DBTrack).filter(models.DBTrack.Spotify_id == track["id"]).first()

            if not db_artist:
                db_artist = models.DBArtist(
                    Spotify_id=artist["id"],
                    Name=artist["name"],
                )
                self.db.add(db_artist)
                self.db.flush()

            if not db_track:
                db_track = models.DBTrack(
                    Spotify_id=track["id"],
                    Name=track["name"],
                    Image=track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                    AID=db_artist.Id
                )
                self.db.add(db_track)
                self.db.flush()  # similiar to a commit in git

            new_record = models.DBTrack_Record(
                Timestamp=played_at,
                Duration=track["duration_ms"],
                UID=user_id,
                TID=db_track.Id
            )
            self.db.add(new_record)
            saved.append(new_record)

        self.db.commit()
        for record in saved:
            self.db.refresh(record)

        return saved

    def get_timestamp(self, user_id: int):
        record = (self.db.query(models.DBTrack_Record)
            .filter(models.DBTrack_Record.UID == user_id)
            .order_by(models.DBTrack_Record.Timestamp.desc())
            .first())
        return record.Timestamp if record else None
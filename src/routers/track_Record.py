import logging
from datetime import datetime
from typing import Optional
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import count

import models
from auth import verify_api_key
from database import get_db
from routers.base import BaseAPI
import helper

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/track_record", tags=["Track-Record"])


class TrackRecordCreate(BaseModel):
    Timestamp: datetime
    UID: int
    TID: int


class TrackRecordResponse(TrackRecordCreate):
    Id: int
    model_config = {"from_attributes": True}

class TrackRecordDetailResponse(TrackRecordResponse):
    Track_Name: str
    Track_Image: str
    Artist_Name: str
    URL: str
    Playcount: int


@cbv(router)
class TrackRecordAPI(BaseAPI):
    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)

    @router.get("/{user_id}", response_model=list[TrackRecordDetailResponse])
    def get_all(self, user_id: int, limit: Optional[int] = None):
        logger.info("GET /track_record/%s called", user_id)
        try:
            tracks = (
                self.db.query(
                    models.DBTrack_Record,
                    count(models.DBTrack_Record.TID).label("playcount")
                )
                .filter(models.DBTrack_Record.UID == user_id)
                .group_by(models.DBTrack_Record.TID)
                .order_by(count(models.DBTrack_Record.TID).desc())
                .limit(limit)
                .all()
            )

            result = []
            for track, playcount in tracks:
                result.append(TrackRecordDetailResponse(
                    Id=int(track.Id),
                    Timestamp=track.Timestamp,
                    Duration=int(track.track_track_record.Duration),
                    UID=int(track.UID),
                    TID=int(track.TID),
                    Track_Name=track.track_track_record.Name,
                    Track_Image=track.track_track_record.Image,
                    Artist_Name=track.track_track_record.artist_track.Name,
                    URL=track.track_track_record.URL,
                    Playcount=playcount,
                ))
            return result
        except Exception as e:
            logger.error("Error getting tracks: %s", str(e))
            raise HTTPException(status_code=500, detail="Error getting tracks")

    @router.post("/sync/{user_id}", response_model=list[TrackRecordResponse])
    def sync_tracks_and_artists(self, user_id: int):
        logger.info("POST /track_record/sync/%s called", user_id)
        try:
            results = self.sp.current_user_recently_played(limit=50)
            timestamp = helper.get_timestamp(self.db,user_id)
            saved = []

            for item in results["items"]:
                cleanplayed_at = item["played_at"][:19]  # Cut off everything after seconds
                played_at = datetime.strptime(cleanplayed_at,
                                              "%Y-%m-%dT%H:%M:%S")  # Turn the string into a correct Datetime

                if timestamp and played_at <= timestamp:  # Check if already in db
                    continue

                track = item["track"]
                artist = track["artists"][0]


               # TODO: Instead of sp.artist try sp.artists again - mby its fixable

                db_artist =helper.make_artist(self.db,self.sp, artist)
                db_track = helper.make_track(self.db, track,db_artist.Id)

                new_record = models.DBTrack_Record(
                    Timestamp=played_at,
                    UID=user_id,
                    TID=db_track.Id
                )
                self.db.add(new_record)  # Saves the new_record in the python memory (nothing to db yet)
                saved.append(new_record)

            self.db.commit()  # The objects get "stale" here so python doesn't know the id of the object yet
            for record in saved:
                self.db.refresh(record)  # Now it asks for everything again - so now it knows the id
            return saved
        except Exception as e:
            logger.error("Error syncing tracks for user %s: %s", user_id, str(e))
            raise HTTPException(status_code=500, detail="Error getting tracks")


    # TODO: Make GET per Day stats route

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import count
import helper
import models
from auth import verify_api_key
from database import get_db
from routers.base import BaseAPI
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/artist", tags=["Artist"])


class ArtistCreate(BaseModel):
    Name: str
    Spotify_id: str
    Image: str | None
    URL: str | None

    model_config = {"from_attributes": True}


class ArtistResponse(ArtistCreate):
    Id: int


class ArtistDetailResponse(ArtistResponse):
    Playtime: int


@cbv(router)
class Artist(BaseAPI):
    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)

    @router.get("/{user_id}", response_model=list[ArtistDetailResponse])
    def get_artists(self, user_id: int, limit: Optional[int] = None):
        logger.info("GET /artist/%s called", user_id)
        try:
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

            playtimes = [helper.get_playtime(self.db,user_id, artist.Id) for artist in artists]
            result = []

            for i in range(len(artists)):
                artist = artists[i]
                playtime = playtimes[i]

                result.append(ArtistDetailResponse(
                    Id=artist.Id,
                    Name=artist.Name,
                    Spotify_id=artist.Spotify_id,
                    Image=artist.Image,
                    URL=artist.URL,
                    Playtime=playtime or 0
                ))

            return result
        except Exception as e:
            logger.error("Error syncing tracks for user %s: %s", user_id, str(e))
            raise HTTPException(status_code=500, detail="Error getting artists")

    @router.delete("/{artist_id}", response_model=ArtistDetailResponse)
    def delete_artist(self, artist_id: int):
        logger.info("DELETE /artist/%s called", artist_id)
        try:
            deleted_artist = self.db.query(models.DBArtist).get(artist_id)
            self.db.delete(deleted_artist)
            self.db.commit()
            return ArtistDetailResponse(Id=deleted_artist.Id, Name=deleted_artist.Name,
                                        Spotify_id=deleted_artist.Spotify_id, Image=deleted_artist.Image,
                                        URL=deleted_artist.URL)
        except Exception as e:
            logger.error("Error deleting artist %s: %s", artist_id, str(e))
            raise HTTPException(status_code=500, detail="Error deleting artist")
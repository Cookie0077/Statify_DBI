import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

import helper
import models
from auth import verify_api_key
from database import get_db
from models import DBPlaylist, DBPlaylist_Track
from routers.base import BaseAPI
from routers.track import TrackResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/playlist", tags=["Playlist"])


class PlalistCreate(BaseModel):
    Name: str
    Image: str
    Spotify_id: str
    URL: str
    UID: int


class PlalistResponse(PlalistCreate):
    Id: int


@cbv(router)
class PlaylistAPI(BaseAPI):
    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)

    @router.post("/sync/{user_id}")
    def GetPlaylistfromAPI(self, user_id: int):
        logger.info("POST /playlist/sync/%s called", user_id)
        try:
            playlists = self.sp.current_user_playlists()
            current_user = self.sp.current_user()
            for playlist in playlists["items"]:
                if playlist["owner"]["id"] != current_user["id"]:
                    continue

                existing_playlist = self.db.query(models.DBPlaylist).filter(
                    models.DBPlaylist.Spotify_id == playlist["id"]).first()
                if not existing_playlist:
                    db_playlist = DBPlaylist(
                        Name=playlist["name"],
                        Spotify_id=playlist["id"],
                        UID=user_id,
                        Image=playlist["images"][0]["url"],
                        URL=playlist["external_urls"]["spotify"],
                    )

                    self.db.add(db_playlist)

            self.db.commit()
            return {"message": "Playlist successfully added"}
        except Exception as e:
            logger.error("Error adding playlist: %s", str(e))
            raise HTTPException(status_code=500, detail="Error adding playlist")

    @router.post("/sync/{playlist_id}/tracks")
    def ADD_GET_Tracks_from_Playlist(self, playlist_id: int):
        logger.info("POST /playlist/%s/tracks called", playlist_id)
        try:
            DBPlaylist = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.Id == playlist_id).first()
            if not DBPlaylist:
                raise HTTPException(status_code=404, detail="Playlist not found")

            count = self.db.query(models.DBPlaylist_Track).filter(DBPlaylist_Track.PID == playlist_id).count()
            results = self.sp.playlist_items(DBPlaylist.Spotify_id, offset=count, limit=100)


            while results:
                for item in results["items"]:
                    if not item or not item.get("item"):
                        continue

                    track = item["item"]
                    existing_track = self.db.query(models.DBTrack).filter(models.DBTrack.Spotify_id == track["id"]).first()
                    if not existing_track:
                        artist = helper.make_artist(self.db, self.sp, track["artists"][0])
                        existing_track = helper.make_track(self.db, track, artist.Id)

                    db_track_playlist = models.DBPlaylist_Track(TID=existing_track.Id, PID=playlist_id)
                    self.db.add(db_track_playlist)

                self.db.commit()
                if results["next"]:
                    time.sleep(0.1)
                    results = self.sp.next(results)
                else:
                    results = None


            return {"message": "Tracks successfully added"}
        except Exception as e:
            logger.error("Error adding tracks: %s", str(e))
            raise HTTPException(status_code=500, detail="Error adding tracks")

    @router.get("/{playlist_id}/tracks", response_model=list[TrackResponse])
    def Get_Tracks_from_Playlist(self, playlist_id: int, offset: Optional[int] = None):
        logger.info("GET /playlist/%s/tracks called", playlist_id)
        try:
            tracks = (
                self.db.query(models.DBTrack)
                .join(models.DBPlaylist_Track, models.DBPlaylist_Track.TID == models.DBTrack.Id)
                .filter(models.DBPlaylist_Track.PID == playlist_id)
                .offset(offset)
                .limit(50)
                .all()
            )
            return tracks
        except Exception as e:
            logger.error("Error getting tracks: %s", str(e))
            raise HTTPException(status_code=500, detail="Error getting tracks")
    @router.get("/{user_id}", response_model=list[PlalistResponse])
    def Get_Playlists(self, user_id: int):
        logger.info("GET /playlist/%s called", user_id)
        try:
            playlists = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.UID == user_id).all()
            return playlists
        except Exception as e:
            logger.error("Error getting playlists: %s", str(e))
            raise HTTPException(status_code=500, detail="Error getting playlists")

    @router.delete("/{playlist_id}", response_model=PlalistResponse)
    def Delete_Playlists(self, playlist_id: int):
        logger.info("DELETE /playlist/%s called", playlist_id)
        try:
            deletd_playlist = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.Id == playlist_id).first()
            self.db.delete(deletd_playlist)
            self.db.commit()
            return PlalistResponse(Id=deletd_playlist.Id, Name=deletd_playlist.Name, Spotify_id=deletd_playlist.Spotify_id,
                                   Image=deletd_playlist.Image, URL=deletd_playlist.URL, UID=deletd_playlist.UID)
        except Exception as e:
            logger.error("Error deleting playlist: %s", str(e))
            raise HTTPException(status_code=500, detail="Error deleting playlist")
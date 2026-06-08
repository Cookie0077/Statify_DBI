from os import name
from typing import Optional

import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator, Field
from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import count

import models
from auth import verify_api_key
from database import get_db
from models import DBPlaylist
from routers.base import BaseAPI
from track import TrackResponse




router = APIRouter(prefix="/playlist", tags=["Playlist"])


class PlalistCreate(BaseModel):
    Name: str
    Image: str
    Spotify_id: str
    UID:int

class PlalistResponse(PlalistCreate):
    Id: int

@cbv(router)
class PlaylistAPI(BaseAPI):

    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)
    @router.post("/{user_id}")
    def GetPlaylistfromAPI(self,user_id: int):
        playlists = self.sp.current_user_playlists()
        for playlist in playlists["items"]:

            existing_playlist = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.Spotify_id == playlist["id"]).first()
            if not existing_playlist:
                db_playlist = DBPlaylist(
                    Name=playlist["name"],
                    Spotify_id=playlist["id"],
                    UID=user_id,
                    Image=playlist["images"][0]["url"],
                )

                self.db.add(db_playlist)

        self.db.commit()
        return {"message":"Playlist successfully added"}


    def AddTracksfromPlaylist(self,DBPlaylist):
        Tracks = self.sp.Playlist_Tracks(DBPlaylist.Spotify_id)
        for track in Tracks["items"]:
           existing_track = self.db.query(models.DBTrack).filter(models.DBTrack.Spotify_id == track["id"]).first()
           if not existing_track:
               # TODO: Hier die make Track methode von Trakc records machen

            db_track_playlist =models.DBPlaylist_Track(TID=existing_track.id,PID=DBPlaylist.Id)
            self.db.add(db_track_playlist)
            self.db.commit()
            return db_track_playlist

    @router.get("/{user_id}",response_model=list[PlalistResponse])
    def GetPlaylist(self,user_id: int):
        playlists = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.UID == user_id).all()
        return playlists

    @router.get("/{playlist_id]}",response_model=list[TrackResponse])
    def GetTracksfromPlaylist(self,playlist_id: int):
        Tracks = self.db.query(models.DBTrack).filter(models.DBPlaylist_Track.PID == playlist_id).all()

        return Tracks
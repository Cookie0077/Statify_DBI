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




router = APIRouter(prefix="/playlist", tags=["Playlist"])


class PlalistCreate(BaseModel):
    Name: str
    Image: str
    Spotify_id: str
    Total_Tracks:int = Field(...,gt=0)
    UID:int

class PlalistResponse(PlalistCreate):
    id: int

@cbv(router)
class PlaylistAPI(BaseAPI):

    db: Session = Depends(get_db)
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




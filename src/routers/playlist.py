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
from models import DBPlaylist, DBPlaylist_Track
from routers.base import BaseAPI
from routers.track import TrackResponse
import helper




router = APIRouter(prefix="/playlist", tags=["Playlist"])


class PlalistCreate(BaseModel):
    Name: str
    Image: str
    Spotify_id: str
    URL: str
    UID:int

class PlalistResponse(PlalistCreate):
    Id: int

@cbv(router)
class PlaylistAPI(BaseAPI):

    db: Session = Depends(get_db)
    api_key: str = Depends(verify_api_key)
    @router.post("/sync/{user_id}")
    def GetPlaylistfromAPI(self,user_id: int):
        playlists = self.sp.current_user_playlists()
        current_user = self.sp.current_user()
        for playlist in playlists["items"]:
            if playlist["owner"]["id"] != current_user["id"]:
                continue


            existing_playlist = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.Spotify_id == playlist["id"]).first()
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
        return {"message":"Playlist successfully added"}


    @router.post("/sync/{playlist_id}/tracks",response_model=list[TrackResponse])
    def ADD_GET_TracksfromPlaylist(self,playlist_id: int):
        result =[]
        DBPlaylist = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.Id == playlist_id).first()
        count = self.db.query(models.DBPlaylist_Track).filter(DBPlaylist_Track.PID == playlist_id).count()
        Items = self.sp.playlist_items(DBPlaylist.Spotify_id, offset=count, limit=100)
        for item in Items["items"]:
            if not item or not item.get("item"):
                continue

            track = item["item"]
            existing_track = self.db.query(models.DBTrack).filter(models.DBTrack.Spotify_id == track["id"]).first()
            if not existing_track:
              artist =  helper.make_artist(self.db,self.sp, track["artists"][0])
              existing_track= helper.make_track(self.db,track,artist.Id)

            db_track_playlist =models.DBPlaylist_Track(TID=existing_track.Id,PID=DBPlaylist.Id)
            self.db.add(db_track_playlist)
            DBtrack = TrackResponse(Name=existing_track.Name,Id=existing_track.Id,Spotify_id=existing_track.Spotify_id,Image=existing_track.Image,URL=existing_track.URL,AID=existing_track.AID)
            result.append(DBtrack)
        self.db.commit()

        return result


    @router.get("/{user_id}",response_model=list[PlalistResponse])
    def GetPlaylists(self,user_id: int):
        playlists = self.db.query(models.DBPlaylist).filter(models.DBPlaylist.UID == user_id).all()
        return playlists

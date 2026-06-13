from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database import Base


class DBUser(Base):
    __tablename__ = "Users"
    Id = Column(Integer, primary_key=True)
    Name = Column(String, index=True)
    Password = Column(String, index=True)
    Image = Column(String, index=True, nullable=True)
    Role_user = relationship("DBRole", back_populates="user_Roles")
    track_User = relationship("DBTrack_Record", back_populates="user_track_record")
    user_playlist = relationship("DBPlaylist", back_populates="playlist_user")


class DBRole(Base):
    __tablename__ = "Role"
    Id = Column(Integer, primary_key=True)
    Role = Column(String, index=True)
    UID = Column(Integer, ForeignKey("Users.Id"), index=True)
    CanGet = Column(Boolean, index=True)
    CanPost = Column(Boolean, index=True)
    CanDelete = Column(Boolean, index=True)
    user_Roles = relationship("DBUser", back_populates="Role_user")


class DBTrack_Record(Base):
    __tablename__ = "Track_Records"
    Id = Column(Integer, primary_key=True)
    Timestamp = Column(DateTime, index=True)
    Duration = Column(Integer, index=True)
    UID = Column(Integer, ForeignKey("Users.Id"), index=True)
    TID = Column(Integer, ForeignKey("Track.Id"), index=True)

    user_track_record = relationship("DBUser", back_populates="track_User")
    track_track_record = relationship("DBTrack", back_populates="track_record")


class DBTrack(Base):
    __tablename__ = "Track"
    Id = Column(Integer, primary_key=True)
    Spotify_id = Column(String, index=True)
    Name = Column(String, index=True)
    Image = Column(String, index=True)
    URL = Column(String, index=True)
    AID = Column(Integer, ForeignKey("Artists.Id"))

    artist_track = relationship("DBArtist", back_populates="track_artist")
    track_record = relationship("DBTrack_Record", back_populates="track_track_record")
    track_playlist = relationship("DBPlaylist_Track", back_populates="playlist_track")


class DBArtist(Base):
    __tablename__ = "Artists"
    Id = Column(Integer, primary_key=True)
    Spotify_id = Column(String, index=True)
    Name = Column(String, index=True)
    Image = Column(String, index=True, nullable=True)
    URL = Column(String, index=True)
    track_artist = relationship("DBTrack", back_populates="artist_track")


class DBPlaylist_Track(Base):
    __tablename__ = "Playlist_Tracks"
    Id = Column(Integer, primary_key=True)
    TID = Column(Integer, ForeignKey("Track.Id"), index=True)
    PID = Column(Integer, ForeignKey("Playlists.Id"), index=True)

    playlist_track = relationship("DBTrack", back_populates="track_playlist")
    playlist_playlist_track = relationship("DBPlaylist", back_populates="playlist_track")


class DBPlaylist(Base):
    __tablename__ = "Playlists"
    Id = Column(Integer, primary_key=True)
    Spotify_id = Column(String, index=True)
    Name = Column(String, index=True)
    Image = Column(String, index=True)
    URL = Column(String, index=True)
    UID = Column(Integer, ForeignKey("Users.Id"), index=True)

    playlist_user = relationship("DBUser", back_populates="user_playlist")
    playlist_track = relationship("DBPlaylist_Track", back_populates="playlist_playlist_track")

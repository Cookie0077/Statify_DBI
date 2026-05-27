from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class DBUser(Base):
    __tablename__ = "Users"
    Id = Column(Integer, primary_key=True)
    Name = Column(String, index=True)
    Spotify_id = Column(String, index=True)
    Password = Column(String, index=True)


    settings_user = relationship("DBUser_Settings", back_populates="user_setting")
    track_User = relationship("DBTrack_Record", back_populates="user_track_record")


class DBUser_Settings(Base):
    __tablename__ = "User_Settings"
    Id = Column(Integer, primary_key=True)
    Spotify_token = Column(String, index=True)
    Role = Column(String, index=True)
    UID = Column(Integer, ForeignKey("Users.UID"), index=True)

    user_setting = relationship("DBUser", back_populates="settings_user")


class DBTrack_Record(Base):
    __tablename__ = "Track_Records"
    Id = Column(Integer, primary_key=True)
    Timestamp = Column(DateTime, index=True)
    Duration = Column(Float, index=True)
    UID = Column(Integer, ForeignKey("Users.UID"), index=True)
    TID = Column(Integer, ForeignKey("Track.TID"), index=True)

    user_track_record = relationship("DBUser", back_populates="track_User")
    track_track_record = relationship("DBTrack", back_populates="track_record")


class DBTrack(Base):
    __tablename__ = "Track"
    Id = Column(Integer, primary_key=True)
    Spotify_id = Column(String, index=True)
    Name = Column(String, index=True)
    Image = Column(String, index=True)
    AID = Column(Integer, ForeignKey("Artists.AID"))

    artist_track = relationship("DBArtist", back_populates="track_artist")
    track_record = relationship("DBTrack_Record", back_populates="track_track_record")
    track_playlist = relationship("DBPlaylist_Track", back_populates="playlist_track")


class DBArtist(Base):
    __tablename__ = "Artists"
    Id = Column(Integer, primary_key=True)
    Spotify_id = Column(String, index=True)
    Name = Column(String, index=True)
    Follower_count = Column(Integer, index=True)

    track_artist = relationship("DBTrack", back_populates="artist_track")
    artist_genres = relationship("DBArtist_Genre", back_populates="artist_genre")


class DBArtist_Genre(Base):
    __tablename__ = "Artist_Genre"
    Id = Column(Integer, primary_key=True)
    AID = Column(Integer, ForeignKey("Artists.AID"), index=True)
    GID = Column(Integer, ForeignKey("Genre.GID"), index=True)

    artist_genre = relationship("DBArtist", back_populates="artist_genres")
    genre_artist = relationship("DBGenre", back_populates="genre_artists")


class DBGenre(Base):
    __tablename__ = "Genre"
    Id = Column(Integer, primary_key=True)
    Name = Column(String, index=True)

    genre_artists = relationship("DBArtist_Genre", back_populates="genre_artist")


class DBPlaylist_Track(Base):
    __tablename__ = "Playlist_Tracks"
    Id = Column(Integer, primary_key=True)
    TID = Column(Integer, ForeignKey("Track.TID"), index=True)
    PID = Column(Integer, ForeignKey("Playlists.PID"), index=True)

    playlist_track = relationship("DBTrack", back_populates="track_playlist")
    playlist_playlist_track = relationship("DBPlaylist", back_populates="playlist_track")


class DBPlaylist(Base):
    __tablename__ = "Playlists" 
    Id = Column(Integer, primary_key=True)
    Spotify_id = Column(String, index=True)
    Name = Column(String, index=True)
    Follower_count = Column(Integer, index=True)
    Owner = Column(String, index=True)

    playlist_track = relationship("DBPlaylist_Track", back_populates="playlist_playlist_track")
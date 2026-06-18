from passlib.context import CryptContext

import models


def make_artist(db,sp,artist: dict):
    db_artist = db.query(models.DBArtist).filter(models.DBArtist.Spotify_id == artist["id"]).first()
    if db_artist:
        return db_artist
    newartist = sp.artist(artist["id"])

    image = newartist["images"][0]["url"] if newartist["images"] else None

    db_artist = models.DBArtist(
        Spotify_id=artist["id"],
        Name=artist["name"],
        Image=image,
        URL=artist["external_urls"]["spotify"]
    )
    db.add(db_artist)
    db.flush()
    return db_artist


def make_track(db, track: dict, aid: int):
    db_track = db.query(models.DBTrack).filter(models.DBTrack.Spotify_id == track["id"]).first()
    if db_track:
        return db_track

    image = track["album"]["images"][0]["url"] if track["album"]["images"] else None
    db_track = models.DBTrack(
        Spotify_id=track["id"],
        Name=track["name"],
        Image=image,
        Duration=track["duration_ms"],
        URL=track["external_urls"]["spotify"],
        AID=aid
    )
    db.add(db_track)
    db.flush()
    return db_track


def get_playtime(db, user_id: int, artist_id: int) -> int:
    playtime = 0

    tracks = (
        db.query(models.DBTrack)
        .join(models.DBTrack_Record, models.DBTrack_Record.TID == models.DBTrack.Id)
        .filter(models.DBTrack_Record.UID == user_id)
        .filter(models.DBTrack.AID == artist_id)
        .all())
    if tracks:
        for curPlaytime in tracks:
            playtime += curPlaytime.Duration

    return playtime


def get_timestamp(db, user_id: int):
    record = (db.query(models.DBTrack_Record)
              .filter(models.DBTrack_Record.UID == user_id)
              .order_by(models.DBTrack_Record.Timestamp.desc())
              .first())
    return record.Timestamp if record else None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


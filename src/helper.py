import models


def make_artist(db, sp, artist: dict):
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
    image = track["album"]["images"][0]["url"] if track["album"]["images"] else None
    db_track = models.DBTrack(
        Spotify_id=track["id"],
        Name=track["name"],
        Image=image,
        URL=track["external_urls"]["spotify"],
        AID=aid
    )
    db.add(db_track)
    db.flush()
    return db_track


def get_playtime(self, user_id: int, artist_id: int) -> int:
    playtime = 0

    tracks = (
        self.db.query(models.DBTrack_Record)
        .join(models.DBTrack, models.DBTrack_Record.TID == models.DBTrack.Id)
        .filter(models.DBTrack_Record.UID == user_id)
        .filter(models.DBTrack.AID == artist_id)
        .all())
    if tracks:
        for curPlaytime in tracks:
            playtime += curPlaytime.Duration

    return playtime


def get_timestamp(self, user_id: int):
    record = (self.db.query(models.DBTrack_Record)
              .filter(models.DBTrack_Record.UID == user_id)
              .order_by(models.DBTrack_Record.Timestamp.desc())
              .first())
    return record.Timestamp if record else None

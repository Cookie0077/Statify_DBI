import models


def make_artist(db,sp,artist: dict):
    newartist = sp.artist(artist["id"])

    image = newartist["images"][0]["url"] if newartist["images"] else None

    db_artist = models.DBArtist(
        Spotify_id=artist["id"],
        Name = artist["name"],
        Image = image
    )
    db.add(db_artist)
    db.flush()
    return db_artist

def make_track(db, track: dict, aid: int):
    db_track = models.DBTrack(
        Spotify_id=track["id"],
        Name=track["name"],
        Image=track["album"]["images"][0]["url"] if track["album"]["images"] else None,
        AID=aid
    )
    db.add(db_track)
    db.flush()
    return db_track
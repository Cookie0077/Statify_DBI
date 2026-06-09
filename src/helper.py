import models

def make_track(db, artist: dict):
    db_artist = models.DBArtist(
        Spotify_id=artist["id"],
        Name=artist["name"]
    )
    db.add(db_artist)
    db.flush()
    return db_artist


from email.mime import image

import models


def make_artist(db,sp,artist: dict):
    newartist = sp.artist(artist["id"])

    image = newartist["images"][0]["url"] if newartist["images"] else None

    db_artist = models.DBArtist(
        Spotify_id=artist["id"],
        Name = artist["name"],
        Image = image,
        URL =artist["external_urls"]["spotify"]
    )
    db.add(db_artist)
    db.flush()
    return db_artist

def make_track(db, track: dict, aid: int):
    image =track["album"]["images"][0]["url"] if track["album"]["images"] else None
    db_track = models.DBTrack(
        Spotify_id=track["id"],
        Name=track["name"],
        Image=  image,
        URL=track["external_urls"]["spotify"],
        AID=aid
    )
    db.add(db_track)
    db.flush()
    return db_track
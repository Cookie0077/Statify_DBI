from spotipy.oauth2 import SpotifyOAuth
import spotipy


# TODO: client_id and client_secret a .env file (.env file also in gitignore)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="1549b84275a94fb2892effbc257c06a3",
    client_secret="643062d2510446969d16dea9b9c53eba",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-recently-played user-top-read playlist-read-private"
))

sp.current_user()
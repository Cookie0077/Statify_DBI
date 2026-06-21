## Anleitung um die App zu starten

1. Bei **src** das .env file erstellen. (ist im .zip schon dabei)
2. Python Interpreter konfigurieren und requirements installieren
3. App über *main.py* starten
4. Spotify Account anmelden und zustimmen
5. http://127.0.0.1:8888/docs aufrufen
6. Oben bei *Authorize* bei **APIKeyHeader**: **STATIKEY** eingeben
7. Dann über den **POST - user/register** Endpoint einen neuen User erstellen
8. Danach wieder beim *Authorize* bei **OAuth2PasswordBearer** sich mit dem gewählten Passwort und Username anmelden
9. Um die DB zu befüllen danach
- *POST - track_record/sync* 
- *POST - playlist/sync*
10. (Optional) *POST - playlist/sync/{playlist_id}/tracks* runnen um bei den jeweiligen Playlists die Songs zu adden
11. Danach ausprobieren was man möchte :)
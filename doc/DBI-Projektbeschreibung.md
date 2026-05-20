#dbi 
## Projektbeschreibung

In unsere App sollte man seine eigenen Spotify Statistiken anschauen können. Dafür werden, falls vorhanden, die Daten aus unserer eigenen DB geladen. Man kann auch refreshen dann wird von der API neue Daten geholt. So kann man dann für die Wochen die Statistiken anschauen wie:
- Anzahl angehörter Minuten
- Meist angehörte/r...
    - Artist
    - Genres
    - Playlists

In unserem Mainwindow sieht man eine grobe Übersicht über ein paar spannende Daten. Über unsere Nav-Bar kann man genauere Daten anschauen wie meist gehörte Artists, Genres, etc...

## Must-Haves

- Dashboard mit Grunddaten
- Statistiken
- Verschieden Tabs
- Data Crunching! -> Wie speichere ich Daten und was kann ich herauslesen!
- Userhandling - DB abspeichern

## Nice-To-Haves

- Userhandling - Mit Spotify-Account 
- Über unsere App direkt in Spotify auf die Lieder zugreifen
- Informationen über Künstler, Songs, etc... als Unterfenster 
- Automatisches Refreschen der Daten
- Filter für Stats

## Domäne & Entitäten

Das System verwaltet folgende Entitäten:

| Entität          | Beschreibung                                                                                        |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| `User`           | Spotify-Nutzer mit ID und Name                                                                      |
| `User_Settings`  | Token, Rolle und Einstellungen eines Users (1:1 zu User)                                            |
| `Track_Record`   | Jeder einzelne Hörvorgang – verbindet User und Track, speichert Timestamp und tatsächliche Duration |
| `Track`          | Ein Song mit Spotify-ID, Name, Bild und Basisdauer                                                  |
| `Artist`         | Künstler mit Spotify-ID, Name und Followeranzahl                                                    |
| `Genre`          | Musikgenre – wird über Artists zugeordnet                                                           |
| `Playlist`       | Playlist mit Spotify-ID, Name, Owner und Followerzahl                                               |
| `Playlist_Track` | Zwischentabelle für m:n zwischen Playlist und Track                                                 |
| `Artist_Genre`   | Zwischentabelle für m:n zwischen Artist und Genre                                                   |

## ERM & RM
![[ERM-RM-Projektbeschreibung.png]]

## Normalformen

Alle Tabellen erfüllen die 1., 2. und 3. Normalform:

**1NF** – Jede Spalte enthält nur atomare (unteilbare) Werte, es gibt keine Wiederholungsgruppen und jede Zeile ist durch einen Primärschlüssel eindeutig identifizierbar. Alle unsere Tabellen sind so aufgebaut – z.B. speichert `Track_Record` pro Hörvorgang genau einen Timestamp und eine Duration, nicht eine Liste davon.

**2NF** – Alle Nicht-Schlüssel-Attribute sind voll funktional abhängig vom gesamten Primärschlüssel (relevant bei zusammengesetzten PKs). 

**3NF** – Es gibt keine transitiven Abhängigkeiten zwischen Nicht-Schlüssel-Attributen. Zum Beispiel: `Follower_count` in `Artist` hängt direkt von `AID` ab, nicht von einem anderen Nicht-Schlüssel-Attribut. Berechnete Werte wie "Gesamtminuten" werden gar nicht gespeichert, sondern per SQL aus `Track_Record` abgeleitet.

## API-Endpunkte

### Track_Record

|Methode|Pfad|Bedeutung|Auth|
|---|---|---|---|
|GET|`/records`|Alle Hörvorgänge auflisten|user, admin|
|GET|`/records/{id}`|Einzelnen Hörvorgang abrufen|user, admin|
|POST|`/records`|Neuen Hörvorgang anlegen|user, admin|
|PUT|`/records/{id}`|Hörvorgang aktualisieren|admin|
|DELETE|`/records/{id}`|Hörvorgang löschen|admin|

### Tracks

|Methode|Pfad|Bedeutung|Auth|
|---|---|---|---|
|GET|`/tracks`|Alle Tracks|user, admin|
|GET|`/tracks/{id}`|Track mit Artistname (JOIN)|user, admin|
|POST|`/tracks`|Track anlegen|admin|
|PUT|`/tracks/{id}`|Track aktualisieren|admin|
|DELETE|`/tracks/{id}`|Track löschen|admin|

### Artists

|Methode|Pfad|Bedeutung|Auth|
|---|---|---|---|
|GET|`/artists`|Alle Artists|user, admin|
|GET|`/artists/{id}`|Artist mit seinen Tracks (JOIN)|user, admin|
|POST|`/artists`|Artist anlegen|admin|
|PUT|`/artists/{id}`|Artist aktualisieren|admin|
|DELETE|`/artists/{id}`|Artist löschen|admin|

### Statistiken 

| Methode | Pfad                      | Beschreibung               |
| ------- | ------------------------- | -------------------------- |
| GET     | `/stats/top-artists`      | Top-Artists nach Höranzahl |
| GET     | `/stats/minutes-per-user` | Gesamtminuten pro User     |
| GET     | `/stats/top-tracks`       | Meistgehörte Tracks        |
| GET     | `/stats/top-genres`       | Meistgehörte Genres        |

### Weitere Ressourcen

| Methode | Pfad              | Bedeutung                            |
| ------- | ----------------- | ------------------------------------ |
| GET     | `/playlists`      | Alle Playlists                       |
| GET     | `/playlists/{id}` | Playlist inkl. Tracks (JOIN)         |
| GET     | `/genres`         | Alle Genres                          |
| GET     | `/users`          | Alle User                            |
| GET     | `/users/{id}`     | User inkl. Settings und Rolle (JOIN) |
## Rollen

| Rolle   | Erlaubte Methoden      |
| ------- | ---------------------- |
| `admin` | GET, POST, PUT, DELETE |
| `user`  | nur GET & POST         |


## Aufgabenverteilung DBI

| Wer     | Was                                               | Dauer      |
| ------- | ------------------------------------------------- | ---------- |
| Jonas   | ERM & RM entwerfen                                | 1–2 Tage   |
| Dominik | Projektbeschreibung (so Rest :)                   | 1–2 Tage   |
| Jonas   | Routers: `tracks.py`, `genres.py`, `stats.py`     | 1–2 Wochen |
| Dominik | Routers: `artists.py`, `playlists.py`, `users.py` | 1–2 Wochen |
| beide   | Validierung, Logging, Rollen, Tests               | 1 Woche    |
| beide   | Dokumentation & Präsentation                      | 1 Woche    |


## GIT-Repository
`https://github.com/Cookie0077/Statify_DBI.git`
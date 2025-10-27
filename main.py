import config
import requests
import time
import threading
import json
import os

from rpc import DiscordRPC

if config.METADATA_PROVIDER.upper() == "SPOTIFY":
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials


class PersistentStore:
    data = {}
    has_loaded = False
    lock = threading.RLock()
    filename = os.path.join(os.path.dirname(__file__), "images.json")

    @classmethod
    def get(cls, key):
        if not cls.has_loaded:
            cls.load()

        return cls.data.get(key)

    @classmethod
    def set(cls, key, value):
        if not cls.has_loaded:
            cls.load()

        with cls.lock:
            cls.data[key] = value
            cls.save()

    @classmethod
    def has(cls, key):
        if not cls.has_loaded:
            cls.load()

        return key in cls.data

    @classmethod
    def load(cls):
        try:
            with open(cls.filename) as file:
                cls.data = json.load(file)
        except FileNotFoundError:
            cls.data = {}

        cls.has_loaded = True

    @classmethod
    def save(cls):
        with cls.lock:
            with open(cls.filename + ".tmp", "w") as file:
                file.write(json.dumps(cls.data))

            os.replace(cls.filename + ".tmp", cls.filename)


class CurrentTrack:
    id = None
    album_id = None

    title = None
    artist = None
    album = None

    started_at = None
    ends_at = None

    image_url = None

    spotify_client = None
    if config.METADATA_PROVIDER.upper() == "SPOTIFY":
        try:
            if not config.SPOTIFY_CLIENTID or not config.SPOTIFY_CLIENTSECRET:
                print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set")
            else:
                auth_manager = SpotifyClientCredentials(
                    client_id=config.SPOTIFY_CLIENTID,
                    client_secret=config.SPOTIFY_CLIENTSECRET
                )
                spotify_client = spotipy.Spotify(auth_manager=auth_manager)
                print("Spotify metadata provider initialized")
        except Exception as e:
            print(f"Failed to initialize Spotify client: {e}")

    def _filter_nowplaying(entry):
        return [
            player
            for player in entry
            if player["username"] == config.NAVIDROME_USERNAME
        ]

    @classmethod
    def set(cls, skip_none_check=False, **kwargs):
        image_url = kwargs.get("image_url")
        cls.image_url = image_url

        id = kwargs.get("id")
        duration = kwargs.get("duration")
        artist = kwargs.get("artist")
        album = kwargs.get("album")
        title = kwargs.get("title")
        album_id = kwargs.get("album_id")

        if (
            None in [id, duration, artist, album, title, album_id]
            and not skip_none_check
        ):
            return

        if id == cls.id:
            return

        cls.id = id
        cls.album_id = album_id
        cls.title = title
        cls.artist = artist
        cls.album = album
        cls.started_at = time.time()
        cls.ends_at = cls.started_at + (duration or 0)

    @classmethod
    def _grab_subsonic(cls):
        res = requests.get(
            f"{config.NAVIDROME_SERVER}/rest/getNowPlaying",
            params={
                "u": config.NAVIDROME_USERNAME,
                "p": config.NAVIDROME_PASSWORD,
                "f": "json",
                "v": "1.13.0",
                "c": "navicord",
            },
        )

        if res.status_code != 200:
            print("There was an error getting now playing: ", res.text)
            return

        try:
            json = res.json()["subsonic-response"]
        except:
            print("There was an error parsing subsonic response: ", res.text)
            return

        if len(json["nowPlaying"]) == 0:
            cls.set(skip_none_check=True)
            return

        if json["status"] == "ok" and len(json["nowPlaying"]) > 0:
            nowPlayingEntry = json["nowPlaying"]["entry"]
            nowPlayingList = cls._filter_nowplaying(nowPlayingEntry)

            if len(nowPlayingList) == 0:
                cls.set(skip_none_check=True)
                return

            nowPlaying = nowPlayingList[0]

            cls.set(
                id=nowPlaying["id"],
                duration=nowPlaying["duration"],
                artist=nowPlaying["artist"],
                album=nowPlaying["album"],
                title=nowPlaying["title"],
                album_id=nowPlaying["albumId"],
            )

    @classmethod
    def _grab_lastfm(cls):
        if PersistentStore.has(cls.album_id):
            cls.set(image_url=PersistentStore.get(cls.album_id))
            return

        res = requests.get(
            "https://ws.audioscrobbler.com/2.0/",
            params={
                "method": "album.getinfo",
                "api_key": config.LASTFM_API_KEY,
                "artist": cls.artist,
                "album": cls.album,
                "format": "json",
            },
        )

        if res.status_code == 200:
            image_url = res.json()["album"]["image"][3]["#text"]

            if image_url == "":
                cls.set(image_url=None)
                return

            cls.set(
                image_url=image_url,
            )

            PersistentStore.set(cls.album_id, image_url)


    @classmethod
    def _grab_spotify(cls):
        if not cls.spotify_client:
            print("Spotify client not initialized")
            return

        if PersistentStore.has(cls.album_id):
            cls.set(image_url=PersistentStore.get(cls.album_id))
            return

        try:
            search_strategies = [
                ("album", f"artist:{cls.artist} album:{cls.album}"),
                ("album", f"{cls.artist} {cls.album}"),
                ("track", f"artist:{cls.artist} track:{cls.title}"),
                ("track", f"{cls.artist} {cls.title}"),
                ("album", cls.album),
            ]

            image_url = None
            
            for search_type, query in search_strategies:
                try:
                    results = cls.spotify_client.search(q=query, type=search_type, limit=1)
                    
                    if search_type == "album" and results["albums"]["items"]:
                        album = results["albums"]["items"][0]
                        if album["images"]:
                            image_url = album["images"][0]["url"]
                            print(f"Found album art via query: {query}")
                            break
                    elif search_type == "track" and results["tracks"]["items"]:
                        track = results["tracks"]["items"][0]
                        if track["album"]["images"]:
                            image_url = track["album"]["images"][0]["url"]
                            print(f"Found album art via track query: {query}")
                            break
                except Exception as e:
                    print(f"Search failed for query '{query}': {e}")
                    continue

            if image_url:
                cls.set(image_url=image_url)
                PersistentStore.set(cls.album_id, image_url)
            else:
                print(f"No Spotify results found after trying all strategies for: {cls.artist} - {cls.album} - {cls.title}")
                cls.set(image_url=None)

        except Exception as e:
            print(f"Error fetching from Spotify: {e}")
            cls.set(image_url=None)

    @classmethod
    def grab(cls):
        cls._grab_subsonic()

        if cls.artist and cls.album:
            provider = config.METADATA_PROVIDER.upper()
            
            if provider == "SPOTIFY":
                cls._grab_spotify()
            elif provider == "LASTFM":
                cls._grab_lastfm()
            else:
                print(f"Unknown metadata provider: {provider}. Using Last.fm as fallback.")
                cls._grab_lastfm()


rpc = DiscordRPC(config.DISCORD_CLIENT_ID, config.DISCORD_TOKEN)

time_passed = 5

print(f"Starting with metadata provider: {config.METADATA_PROVIDER}")

while True:
    time.sleep(config.POLLING_TIME)

    CurrentTrack.grab()

    if time_passed >= 5:
        time_passed = 0

        if CurrentTrack.id is None:
            rpc.clear_activity()
            continue

        match config.ACTIVITY_NAME:
            case "ARTIST":
                activity_name = CurrentTrack.artist
            case "ALBUM":
                activity_name = CurrentTrack.album
            case "TRACK":
                activity_name = CurrentTrack.title
            case _:
                activity_name = config.ACTIVITY_NAME

        rpc.send_activity(
            {
                "application_id": config.DISCORD_CLIENT_ID,
                "type": 2,
                "state": CurrentTrack.album,
                "details": CurrentTrack.title,
                "assets": {
                    "large_image": CurrentTrack.image_url,
                },
                "timestamps": {
                    "start": CurrentTrack.started_at * 1000,
                    "end": CurrentTrack.ends_at * 1000,
                },
                "name": activity_name,
            }
        )

    time_passed += 1
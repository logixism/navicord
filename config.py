from dotenv import load_dotenv
from os import getenv
load_dotenv()

ACTIVITY_NAME = (
    getenv("ACTIVITY_NAME") or "ARTIST"
)  # ARTIST | ALBUM | TRACK | (anything else for normal text)
POLLING_TIME = int(getenv("POLLING_TIME") or 1)
DISCORD_CLIENT_ID = getenv("DISCORD_CLIENT_ID")
DISCORD_TOKEN = getenv("DISCORD_TOKEN")

# Metadata provider: LASTFM or SPOTIFY
METADATA_PROVIDER = getenv("METADATA_PROVIDER") or "LASTFM"

# Last.fm credentials
LASTFM_API_KEY = getenv("LASTFM_API_KEY")

# Spotify credentials
SPOTIFY_CLIENTID = getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENTSECRET = getenv("SPOTIFY_CLIENT_SECRET")

# Navidrome settings
NAVIDROME_SERVER = getenv("NAVIDROME_SERVER")  # don't forget http(s):// and no trailing slash
NAVIDROME_USERNAME = getenv("NAVIDROME_USERNAME")
NAVIDROME_PASSWORD = getenv("NAVIDROME_PASSWORD")
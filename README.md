# Navicord

# Navicord has been archived. Please use the official Navidrome plugin: https://github.com/navidrome/discord-rich-presence-plugin

[![Docker Image](https://badgen.net/badge/docker/navicord?icon=docker&color=blue)](https://hub.docker.com/r/logixism/navicord/tags)

A _headless_ Discord Rich Presence client for [Navidrome](https://www.navidrome.org/), with automatic album art fetching and timestamps

## ❗ Necessary setup

Create an .env file with the following variables:

| Variable           | Description                | Example value                    |
| ------------------ | -------------------------- | -------------------------------- |
| DISCORD_CLIENT_ID  | Your Discord app ID        | 805831541070495744               |
| DISCORD_TOKEN      | Your Discord account token | Mzg5NjkzNzA5MzQ4MTQ2NzY4.DM9aRQ  |
| LASTFM_API_KEY     | Your last.fm API key       | 098f6bcd4621d373cade4e832627b4f6 |
| NAVIDROME_SERVER   | Your ND server URL         | https://music.logix.lol          |
| NAVIDROME_USERNAME | Your ND username           | logix                            |
| NAVIDROME_PASSWORD | Your ND password           | 66_CfZh8                         |

## 👀 Other setup

There are also a few other variables that can be set in the environment file:

| Variable      | Description                                   | Possible Values                  |
| ------------- | --------------------------------------------- | -------------------------------- |
| ACTIVITY_NAME | Sets the activity name                        | ARTIST, ALBUM, TRACK, any string |
| POLLING_TIME  | How frequently we ask ND what song is playing | Any positive integer             |

## 🚀 Run the server

> [!IMPORTANT]  
> Since the Subsonic API does not provide a way to track song changes, we spam the ND server with requests every second. This can makes the logs grow rather quick if your log level is set to `debug` or `trace`

### Using Docker 🐋

To run the server with docker, you can use the following command:

```bash
docker run --env-file <path/to/env/file> logixism/navicord
```

### Using Python 🐍

To run the server with python, you can use the following commands:

First, install the dependencies (needs to be done only the first time)

```bash
pip install -r requirements.txt
```

Then, run the server

```bash
python main.py
```

## ℹ️ Contributing

If you find a bug or have a suggestion, please [open an issue](https://github.com/logixism/navicord).
If you want to contribute, please [fork the repository](https://github.com/logixism/navicord/fork) and create a pull request. Thanks!

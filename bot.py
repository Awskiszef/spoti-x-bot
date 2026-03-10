import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from requests_oauthlib import OAuth1


load_dotenv()

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"
SPOTIFY_ALBUMS_URL = "https://api.spotify.com/v1/artists/{artist_id}/albums"
TWITTER_POST_URL = "https://api.twitter.com/2/tweets"
STATE_FILE = Path("state.json")


def env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"posted_release_ids": []}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_spotify_access_token() -> str:
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=HTTPBasicAuth(env("SPOTIFY_CLIENT_ID"), env("SPOTIFY_CLIENT_SECRET")),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def find_artist_id(artist_name: str, access_token: str) -> str:
    response = requests.get(
        SPOTIFY_SEARCH_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": artist_name, "type": "artist", "limit": 1},
        timeout=30,
    )
    response.raise_for_status()
    items = response.json().get("artists", {}).get("items", [])
    if not items:
        raise RuntimeError(f"Artist not found on Spotify: {artist_name}")
    return items[0]["id"]


def get_latest_release(artist_id: str, access_token: str) -> dict[str, Any] | None:
    response = requests.get(
        SPOTIFY_ALBUMS_URL.format(artist_id=artist_id),
        headers={"Authorization": f"Bearer {access_token}"},
        params={
            "include_groups": "album,single",
            "limit": 10,
            "market": "US",
        },
        timeout=30,
    )
    response.raise_for_status()

    items = response.json().get("items", [])
    if not items:
        return None

    # Spotify may return duplicates across markets or album types.
    unique_releases: dict[str, dict[str, Any]] = {}
    for item in items:
        unique_releases[item["id"]] = item

    return sorted(
        unique_releases.values(),
        key=lambda item: (item.get("release_date", ""), item.get("name", "")),
        reverse=True,
    )[0]


def build_tweet(artist_name: str, release: dict[str, Any]) -> str:
    release_type = release.get("album_type", "release").capitalize()
    name = release["name"]
    date = release.get("release_date", "unknown date")
    url = release["external_urls"]["spotify"]
    return f"New {release_type} from {artist_name}: {name} ({date}) {url}"


def post_tweet(text: str) -> None:
    auth = OAuth1(
        env("TWITTER_API_KEY"),
        env("TWITTER_API_SECRET"),
        env("TWITTER_ACCESS_TOKEN"),
        env("TWITTER_ACCESS_TOKEN_SECRET"),
    )
    response = requests.post(
        TWITTER_POST_URL,
        auth=auth,
        json={"text": text},
        timeout=30,
    )
    response.raise_for_status()


def check_once() -> bool:
    artist_name = env("SPOTIFY_ARTIST_NAME")
    state = load_state()
    posted_ids = set(state.get("posted_release_ids", []))

    access_token = get_spotify_access_token()
    artist_id = find_artist_id(artist_name, access_token)
    release = get_latest_release(artist_id, access_token)
    if not release:
        print("No releases found.")
        return False

    release_id = release["id"]
    if release_id in posted_ids:
        print(f"Already posted: {release['name']}")
        return False

    tweet = build_tweet(artist_name, release)
    post_tweet(tweet)

    posted_ids.add(release_id)
    state["posted_release_ids"] = sorted(posted_ids)
    save_state(state)
    print(f"Posted: {tweet}")
    return True


def run_forever() -> None:
    interval_seconds = int(os.getenv("CHECK_INTERVAL_SECONDS", "3600"))
    print(f"Checking every {interval_seconds} seconds.")

    while True:
        try:
            check_once()
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}", file=sys.stderr)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    mode = os.getenv("BOT_MODE", "once").lower()
    if mode == "loop":
        run_forever()
    else:
        check_once()

import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import requests
import time


def get_playlist_id_from_url(playlist_url):
    """Extract playlist ID from Spotify playlist URL."""
    # Parse different URL formats
    parsed = urlparse(playlist_url)

    # Handle open.spotify.com URLs
    if "open.spotify.com" in parsed.netloc:
        path_parts = parsed.path.split("/")
        if "playlist" in path_parts:
            playlist_index = path_parts.index("playlist")
            if (playlist_index + 1) < len(path_parts):
                return path_parts[playlist_index + 1]

    # Handle spotify: URI
    elif parsed.scheme == "spotify" and "playlist" in parsed.path:
        return parsed.path.split(":")[-1]

    # Handle direct ID input
    elif len(playlist_url.strip()) == 22:
        return playlist_url.strip()

    raise ValueError(
        "Invalid Spotify playlist URL or ID. Please provide a valid Spotify playlist link."
    )


def get_playlist_tracks(sp, playlist_id):
    """Get all tracks from a playlist."""
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]

    # Spotify API paginates results, so we need to get all pages
    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    return tracks


def get_soundcharts_auth_token(api_key, api_secret):
    """Get authentication token from Soundcharts API."""
    url = "https://api.soundcharts.com/api/v2/auth/login"
    payload = {"apikey": api_key, "apisecret": api_secret}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("token")
    except Exception as e:
        print(f"Failed to authenticate with Soundcharts API: {e}")
        return None


def get_track_features(sp, track_id, soundcharts_token=None):
    """Get audio features for a track using Soundcharts API."""
    # If no Soundcharts token is provided, return None for features
    if not soundcharts_token:
        print(
            f"No Soundcharts token available - skipping audio features for track {track_id}"
        )
        return None

    try:
        # First, get the ISRC code from Spotify
        track_info = sp.track(track_id)
        isrc = track_info.get("external_ids", {}).get("isrc")

        if not isrc:
            print(f"No ISRC found for track {track_id} - cannot fetch audio features")
            return None

        # Query Soundcharts API for audio features using ISRC
        url = f"https://api.soundcharts.com/api/v2/track/features"
        headers = {
            "Authorization": f"Bearer {soundcharts_token}",
            "Content-Type": "application/json",
        }
        params = {"isrc": isrc}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        features_data = response.json()

        # Map Soundcharts features to the same format as Spotify's
        # Note: Field names and scales might differ, adjust as needed
        mapped_features = {
            "tempo": features_data.get("bpm", 0),
            "key": features_data.get("key", -1),
            "mode": features_data.get("mode", -1),
            "time_signature": features_data.get("timeSignature", 4),
            "danceability": features_data.get("danceability", 0),
            "energy": features_data.get("energy", 0),
            "loudness": features_data.get("loudness", 0),
            "speechiness": features_data.get("speechiness", 0),
            "acousticness": features_data.get("acousticness", 0),
            "instrumentalness": features_data.get("instrumentalness", 0),
            "liveness": features_data.get("liveness", 0),
            "valence": features_data.get("valence", 0),
        }

        return mapped_features

    except Exception as e:
        print(f"Failed to get audio features for track {track_id}: {e}")
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
        return None


def get_track_metadata(sp, tracks, soundcharts_token=None):
    """Extract metadata from tracks."""
    metadata = []

    for item in tracks:
        track = item["track"]

        # Skip None tracks (can happen with locally added files)
        if track is None:
            continue

        # Get audio features using Soundcharts API
        features = get_track_features(sp, track["id"], soundcharts_token)

        # Extract artist info
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        artist_ids = [artist["id"] for artist in track["artists"]]

        # Get genres from primary artist
        genres = []
        if len(artist_ids) > 0:
            try:
                artist_info = sp.artist(artist_ids[0])
                genres = artist_info.get("genres", [])
            except:
                pass

        # Basic track info
        track_data = {
            "title": track["name"],
            "artist": artists,
            "album": track["album"]["name"],
            "release_date": track["album"].get("release_date", ""),
            "duration_ms": track["duration_ms"],
            "duration": round(track["duration_ms"] / 1000, 2),  # in seconds
            "explicit": track["explicit"],
            "track_url": track["external_urls"].get("spotify", ""),
            "preview_url": track.get("preview_url", ""),
            "popularity": track.get("popularity", 0),
            "genres": genres,
        }

        # Add audio features if available
        if features:
            track_data.update(
                {
                    "bpm": round(features.get("tempo", 0), 2),
                    "key": features.get("key", -1),
                    "mode": features.get("mode", -1),  # 0 = minor, 1 = major
                    "time_signature": features.get("time_signature", 4),
                    "danceability": features.get("danceability", 0),
                    "energy": features.get("energy", 0),
                    "loudness": features.get("loudness", 0),
                    "speechiness": features.get("speechiness", 0),
                    "acousticness": features.get("acousticness", 0),
                    "instrumentalness": features.get("instrumentalness", 0),
                    "liveness": features.get("liveness", 0),
                    "valence": features.get("valence", 0),
                }
            )

            # Convert key numbers to musical notation
            keys = {
                0: "C",
                1: "C#/Db",
                2: "D",
                3: "D#/Eb",
                4: "E",
                5: "F",
                6: "F#/Gb",
                7: "G",
                8: "G#/Ab",
                9: "A",
                10: "A#/Bb",
                11: "B",
                -1: "Unknown",
            }
            modes = {0: "Minor", 1: "Major", -1: "Unknown"}

            track_data["key_name"] = keys[features.get("key", -1)]
            track_data["mode_name"] = modes[features.get("mode", -1)]
            # Combine key and mode (e.g., "C Major")
            if features.get("key", -1) != -1 and features.get("mode", -1) != -1:
                track_data["key_mode"] = (
                    f"{keys[features.get('key', -1)]} {modes[features.get('mode', -1)]}"
                )
            else:
                track_data["key_mode"] = "Unknown"

        metadata.append(track_data)

    return metadata


def main():
    """Main function to run the script."""
    # Load environment variables from .env file
    load_dotenv()

    # Get credentials from .env file
    spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    soundcharts_api_key = os.environ.get("SOUNDCHARTS_API_KEY")
    soundcharts_api_secret = os.environ.get("SOUNDCHARTS_API_SECRET")

    if not spotify_client_id or not spotify_client_secret:
        print("Missing Spotify API credentials in .env file.")
        print(
            "Please create a .env file with SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET."
        )
        print(
            "Get these credentials from: https://developer.spotify.com/dashboard/applications"
        )
        sys.exit(1)

    # Get playlist URL from user input
    playlist_url = input("Enter Spotify playlist URL: ").strip()

    try:
        # Set up Spotify client
        spotify_auth_manager = SpotifyClientCredentials(
            client_id=spotify_client_id, client_secret=spotify_client_secret
        )
        sp = spotipy.Spotify(auth_manager=spotify_auth_manager)

        # Set up Soundcharts token (if credentials are available)
        soundcharts_token = None
        if soundcharts_api_key and soundcharts_api_secret:
            soundcharts_token = get_soundcharts_auth_token(
                soundcharts_api_key, soundcharts_api_secret
            )
            if not soundcharts_token:
                print(
                    "Warning: Could not authenticate with Soundcharts API. Audio features will not be available."
                )
        else:
            print(
                "Warning: Soundcharts API credentials not found in .env file. Audio features will not be available."
            )

        # Get playlist ID and fetch tracks
        playlist_id = get_playlist_id_from_url(playlist_url)

        # Get playlist information
        playlist_info = sp.playlist(playlist_id)
        playlist_name = playlist_info["name"]
        playlist_owner = playlist_info["owner"]["display_name"]
        playlist_description = playlist_info.get("description", "")
        print(f"\nFetching data for playlist: '{playlist_name}' by {playlist_owner}")

        # Get all tracks from the playlist
        print("Fetching tracks...")
        tracks = get_playlist_tracks(sp, playlist_id)
        print(f"Found {len(tracks)} tracks. Fetching metadata...")

        # Get metadata for all tracks
        metadata = get_track_metadata(sp, tracks, soundcharts_token)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(metadata)

        # Create safe filename
        safe_name = "".join(
            [c if c.isalnum() or c in [" ", "-", "_"] else "_" for c in playlist_name]
        )
        output_file = f"{safe_name}_metadata.csv"
        df.to_csv(output_file, index=False)

        print(f"\nMetadata extracted successfully!")
        print(f"Total tracks processed: {len(metadata)}")
        print(f"Data saved to: {output_file}")

        # Display column names (metadata available)
        print("\nMetadata fields extracted:")
        for column in df.columns:
            print(f"- {column}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

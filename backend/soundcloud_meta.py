import os
import sys
import requests
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

def get_soundcloud_auth():
    """Authenticate with SoundCloud API."""
    client_id = os.environ.get("SOUNDCLOUD_CLIENT_ID")
    
    if not client_id:
        raise ValueError("SOUNDCLOUD_CLIENT_ID environment variable not found in .env file")
    
    return client_id

def get_playlist_id_from_url(playlist_url):
    """Extract playlist ID or permalink from SoundCloud URL."""
    # Parse the URL
    parsed = urlparse(playlist_url)
    
    # Check if it's a valid SoundCloud URL
    if "soundcloud.com" not in parsed.netloc:
        raise ValueError("Invalid SoundCloud URL. Please provide a valid SoundCloud playlist link.")
    
    # Extract the path (e.g., /username/sets/playlist-name)
    path = parsed.path
    
    # For API calls, we'll need the full path or resolve endpoint
    return path

def get_playlist_info(client_id, playlist_path):
    """Get playlist information using the SoundCloud API."""
    # Use the resolve endpoint to get playlist data from URL path
    api_url = f"https://api-v2.soundcloud.com/resolve"
    params = {
        "url": f"https://soundcloud.com{playlist_path}",
        "client_id": client_id
    }
    
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    playlist_data = response.json()
    
    return playlist_data

def get_playlist_tracks(client_id, playlist_data):
    """Get all tracks from a SoundCloud playlist."""
    tracks = []
    
    # If the playlist has tracks directly
    if "tracks" in playlist_data and playlist_data["tracks"]:
        tracks = playlist_data["tracks"]
    
    # If the playlist has track IDs and needs a separate request
    elif "tracks_uri" in playlist_data and playlist_data["tracks_uri"]:
        tracks_url = playlist_data["tracks_uri"]
        
        # Add client_id to the URL
        if "?" in tracks_url:
            tracks_url += f"&client_id={client_id}"
        else:
            tracks_url += f"?client_id={client_id}"
        
        response = requests.get(tracks_url)
        response.raise_for_status()
        tracks = response.json()["collection"]
    
    # Handle pagination if needed
    next_href = playlist_data.get("next_href")
    while next_href:
        # Add client_id to the next_href URL
        if "?" in next_href:
            next_href += f"&client_id={client_id}"
        else:
            next_href += f"?client_id={client_id}"
            
        response = requests.get(next_href)
        response.raise_for_status()
        next_data = response.json()
        tracks.extend(next_data["collection"])
        next_href = next_data.get("next_href")
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.1)
    
    return tracks

def get_track_metadata(client_id, tracks):
    """Extract metadata from SoundCloud tracks."""
    metadata = []
    
    for track in tracks:
        # For playlists that only contain track IDs,
        # we might need to fetch full track data
        if "title" not in track and "id" in track:
            track_url = f"https://api-v2.soundcloud.com/tracks/{track['id']}?client_id={client_id}"
            response = requests.get(track_url)
            if response.status_code == 200:
                track = response.json()
            else:
                continue
        
        # Extract available track metadata
        track_data = {
            "title": track.get("title", "Unknown"),
            "artist": track.get("user", {}).get("username", "Unknown"),
            "artist_permalink": track.get("user", {}).get("permalink", ""),
            "duration_ms": track.get("duration", 0),
            "duration": round(track.get("duration", 0) / 1000, 2),  # in seconds
            "permalink_url": track.get("permalink_url", ""),
            "created_at": track.get("created_at", ""),
            "description": track.get("description", ""),
            "genre": track.get("genre", ""),
            "tag_list": track.get("tag_list", ""),
            "playback_count": track.get("playback_count", 0),
            "likes_count": track.get("likes_count", 0),
            "reposts_count": track.get("reposts_count", 0),
            "comment_count": track.get("comment_count", 0),
            "download_count": track.get("download_count", 0),
            "stream_url": track.get("stream_url", ""),
            "waveform_url": track.get("waveform_url", ""),
            "artwork_url": track.get("artwork_url", ""),
            "downloadable": track.get("downloadable", False),
            "streamable": track.get("streamable", False),
            "bpm": track.get("bpm", None),  # Some tracks might have BPM
            "key_signature": track.get("key_signature", None)  # Some tracks might have key
        }
        
        # Extract additional metadata if available
        if "publisher_metadata" in track and track["publisher_metadata"]:
            pub_meta = track["publisher_metadata"]
            track_data.update({
                "isrc": pub_meta.get("isrc", ""),
                "p_line": pub_meta.get("p_line", ""),
                "c_line": pub_meta.get("c_line", ""),
                "release_title": pub_meta.get("release_title", ""),
                "explicit": pub_meta.get("explicit", False),
                "upc_or_ean": pub_meta.get("upc_or_ean", "")
            })
        
        metadata.append(track_data)
    
    return metadata

def main():
    """Main function to run the script."""
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Get SoundCloud client ID
        client_id = get_soundcloud_auth()
        
        # Get playlist URL from user input
        playlist_url = input("Enter SoundCloud playlist URL: ").strip()
        
        # Get playlist path from URL
        playlist_path = get_playlist_id_from_url(playlist_url)
        
        # Get playlist information
        print("Fetching playlist information...")
        playlist_data = get_playlist_info(client_id, playlist_path)
        
        playlist_title = playlist_data.get("title", "Unknown Playlist")
        playlist_creator = playlist_data.get("user", {}).get("username", "Unknown")
        print(f"\nFetching data for playlist: '{playlist_title}' by {playlist_creator}")
        
        # Get all tracks from the playlist
        print("Fetching tracks...")
        tracks = get_playlist_tracks(client_id, playlist_data)
        print(f"Found {len(tracks)} tracks. Fetching metadata...")
        
        # Get metadata for all tracks
        metadata = get_track_metadata(client_id, tracks)
        
        # Create DataFrame and save to CSV
        df = pd.DataFrame(metadata)
        
        # Create safe filename
        safe_name = "".join([c if c.isalnum() or c in [" ", "-", "_"] else "_" for c in playlist_title])
        output_file = f"{safe_name}_soundcloud_metadata.csv"
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
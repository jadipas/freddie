#!/usr/bin/env python3
import os
import sys
import argparse
import json
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.id3 import ID3
import datetime
import platform
import librosa
import numpy as np
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)


def calculate_bpm(file_path):
    """Calculate BPM using librosa."""
    try:
        # Load audio file with librosa (using a smaller duration for faster processing)
        y, sr = librosa.load(file_path, sr=None, duration=60)

        # Calculate tempo (BPM)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]

        # Round to nearest integer
        return round(tempo)
    except Exception as e:
        print(f"Error calculating BPM for {file_path}: {e}")
        return None


def extract_mp3_metadata(file_path, calculate_missing_bpm=True):
    """Extract metadata from an MP3 file."""
    try:
        audio = MP3(file_path)
        tags = ID3(file_path)

        metadata = {
            "file_path": file_path,
            "file_type": "mp3",
            "duration": audio.info.length,
            "bitrate": audio.info.bitrate,
            "sample_rate": audio.info.sample_rate,
            "channels": audio.info.channels,
        }

        # Extract common ID3 tags
        tag_mapping = {
            "title": ["TIT2"],
            "artist": ["TPE1"],
            "album": ["TALB"],
            "year": ["TDRC", "TYER"],
            "genre": ["TCON"],
            "track_number": ["TRCK"],
            "bpm": ["TBPM"],
            "key": ["TKEY"],
            "composer": ["TCOM"],
            "publisher": ["TPUB"],
            "initial_key": ["TKEY"],
        }

        for key, tag_ids in tag_mapping.items():
            for tag_id in tag_ids:
                if tag_id in tags:
                    metadata[key] = str(tags[tag_id])
                    break

        # Calculate BPM if it's not in the metadata and calculation is requested
        if "bpm" not in metadata and calculate_missing_bpm:
            print(
                f"BPM not found in metadata, calculating for: {os.path.basename(file_path)}"
            )
            bpm = calculate_bpm(file_path)
            if bpm:
                metadata["bpm"] = str(bpm)
                metadata["bpm_calculated"] = True

        return metadata
    except Exception as e:
        return {"file_path": file_path, "error": str(e)}


def extract_mp4_metadata(file_path, calculate_missing_bpm=True):
    """Extract metadata from an MP4 file."""
    try:
        audio = MP4(file_path)

        metadata = {
            "file_path": file_path,
            "file_type": "mp4",
            "duration": audio.info.length,
            "bitrate": audio.info.bitrate,
            "sample_rate": audio.info.sample_rate,
            "channels": audio.info.channels,
        }

        # Extract MP4 tags
        tag_mapping = {
            "title": ["©nam"],
            "artist": ["©ART"],
            "album": ["©alb"],
            "year": ["©day"],
            "genre": ["©gen", "gnre"],
            "track_number": ["trkn"],
            "bpm": ["tmpo"],
            "composer": ["©wrt"],
            "comment": ["©cmt"],
            "copyright": ["cprt"],
            "album_artist": ["aART"],
        }

        for key, tag_ids in tag_mapping.items():
            for tag_id in tag_ids:
                if tag_id in audio:
                    # Handle list values
                    value = audio[tag_id]
                    if isinstance(value, list):
                        # For BPM specifically, it's often stored as an integer
                        if tag_id == "tmpo" and key == "bpm":
                            metadata[key] = str(value[0])
                        else:
                            metadata[key] = str(value[0])
                    else:
                        metadata[key] = str(value)
                    break

        # Calculate BPM if it's not in the metadata and calculation is requested
        if "bpm" not in metadata and calculate_missing_bpm:
            print(
                f"BPM not found in metadata, calculating for: {os.path.basename(file_path)}"
            )
            bpm = calculate_bpm(file_path)
            if bpm:
                metadata["bpm"] = str(bpm)
                metadata["bpm_calculated"] = True

        return metadata
    except Exception as e:
        return {"file_path": file_path, "error": str(e)}


def scan_directory(directory, calculate_missing_bpm=True):
    """Scan a directory for MP3 and MP4 files and extract their metadata."""
    results = []

    # Make sure the directory path is normalized for the current OS
    directory = os.path.normpath(directory)

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    print(f"Scanning directory: {directory}")
    total_files = 0
    processed_files = 0

    # First, count the total number of MP3/MP4 files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".mp3", ".mp4", ".m4a")):
                total_files += 1

    if total_files == 0:
        print("No MP3 or MP4 files found in the directory.")
        return results

    # Then process each file
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            if file.lower().endswith(".mp3"):
                processed_files += 1
                print(f"Processing MP3 ({processed_files}/{total_files}): {file}")
                metadata = extract_mp3_metadata(file_path, calculate_missing_bpm)
                results.append(metadata)

            elif file.lower().endswith((".mp4", ".m4a")):
                processed_files += 1
                print(f"Processing MP4/M4A ({processed_files}/{total_files}): {file}")
                metadata = extract_mp4_metadata(file_path, calculate_missing_bpm)
                results.append(metadata)

    return results


def save_metadata(metadata, output_file):
    """Save metadata to a file in JSON format."""
    # Normalize the output file path for the current OS
    output_file = os.path.normpath(output_file)

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            # Add timestamp, summary, and system info
            output = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "system": platform.system(),
                "file_count": len(metadata),
                "metadata": metadata,
            }
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"\nMetadata saved to {output_file}")
        print(f"Processed {len(metadata)} audio files.")

        # Print summary of BPM calculation
        calculated_bpm_count = sum(
            1 for item in metadata if item.get("bpm_calculated") == True
        )
        if calculated_bpm_count > 0:
            print(
                f"BPM was calculated for {calculated_bpm_count} files that didn't have BPM metadata."
            )

    except Exception as e:
        print(f"Error saving metadata to {output_file}: {e}")
        # Try to save in the current directory as a fallback
        fallback_file = os.path.basename(output_file)
        print(f"Attempting to save to current directory as {fallback_file}")
        with open(fallback_file, "w", encoding="utf-8") as f:
            output = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "system": platform.system(),
                "file_count": len(metadata),
                "metadata": metadata,
            }
            json.dump(output, f, indent=4, ensure_ascii=False)
        print(f"Metadata saved to {fallback_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract metadata from MP3 and MP4 files in a directory."
    )
    parser.add_argument("directory", help="Directory to scan for audio files")
    parser.add_argument(
        "-o",
        "--output",
        default="audio_metadata.json",
        help="Output file name (default: audio_metadata.json)",
    )
    parser.add_argument(
        "--no-bpm-calc",
        action="store_true",
        help="Disable automatic BPM calculation for files missing BPM metadata",
    )

    args = parser.parse_args()

    # Detect operating system
    system = platform.system()
    print(f"Detected operating system: {system}")

    # Check if librosa is available for BPM calculation
    if not args.no_bpm_calc:
        try:
            import librosa

            print(
                "BPM calculation enabled - will calculate BPM for files that don't have it in metadata"
            )
        except ImportError:
            print(
                "Warning: librosa library not found. BPM calculation will be disabled."
            )
            print(
                "To enable BPM calculation, install librosa with: pip install librosa"
            )
            args.no_bpm_calc = True

    metadata = scan_directory(args.directory, not args.no_bpm_calc)
    save_metadata(metadata, args.output)


if __name__ == "__main__":
    main()

# Freddie the DJ Playlist Assistant

Freddie is a Python tool designed to help DJs plan and build playlists. It scans a given directory for MP3 and MP4/M4A files, extracts metadata (like title, artist, album, duration, BPM, etc.) through `/backend/metadata_extractor.py`, and automatically calculates BPM if it’s not available in the file’s metadata.

## Features

-   **Metadata Extraction:** Reads and aggregates metadata from MP3 and MP4/M4A files using `/backend/metadata_extractor.py`.
-   **Automatic BPM Calculation:** Uses the `librosa` library to calculate BPM when missing.
-   **Interactive Frontend:** A simple UI displays the playlist and offers recommendations.
-   **Customizable Output:** Save the metadata into a JSON file for further analysis.
-   **Cross-Platform:** Works on Windows, macOS, and Linux.

## Installation

1. **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Run Metadata Extraction:**

    ```sh
    python backend/metadata_extractor.py /path/to/your/audio/files
    ```

    - Use `--output` to specify a custom output file.
    - Use `--no-bpm-calc` to disable BPM calculation.

2. **Launch the Frontend UI:**
    ```sh
    python frontend/app.py
    ```
    - Browse and filter the generated playlist.
    - Get track recommendations based on metadata and BPM.

## License

Include your license information here (for example, MIT License).

Enjoy building your perfect playlist!

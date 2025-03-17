# Freddie the DJ Playlist Assistant

Freddie is a Python tool designed to help DJs plan and build playlists. It scans a given directory for MP3 and MP4/M4A files, extracts metadata (like title, artist, album, duration, BPM, etc.), and automatically calculates BPM when it’s not available in the file’s metadata. The output is saved in a JSON file, which you can use to plan your playlists and mix tracks with a matching pace.

## Features

-   **Metadata Extraction:** Reads and aggregates metadata from MP3 and MP4/M4A files.
-   **Automatic BPM Calculation:** Uses the `librosa` library to calculate BPM if it is missing.
-   **Customizable Output:** Save the metadata into a JSON file for further analysis.
-   **Cross-Platform:** Works on different operating systems (Windows, macOS, Linux).

## Installation

1. **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install dependencies:**

    Make sure you have Python 3 installed.

    Install required Python packages with:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the script from the command line by providing a directory to scan. For example:

```sh
python metadata_extractor.py /path/to/your/audio/files
```

### Options

-   `-o, --output`  
    Specify the output file name. Defaults to `audio_metadata.json`.

    Example:

    ```sh
    python metadata_extractor.py /path/to/your/audio/files --output my_playlist_metadata.json
    ```

-   `--no-bpm-calc`  
    Disable automatic BPM calculation for files missing BPM metadata.

    Example:

    ```sh
    python metadata_extractor.py /path/to/your/audio/files --no-bpm-calc
    ```

## Additional Information

-   **Logging:** The script prints progress information to the terminal during execution including which files are being processed and the status of BPM calculation.
-   **Error Handling:** If an error occurs during metadata extraction or file saving, the script will print an error message and attempt a fallback save in the current directory.

## License

Include your license information here (for example, MIT License).

Enjoy building your perfect playlist!

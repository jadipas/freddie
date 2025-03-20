from fastapi import FastAPI, HTTPException
import os
import json
from pathlib import Path

# Initialize FastAPI app
app = FastAPI()

# Define the metadata file path relative to this file
METADATA_FILE = Path(__file__).parent / "audio_metadata.json"


@app.get("/audio_metadata")
async def get_audio_metadata():
    # Check if the metadata file exists
    if METADATA_FILE.exists():
        try:
            with METADATA_FILE.open("r") as file:
                data = json.load(file)
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading metadata: {e}")
    else:
        # Import and call the metadata extraction function
        try:
            from metadata_extractor import extract_metadata

            extract_metadata()  # This should generate the audio_metadata.json file
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating metadata: {e}"
            )

        # Verify file creation and return JSON
        if METADATA_FILE.exists():
            try:
                with METADATA_FILE.open("r") as file:
                    data = json.load(file)
                return data
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error reading generated metadata: {e}"
                )
        else:
            raise HTTPException(
                status_code=500, detail="Metadata file was not created."
            )

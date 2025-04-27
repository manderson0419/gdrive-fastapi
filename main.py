from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from typing import List
import io
import os
import json

app = FastAPI(
    title="Google Drive Files API",
    version="1.1.0",
    description="API to list and download files from a Google Drive folder."
)

# === SETTINGS ===
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Load service account credentials from environment variable
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

# === CONFIGURE FOLDER ID ===
FOLDER_ID = '1VsWkYlSJSFWHRK6u66qKhUn9xqajMPd6'  # <-- Your Google Drive Folder ID

# === INITIALIZE GOOGLE DRIVE CLIENT ===
drive_service = build('drive', 'v3', credentials=credentials)

# === ROUTES ===

@app.get("/")
def root():
    return {"message": "Google Drive FastAPI server is running 🚀"}

@app.get("/files", response_model=List[dict])
def list_files():
    """List files in the specified Google Drive folder, excluding shortcuts."""
    query = (
        f"'{FOLDER_ID}' in parents and "
        f"trashed = false and "
        f"mimeType != 'application/vnd.google-apps.shortcut'"
    )
    results = drive_service.files().list(
        q=query,
        fields="files(id, name, mimeType)"
    ).execute()
    files = results.get('files', [])
    return files

@app.get("/download")
def download_file(file_id: str):
    """Download a file from Google Drive by its file ID and stream it back."""
    request = drive_service.files().get_media(fileId=file_id)

    # Download file into memory
    memory_file = io.BytesIO()
    downloader = MediaIoBaseDownload(memory_file, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

    memory_file.seek(0)  # Reset pointer to beginning

    # Fetch filename
    file_metadata = drive_service.files().get(fileId=file_id, fields="name").execute()
    filename = file_metadata.get("name", "downloaded_file")

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }

    return StreamingResponse(memory_file, media_type="application/octet-stream", headers=headers)

@app.get("/openapi.json")
def get_openapi():
    """Serve the static OpenAPI schema."""
    return FileResponse("openapi.json")

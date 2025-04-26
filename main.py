from fastapi import FastAPI
from fastapi.responses import StreamingResponse  # <-- New import
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload  # <-- Needed for download
from typing import List
import io  # <-- New import
import os

app = FastAPI()

# === SETTINGS ===
SERVICE_ACCOUNT_FILE = '/Users/michaelaanderson/Downloads/tidy-centaur-457916-h9-2230742befee.json'
FOLDER_ID = '1VsWkYlSJSFWHRK6u66qKhUn9xqajMPd6'
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# === INITIALIZE GOOGLE DRIVE CLIENT ===
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

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

from fastapi.responses import FileResponse
import tempfile

@app.get("/download/{file_id}")
def download_file(file_id: str):
    """Download a file from Google Drive by its file ID."""
    request = drive_service.files().get_media(fileId=file_id)
    
    # Create a temporary file to download into
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    
    downloader = MediaIoBaseDownload(temp_file, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    
    temp_file.flush()
    temp_file.seek(0)
    
    # Fetch the filename
    file_metadata = drive_service.files().get(fileId=file_id, fields="name").execute()
    filename = file_metadata.get("name", "downloaded_file")

    return FileResponse(temp_file.name, media_type='application/octet-stream', filename=filename)

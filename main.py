from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from typing import List
import io
import os
import json

app = FastAPI()

# === SETTINGS ===
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Load service account credentials from environment variable
service_account_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

# Your Google Drive folder ID
FOLDER_ID = '1VsWkYlSJSFWHRK6u66qKhUn9xqajMPd6'

# === INITIALIZE GOOGLE DRIVE CLIENT ===
drive_service = build('drive', 'v3', credentials=credentials_

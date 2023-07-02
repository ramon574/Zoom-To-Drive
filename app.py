import os
import requests
import io
import tempfile
from flask import Flask, redirect, request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Set up Flask app
app = Flask(__name__)
app.secret_key = "unblinded2018"

# Google OAuth 2.0 configuration
CLIENT_SECRETS_FILE = 'client_secrets.json'
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]
API_VERSION = 'v3'

# Create the Flow instance
flow = Flow.from_client_secrets_file(
    CLIENT_SECRETS_FILE,
    scopes=SCOPES,
    redirect_uri='https://zoom-to-drive.onrender.com/upload_callback'  # Replace with your domain
)

# Redirect user to Google for authentication
@app.route('/')
def index():
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return redirect(authorization_url)

# Callback route after authentication
@app.route('/upload_callback')
def upload_callback():
    # Fetch the authorization code from the callback request
    authorization_code = request.args.get('code')

    # Exchange the authorization code for a token
    flow.fetch_token(authorization_response=request.url)

    # Create a Google Drive service instance using the credentials
    credentials = flow.credentials
    drive_service = build('drive', API_VERSION, credentials=credentials)

    # Fetch the video file from the URL
    url = 'https://us02web.zoom.us/rec/download/x7kM-ZYD0N_9iBktf24pGMnMoQPY9PaTGdYt1w3uIpcBvUI_CyixfuyQzU3ABpS6XPBrvfH0G_JyiNKg.TncpleKMGhEL8jEW'
    response = requests.get(url)
    video_content = response.content

    # Upload the video to Google Drive
    file_metadata = {'name': 'my_video.mp4'}
    media = MediaIoBaseUpload(io.BytesIO(video_content), mimetype='video/mp4')
    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return 'Video uploaded successfully!'

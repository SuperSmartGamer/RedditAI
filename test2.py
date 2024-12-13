from instagrapi import Client
import os
import pickle
import subprocess

import ffmpeg

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Function to upload video to Instagram
def upload_video(file_path, description):
    # Initialize the Instagram client
    cl = Client()

    try:
        # Log in to Instagram account
        cl.login(os.getenv('YT_Username'), os.getenv('YT_Password'))

        try:
            # Upload video as a Reel
            cl.video_upload(file_path, caption=description)
            print(f"Uploaded: {file_path}")

        except Exception as upload_error:
            print(f"Failed to upload {file_path}: {upload_error}")
    
    except Exception as login_error:
        print(f"Login failed: {login_error}")



# Set the API service name and version


API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Path to your client_secrets.json file
CLIENT_SECRETS_FILE = "client_secret.json"

# Scopes for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    CLIENT_SECRETS_FILE = "client_secret.json"
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    TOKEN_FILE = "token.pickle"

    credentials = None

    # Check if credentials are saved locally
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    # If no valid credentials are available, request new ones
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())  # Refresh the token if expired
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)  # Opens a browser for authentication

        # Save the credentials for the next run
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)

    # Build and return the YouTube API client
    return build("youtube", "v3", credentials=credentials)

from googleapiclient.http import MediaFileUpload

def extract_thumbnail(video_path, thumbnail_path="thumbnail.jpg"):
    """
    Extracts the first frame of the video as a thumbnail.

    Args:
        video_path (str): Path to the video file.
        thumbnail_path (str): Path to save the extracted thumbnail.

    Returns:
        str: Path to the extracted thumbnail, or None if extraction fails.
    """
    try:
        ffmpeg.input(video_path, ss=0).output(thumbnail_path, vframes=1).run(overwrite_output=True)
        print(f"Thumbnail saved at: {thumbnail_path}")
        return thumbnail_path
    except Exception as e:
        print("Error extracting thumbnail:", e)
        return None

def upload_video_yt(youtube, video_file, title, description, category_id="22"):
    """
    Uploads a video to YouTube with a thumbnail.

    Args:
        youtube: Authenticated YouTube API client.
        video_file (str): Path to the video file.
        title (str): Title of the video.
        description (str): Description of the video.
        category_id (str): YouTube video category ID (default is "22" for "People & Blogs").
    """
    thumbnail_path = extract_thumbnail(video_file)
    
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": description.split(", "),  # Generate tags from description
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    try:
        # Upload the video
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=video_file
        )
        response = request.execute()
        print("Video uploaded successfully:", response["id"])

        # Upload the thumbnail if it exists
        if thumbnail_path:
            youtube.thumbnails().set(
                videoId=response["id"],
                media_body=thumbnail_path
            ).execute()
            print("Thumbnail uploaded successfully.")

    except Exception as e:
        print("Error uploading video:", e)
    finally:
        # Delete the thumbnail file
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
            print(f"Thumbnail file deleted: {thumbnail_path}")



def postStuff(title, file):
    youtube_service = get_authenticated_service()

    description = """
    daily reddit stories, daily reddit, daily reddit readings, daily reddit update, 
    daily dose reddit, daily voice reddit, daily voice reddit stories, funny reddit daily, 
    askreddit, shorts, reddit, viralvideo, viralshorts

    #redditstories #askreddittopposts #reddit #askredditposts #minecraftshorts #bestofaskreddit 
    #minecraftparkour #dailyredditstories #dailyreddit #dailyredditreadings #dailyredditupdate 
    #dailydosereddit #dailyvoicereddit #dailyvoiceredditstories #funnyredditdaily #askreddit 
    #shorts #viralvideo #viralshorts
    """

    upload_video_yt(youtube_service, file, title, description=description)
    #upload_video(file, description= title+"     "+description)

postStuff(file=r"reddit_videos\un-uploaded\12-13-2024 #2.mp4", title="Daily Reddit test")
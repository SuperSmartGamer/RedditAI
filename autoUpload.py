from instagrapi import Client
import os
import pickle
import subprocess
from random import randint
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



def extract_thumbnail(video_path, output_dir="temp", thumbnail_name="temp_"+str(randint(0,10000000))+".jpg", frame_time="00:00:01"):
    """
    Generates a thumbnail for a given video.

    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory to save the thumbnail.
        thumbnail_name (str): Name of the output thumbnail file.
        frame_time (str): Timestamp to capture the frame (default is 00:00:01).

    Returns:
        str: Path to the generated thumbnail or an error message.
    """
    # Ensure paths are valid
    if not os.path.isfile(video_path):
        return f"Error: Video file '{video_path}' does not exist."

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Generate the full path for the thumbnail
    thumbnail_path = os.path.join(output_dir, thumbnail_name)

    try:
        # FFmpeg command to generate the thumbnail
        command = [
            "ffmpeg",
            "-y",  # Overwrite without asking
            "-ss", frame_time,  # Seek to the desired frame time
            "-i", video_path,  # Input video
            "-frames:v", "1",  # Extract a single frame
            "-q:v", "2",  # High-quality output
            thumbnail_path  # Output file
        ]

        # Run the FFmpeg command
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if os.path.isfile(thumbnail_path):
            return f"Thumbnail successfully created: {thumbnail_path}"
        else:
            return f"Error: Thumbnail file '{thumbnail_path}' was not created."

    except subprocess.CalledProcessError as e:
        return f"Error generating thumbnail: {e.stderr.decode('utf-8').strip()}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Example Usage



from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import os

# Authenticate and build the YouTube service
def authenticate_youtube():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.force-ssl'])
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

# Get the playlist ID for "Reddit daily"
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
import os

# Authenticate and build the YouTube service
def authenticate_youtube():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.force-ssl'])
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

# Get the playlist ID for "Reddit daily"
def get_playlist_id(youtube, playlist_name="Reddit daily"):
    request = youtube.playlists().list(
        part="snippet",
        mine=True,
    )
    response = request.execute()

    for playlist in response["items"]:
        if playlist["snippet"]["title"] == playlist_name:
            return playlist["id"]
    return None

# Upload video and add to "Reddit daily" playlist
def upload_video_yt(youtube, video_file, title, description, category_id="22"):
    """
    Uploads a video to YouTube with a thumbnail and adds it to the 'Reddit daily' playlist.

    Args:
        youtube: Authenticated YouTube API client.
        video_file (str): Path to the video file.
        title (str): Title of the video.
        description (str): Description of the video.
        category_id (str): YouTube video category ID (default is "22" for "People & Blogs").
    """
    # Extract valid tags from the description
    tags = [
        tag.strip("#").strip()
        for tag in description.replace("\n", " ").split()
        if tag.startswith("#") and len(tag.strip("#").strip()) > 0
    ]

    thumbnail_path = extract_thumbnail(video_file)

    request_body = {
        "snippet": {
            "title": title,
            "description": description.strip(),
            "tags": tags[:50],  # YouTube allows a max of 50 tags
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
            media_body=MediaFileUpload(video_file)
        )
        response = request.execute()
        print("Video uploaded successfully:", response["id"])

        # Upload the thumbnail if it exists
        if thumbnail_path:
            youtube.thumbnails().set(
                videoId=response["id"],
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Thumbnail uploaded successfully.")

        # Get the "Reddit daily" playlist ID
        playlist_id = get_playlist_id(youtube, "Reddit daily")
        if playlist_id:
            # Add the video to the playlist
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": response["id"]
                        }
                    }
                }
            ).execute()
            print("Video added to the 'Reddit daily' playlist.")
        else:
            print("Playlist 'Reddit daily' not found.")

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
    upload_video(file, description= title+"     "+description)
    


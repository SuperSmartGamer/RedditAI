from instagrapi import Client
import os

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


print(os.getenv('YT_Username'), os.getenv('YT_Password'))
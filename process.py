import os
import re
from moviepy.editor import VideoFileClip, CompositeVideoClip
from itertools import combinations
from random import randint
from datetime import datetime
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
from generate_tts import text_to_speech
from getRed import fetch_reddit_posts
from create import transcribe_audio_to_srt
from videofy import create_video
from int_to_word import *
from moviepy.editor import VideoFileClip
from word2number import w2n  # Ensure this is imported
from thumbnail_generator import thumbnail_gen
import shutil
import time
from autoUpload import postStuff
import random

def move_files(source_dir, target_dir):
    """
    Moves all files from source_dir to target_dir.

    Args:
        source_dir (str): The path of the directory to move files from.
        target_dir (str): The path of the directory to move files to.
    """
    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created target directory '{target_dir}'.")

    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        target_file = os.path.join(target_dir, filename)
        if os.path.isfile(source_file):
            shutil.move(source_file, target_file)
            print(f"Moved: {source_file} -> {target_file}")

def days_since(date_str, offset=0):
    # Convert the input date string to a datetime object
    date_format = "%m/%d/%y"
    input_date = datetime.strptime(date_str, date_format)
    
    # Get the current date
    current_date = datetime.today()
    
    # Calculate the difference in days and add the offset
    delta = current_date - input_date
    return delta.days + offset



def number_to_words_in_text(text):
    if not isinstance(text, str):  # Ensure text is a string
        return text
    
    def replace(match):
        number = match.group(0)  # Get the matched number as string
        try:
            # Convert the number to a word and ensure it's a string
            return str(w2n.word_to_num(number)) if number.isdigit() else number
        except ValueError:
            return number  # In case the word can't be converted to a number
    
    return re.sub(r'\d+', replace, text)


def combine_mp3s(file1, file2, volume_percent=100):
	AudioSegment.from_file(file1)[:min(len(AudioSegment.from_file(file1)), len(AudioSegment.from_file(file2)))] \
		.overlay(AudioSegment.from_file(file2) + 20 * (volume_percent / 100 - 1)) \
		.export(file1, format="mp3")


def cleanup(directory, keyword):
    for filename in os.listdir(directory):
        if keyword in filename:
            file_path = os.path.join(directory, filename)
            os.remove(file_path)


def closest_sum(arr, target):
    closest = 0
    closest_combination = []
    
    for r in range(1, len(arr) + 1):
        for comb in combinations(enumerate(arr), r):
            indices, values = zip(*comb)
            total = sum(values)
            if total <= target and total > closest:
                closest = total
                closest_combination = indices
                
    print(f"Target: {target}, Closest sum: {closest}, Combination: {closest_combination}")
    return closest_combination


def get_audio_length(file_path):
    return len(AudioSegment.from_file(file_path))

def replace_in_srt(file_path, x, y):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        updated_content = content.replace(x, y)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print(f"Replacements completed. File updated: {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

def tts_logic(title, comments, output_path="temp/"+str(randint(0,100000000000))+".mp3", target_value=59000):
    clip_lengths = []
    valid_comments = []

    for comment_index, x in enumerate(comments):
        try:
            if not x.strip():  # Skip empty comments
                print(f"Skipping empty comment at index {comment_index}")
                continue
            
            # Convert the comment to words, including numbers
            print(f"Processing comment at index {comment_index}: {x}")
            text_to_speech(x, f"temp/temp_{comment_index}.mp3", speed_percent=50)
            clip_length = get_audio_length(f"temp/temp_{comment_index}.mp3")
            clip_lengths.append(clip_length)
            valid_comments.append(x)
            print(f"Clip length for comment {comment_index}: {clip_length / 1000} seconds")
        except Exception as e:
            print(f"Error processing comment at index {comment_index}: {e}")
            continue

    if not valid_comments:
        print("No valid comments to process.")
        return 0

    # Select the optimal set of comments
    n = closest_sum(clip_lengths, target_value - 15000)
    selected_comments = [valid_comments[i] for i in n]
    selected_comments = numberize(selected_comments)
    selected_comments.insert(0, title)
    full_text = ". ".join(selected_comments)

    try:
        text_to_speech(full_text, output_path)
        print(f"Total length of speech: {get_audio_length(output_path) / 1000} seconds")
    except Exception as e:
        print(f"Error generating final speech file: {e}")
        return 0

    return 0



def script(data):
    paths = []
    for x in data:
        print("Working on audio #", data.index(x))
        tts_logic(x["title"], x["comments"], output_path=f"audio/{get_date()} #{data.index(x)}.mp3")
        audio_path = f"audio/{get_date()} #{data.index(x)}.mp3"
        combine_mp3s(audio_path, "music/music_"+str(randint(1,10))+".mp3", 25)
        paths.append(audio_path)
        print(f"Audio file created at: {audio_path}")
    
    cleanup("temp", "temp")
    
    # Check total duration of all audio files
    total_duration = sum(get_audio_length(path) for path in paths) / 1000  # In seconds
    print(f"Total duration of all audio clips: {total_duration} seconds")
    
    return paths


def numberize(arr):
    for z in arr:  
        arr[arr.index(z)] = str(arr.index(z)+1)+". "+z
    return arr


def get_date():
    return datetime.now().strftime("%m-%d-%Y")

def random_clip(directory):
    try:
        # List of common video file extensions
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm']
        
        # Get a list of all files in the directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        # Filter files to include only video files
        video_files = [f for f in files if any(f.lower().endswith(ext) for ext in video_extensions)]
        
        print(video_files)
        
        # Check if the directory contains any video files
        if not video_files:
            return None
        
        # Select and return a random video file
        return directory + "/" + random.choice(video_files)
    except FileNotFoundError:
        print("Directory not found.")
        return None

def trim_videos_in_directory(directory, max_length):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(('.mp4', '.avi', '.mov')):  # Add other video formats if needed
            video_path = os.path.join(directory, filename)
            
            # Load the video
            video = VideoFileClip(video_path)
            
            # Check if the video exceeds the max_length
            if video.duration > max_length:
                # Trim the video to max_length
                video = video.subclip(0, max_length)
                
                # Save the trimmed video, overwriting the original
                video.write_videofile(video_path, codec="libx264")  # Specify codec for saving
                print(f"Trimmed: {filename}")

def thumbnailify(username="", subreddit="", output_path="temp", title=""):
    # Assuming thumbnail_gen generates the image and returns the path to it
    generated_image_path = thumbnail_gen(
        subreddit_text=subreddit,
        textbox_text=title,
        output_filepath=output_path,
        html_file_path="file:///D:/reddit/index.html",
        username=username
    )

    # Check if the image exists and wait for it to be generated
    if not os.path.exists(generated_image_path):
        max_wait_time = 30  # Maximum wait time (in seconds)
        wait_interval = 0.5  # Check interval (in seconds)
        elapsed_time = 0

        while not os.path.exists(generated_image_path) and elapsed_time < max_wait_time:
            time.sleep(wait_interval)
            elapsed_time += wait_interval
        
        # If the file is still not found, raise an error
        if not os.path.exists(generated_image_path):
            raise TimeoutError(f"Thumbnail generation failed. File not found: {generated_image_path}")
    
    print(f"Thumbnail created at: {generated_image_path}")
    return str(generated_image_path)


def overlay_video(main_video_path, secondary_video_path):
    """
    Overlays a small secondary video onto a main video, slightly above the bottom and centered.

    Parameters:
        main_video_path (str): Path to the main video file (also the output path).
        secondary_video_path (str): Path to the secondary video file.
    """
    # Load the main and secondary videos
    main_clip = VideoFileClip(main_video_path)
    secondary_clip = VideoFileClip(secondary_video_path)

    # Resize the secondary video to be smaller (e.g., 20% of main video's width)
    secondary_clip = secondary_clip.resize(width=main_clip.w * 0.2)

    # Calculate position: centered horizontally and slightly above the bottom
    x_center = (main_clip.w - secondary_clip.w) / 2
    y_position = main_clip.h - secondary_clip.h - 50  # 50 pixels above the bottom

    # Position the secondary clip
    secondary_clip = secondary_clip.set_position((x_center, y_position))

    # Overlay the secondary clip onto the main clip
    final_clip = CompositeVideoClip([main_clip, secondary_clip])

    # Write the result to the same file as the main video
    final_clip.write_videofile(main_video_path, codec="libx264", audio_codec="aac")


def main(data, upload=False):
    move_files("reddit_videos/un-uploaded", "reddit_videos")
    day = days_since("12/12/24", 5)

    for x in data:
        with open('log.txt', 'a') as file:
            file.write(f"{x['post_id']}, \n")

    audio = script(data)  # Generate audio files from Reddit data

    for i, x in enumerate(audio):
        post = data[i]
        is_nsfw = post['nsfw']
        nsfw_suffix = "_nsfw" if is_nsfw else ""
        base_file_name = f"{get_date()} #{i}"

        srt_file_name = f"subtitles/{base_file_name}{nsfw_suffix}.srt"
        video_file_name = f"reddit_videos/un-uploaded/{base_file_name}{nsfw_suffix}.mp4"
        image_file_name = f"image/{base_file_name}{nsfw_suffix}.png"

        transcribe_audio_to_srt(x, srt_file_name)

        # Use thumbnailify to generate the image path and wait for its creation
        trigger_image = thumbnailify(
            subreddit="r/" + post["subreddit"],
            title=post["title"],
            output_path=image_file_name,
            username="u/" + post["username"]
        )

        create_video(
            mp3_file=x,
            srt_file=srt_file_name,
            output_file=video_file_name,
            aspect_ratio="9:16",
            background_video=random_clip("clips"),
            font="fonts/KOMIKAX_.ttf",
            font_size=75,
            text_color="white",
            stroke_color="black",
            stroke_width=5,
            trigger_image=trigger_image,
            trigger_char="1. ",
            trigger_char_2="One,",
            fps=30
        )

        # Check the final video duration
        video_duration = get_audio_length(video_file_name) / 1000  # Convert milliseconds to seconds
        print(f"Final video length: {video_duration} seconds")

    if upload:
        for file in os.listdir("reddit_videos/un-uploaded"):
            # Build the full file path
            file_path = os.path.join("reddit_videos/un-uploaded", file)

            # Check if it's a file (and not a subdirectory)
            if os.path.isfile(file_path):
                print(f"Processing file: {file}")

                # Extract post title based on file index
                try:
                    # Handle NSFW suffix and remove file extension
                    file_name_without_extension = file.split('.')[0]
                    index_part = file_name_without_extension.split(" ")[1].split("#")[1]

                    if "_nsfw" in index_part:
                        index_part = index_part.split("_")[0]

                    # Convert the index part to an integer
                    video_index = int(index_part)
                    post_title = data[video_index]["title"]

                    postStuff(title=post_title, file=file_path)
                except (ValueError, IndexError) as e:
                    print(f"Error processing file {file}: {e}")
                    continue

        cleanup("temp", "temp")





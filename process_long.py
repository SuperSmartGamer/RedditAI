import os
import re
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
from datetime import datetime, timedelta



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
    for x in comments:
        comment_index = comments.index(x)
        # Convert the comment to words, including numbers
        comments[comment_index] = number_to_words_in_text(x)
        print(f"Converted comment: {comments[comment_index]}")  # Ensure conversion is correct
        # Generate speech
        text_to_speech(comments[comment_index], f"temp/temp_{comment_index}.mp3", speed_percent=20)
        clip_length = get_audio_length(f"temp/temp_{comment_index}.mp3")
        clip_lengths.append(clip_length)
        print(f"Clip length for comment {comment_index}: {clip_length / 1000} seconds")
    
    # Select the optimal set of comments
    n = closest_sum(clip_lengths, target_value - 15000)
    v = [comments[i] for i in n]
    v = numberize(v)
    v.insert(0, title)
    #v.insert(1," lez go ")
    v = ". ".join(v)
    text_to_speech(v, output_path)
    #add sort here

    print(f"Total length of speech: {get_audio_length(output_path) / 1000} seconds")
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


def main(data):
    move_files("reddit_videos/un-uploaded", "reddit_videos")

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
        #replace_in_srt(srt_file_name, "Let's go.","lez go")

        # Use thumbnailify to generate the image path and wait for its creation
        trigger_image = thumbnailify(
            subreddit="r/"+post["subreddit"],
            title=post["title"],
            output_path=image_file_name,
            username="u/"+post["username"]
        )

        create_video(
            mp3_file=x,
            srt_file=srt_file_name,
            output_file=video_file_name,
            aspect_ratio="9:16",
            background_video=f"clips/clip_{randint(1, 99)}.mp4",
            font="fonts/KOMIKAX_.ttf",
            font_size=75,
            text_color="white",
            stroke_color="black",
            stroke_width=5,
            trigger_image=trigger_image,
            trigger_char="!. "
        )

        
        # Check the final video duration
        video_duration = get_audio_length(video_file_name) / 1000  # Convert milliseconds to seconds
        print(f"Final video length: {video_duration} seconds")




# Example usage
main(fetch_reddit_posts( 
    sorting_method="top", 
    time_frame="day", 
    num_posts=1, 
    num_comments=1
))

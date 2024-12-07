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
import random



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


def closest_sum(arr, target, iterations=1000):
    closest = float('-inf')  # Initialize closest sum as negative infinity
    closest_combination = None  # Initialize the best combination

    for _ in range(iterations):
        # Convert to a list of tuples if 'arr' is a dictionary
        if isinstance(arr, dict):
            arr = list(arr.items())  # Convert dictionary to list of (key, value) pairs

        # Randomize the order to explore different combinations
        shuffled_arr = random.sample(arr, len(arr))
        
        current_sum = 0
        current_combination = []

        # Check if 'arr' is a list of values or a list of (index, value) pairs
        if all(isinstance(item, tuple) and len(item) == 2 for item in shuffled_arr):
            # If it's a list of tuples (index, value), unpack the tuple
            for idx, value in shuffled_arr:
                if current_sum + value <= target:
                    current_sum += value
                    current_combination.append(idx)

                if current_sum == target:
                    break
        else:
            # If it's a list of values, use the value directly
            for idx, value in enumerate(shuffled_arr):
                if current_sum + value <= target:
                    current_sum += value
                    current_combination.append(idx)

                if current_sum == target:
                    break

        # Update the best combination if this one is closer
        if current_sum > closest:
            closest = current_sum
            closest_combination = current_combination

    print(f"Target: {target}, Closest sum: {closest}, Combination: {closest_combination}")
    closest_combination .sort()
    return closest_combination

def get_audio_length(file_path):
    return len(AudioSegment.from_file(file_path))


def tts_logic(title, comments, output_path="temp/"+str(randint(0,100000000))+".mp3", target_value=590000):
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
    v.insert(0, title + ". ")
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
        arr[arr.index(z)] = number_to_words_in_text(str(arr.index(z)+1)+". "+z)
    return arr


def get_date():
    return datetime.now().strftime("%m-%d-%Y")


def trim_videos_in_directory(directory, max_length):
    pass


def main(data):
    for x in data:
        with open('log.txt', 'a') as file:
            file.write(f"{x['post_id']}, \n")
    
    audio = script(data)
    
    for x in audio:
        transcribe_audio_to_srt(x, f"subtitles/{get_date()} #{audio.index(x)}.srt")
        video_output_path = f"reddit_videos/{get_date()} #{audio.index(x)} Long Form.mp4"
        create_video(
            mp3_file=x,
            srt_file=f"subtitles/{get_date()} #{audio.index(x)}.srt",
            output_file=video_output_path,
            aspect_ratio="16:9",
            background_video="clips/background-stripes.mp4", #f"clips/clip_{randint(1,99)}.mp4", 
            font1="fonts/made-okine-sans-personal-use.black.otf",
            font2="fonts/made-okine-sans-personal-use.black-outline.otf",
            font_size=75,
            text_color1="white",
            text_color2="black"
        )
        # Check final video duration
        video_duration = get_audio_length(video_output_path) / 1000  # In seconds
        print(f"Final video length: {video_duration} seconds")
       #trim_videos_in_directory(r"C:\Users\william\Desktop\Code\test\reddit\reddit_videos", 59.999)


# Example usage
main(fetch_reddit_posts( 
    sorting_method="top", 
    time_frame="month", 
    num_posts=10, 
    num_comments=100
))

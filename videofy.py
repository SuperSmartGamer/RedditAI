from moviepy.editor import AudioFileClip, VideoFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip
import pysrt
import os
import time
import random

def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

def get_video_dimensions(aspect_ratio):
    ratios = {
        "16:9": (1920, 1080),
        "4:3": (1440, 1080),
        "21:9": (2560, 1080),
        "1:1": (1080, 1080),
        "9:16": (1080, 1920)
    }
    return ratios.get(aspect_ratio, (1920, 1080))

def get_random_time(video_duration, time_offset):
    max_random_time = video_duration - time_offset
    if max_random_time <= 0:
        raise ValueError("Time offset is too large, resulting in no valid time range.")
    return random.uniform(0, max_random_time)

def resize_image_aspect_ratio(image_clip, width, height):
    image_aspect_ratio = image_clip.size[0] / image_clip.size[1]
    video_aspect_ratio = width / height

    if image_aspect_ratio > video_aspect_ratio:
        image_clip = image_clip.resize(width=width)
    else:
        image_clip = image_clip.resize(height=height)
    
    return image_clip

def create_video(mp3_file, srt_file, output_file, trigger_char, 
                              trigger_image, aspect_ratio="16:9", 
                              background_video=None, background_color=(0, 0, 0), 
                              font="Arial", font_size=60, 
                              text_color="white", stroke_color="black", stroke_width=2, fps=24, trigger_char_2="One,"):
    
    if not os.path.exists(mp3_file) or not os.path.exists(srt_file):
        raise FileNotFoundError("Ensure MP3 and SRT files exist.")
    
    # Wait for trigger image to be created
    max_wait_time = 30  # Maximum time to wait for the file (in seconds)
    wait_interval = 0.5  # Time interval to check the file (in seconds)
    elapsed_time = 0
    while not os.path.exists(trigger_image):
        if elapsed_time >= max_wait_time:
            raise TimeoutError(f"Thumbnail generation took too long. File not found: {trigger_image}")
        time.sleep(wait_interval)
        elapsed_time += wait_interval

    # Check if background video exists
    if background_video and not os.path.exists(background_video):
        raise FileNotFoundError(f"Background video not found: {background_video}")

    # Get video dimensions
    width, height = get_video_dimensions(aspect_ratio)
    audio = AudioFileClip(mp3_file)

    # Get random start time for background video to ensure it doesn't run out of content
    if background_video:
        video_duration = VideoFileClip(background_video).duration
        random_start_time = get_random_time(video_duration, 60)  # audio.duration
        background = VideoFileClip(background_video).subclip(random_start_time, random_start_time + audio.duration)

        # Crop the background video to match the target aspect ratio
        video_aspect_ratio = width / height
        background_aspect_ratio = background.size[0] / background.size[1]

        if background_aspect_ratio > video_aspect_ratio:
            # Crop sides
            new_width = int(background.size[1] * video_aspect_ratio)
            x_center = background.size[0] // 2
            x1 = x_center - new_width // 2
            x2 = x_center + new_width // 2
            background = background.crop(x1=x1, y1=0, x2=x2, y2=background.size[1])
        else:
            # Crop top and bottom
            new_height = int(background.size[0] / video_aspect_ratio)
            y_center = background.size[1] // 2
            y1 = y_center - new_height // 2
            y2 = y_center + new_height // 2
            background = background.crop(x1=0, y1=y1, x2=background.size[0], y2=y2)

        background = background.resize((width, height))
    else:
        background = ColorClip(size=(width, height), color=background_color).set_duration(audio.duration)

    # Read subtitles and process clips
    subs = pysrt.open(srt_file)
    subtitle_clips = []
    clips = []
    trigger_detected = False

    # Pre-resize trigger image while maintaining aspect ratio
    trigger_image_clip = ImageClip(trigger_image)
    trigger_image_clip = resize_image_aspect_ratio(trigger_image_clip, width, height)

    for i, sub in enumerate(subs):
        start_time = time_to_seconds(sub.start)
        end_time = time_to_seconds(sub.end)
        duration = end_time - start_time

        if (trigger_char in sub.text or trigger_char_2 in sub.text) and not trigger_detected:
            trigger_detected = True

            # Display trigger image until the start of this subtitle
            image_clip = trigger_image_clip.set_position("center").set_duration(start_time)
            clips.append(image_clip)

        if trigger_detected:
            # Pre-render text clips to avoid processing each frame
            text_clip = TextClip(
                sub.text,
                fontsize=font_size,
                font=font,
                color=text_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method='caption',
                size=(width * 0.8, None)
            ).set_duration(duration)

            vertical_position = (height - text_clip.h) // 2
            text_clip = text_clip.set_start(start_time).set_position(('center', vertical_position))
            subtitle_clips.append(text_clip)

    if not trigger_detected:
        # Display the trigger image for the full duration if no trigger is detected
        image_clip = trigger_image_clip.set_position("center").set_duration(audio.duration)
        clips = [image_clip]
    else:
        clips += subtitle_clips

    # Create final video
    final_video = CompositeVideoClip([background] + clips).set_audio(audio).set_duration(audio.duration)

    # Use NVENC for GPU acceleration and multi-threading
    final_video.write_videofile(output_file, fps=fps, codec='h264_nvenc', audio_codec='aac', threads=8,
                                ffmpeg_params=["-c:v", "h264_nvenc", "-preset", "fast", "-rc:v", "vbr_hq", "-tune", "fastdecode"])

    # Cleanup
    audio.close()
    final_video.close()
    if background_video:
        background.close()

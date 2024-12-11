from moviepy.editor import AudioFileClip, VideoFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip
import pysrt
import os
import time

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

def create_video(mp3_file, srt_file, output_file, trigger_char, 
                              trigger_image, aspect_ratio="16:9", 
                              background_video=None, background_color=(0, 0, 0), 
                              font="Arial", font_size=60, 
                              text_color="white", stroke_color="black", stroke_width=2):
    # Ensure files exist before proceeding
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

    # Create background clip
    if background_video:
        background = VideoFileClip(background_video).loop(duration=audio.duration).resize((width, height))
    else:
        background = ColorClip(size=(width, height), color=background_color).set_duration(audio.duration)

    # Read subtitles and process clips
    subs = pysrt.open(srt_file)
    subtitle_clips = []
    clips = []
    trigger_detected = False

    for i, sub in enumerate(subs):
        start_time = time_to_seconds(sub.start)
        end_time = time_to_seconds(sub.end)
        duration = end_time - start_time

        if trigger_char in sub.text and not trigger_detected:
            trigger_detected = True

            # Display trigger image until the start of this subtitle
            image_clip = ImageClip(trigger_image)
            image_aspect_ratio = image_clip.size[0] / image_clip.size[1]
            video_aspect_ratio = width / height

            if image_aspect_ratio > video_aspect_ratio:
                image_clip = image_clip.resize(width=width)
            else:
                image_clip = image_clip.resize(height=height)

            image_clip = image_clip.set_position("center").set_duration(start_time)
            clips.append(image_clip)

        if trigger_detected:
            text_clip = TextClip(
                sub.text,
                fontsize=font_size,
                font=font,
                color=text_color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method='caption',
                size=(width * 0.8, None)
            )
            vertical_position = (height - text_clip.h) // 2
            text_clip = (text_clip
                         .set_start(start_time)
                         .set_duration(duration)
                         .set_position(('center', vertical_position)))
            subtitle_clips.append(text_clip)

    if not trigger_detected:
        # Display the trigger image for the full duration if no trigger is detected
        image_clip = ImageClip(trigger_image)
        image_aspect_ratio = image_clip.size[0] / image_clip.size[1]
        video_aspect_ratio = width / height

        if image_aspect_ratio > video_aspect_ratio:
            image_clip = image_clip.resize(width=width)
        else:
            image_clip = image_clip.resize(height=height)

        image_clip = image_clip.set_position("center").set_duration(audio.duration)
        clips = [image_clip]
    else:
        clips += subtitle_clips

    # Create final video
    final_video = CompositeVideoClip([background] + clips).set_audio(audio).set_duration(audio.duration)
    final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac', audio_fps=44100)

    # Cleanup
    audio.close()
    final_video.close()
    if background_video:
        background.close()

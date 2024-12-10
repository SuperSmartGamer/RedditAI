from moviepy.editor import AudioFileClip, VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import pysrt
import os

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

def create_stroke_text_clip(text, font, fontsize, color, stroke_color, stroke_width, size):
    # Create the stroke by layering text clips with offsets
    offsets = [(dx, dy) for dx in range(-stroke_width, stroke_width + 1)
                      for dy in range(-stroke_width, stroke_width + 1) if dx != 0 or dy != 0]
    
    # Create the stroke layer
    stroke_clips = [
        TextClip(
            text, fontsize=fontsize, font=font, color=stroke_color,
            method='caption', size=size
        ).set_position((dx, dy))
        for dx, dy in offsets
    ]
    
    # Create the main text layer
    main_text_clip = TextClip(
        text, fontsize=fontsize, font=font, color=color,
        method='caption', size=size
    )
    
    return CompositeVideoClip(stroke_clips + [main_text_clip])

def create_subtitle_clips(srt_file, video_width, video_height, 
                          font="Arial", fontsize=60, text_color="white", 
                          stroke_color="black", stroke_width=2, 
                          max_width_ratio=0.8):
    subs = pysrt.open(srt_file)
    subtitle_clips = []
    
    for sub in subs:
        start_time = time_to_seconds(sub.start)
        end_time = time_to_seconds(sub.end)
        duration = end_time - start_time
        
        size = (video_width * max_width_ratio, None)
        subtitle_clip = create_stroke_text_clip(
            sub.text, font=font, fontsize=fontsize, color=text_color,
            stroke_color=stroke_color, stroke_width=stroke_width, size=size
        )
        
        vertical_position = (video_height - subtitle_clip.h) // 2
        subtitle_clip = subtitle_clip.set_start(start_time).set_duration(duration).set_position(('center', vertical_position))
        subtitle_clips.append(subtitle_clip)
    
    return subtitle_clips

def create_video(mp3_file, srt_file, output_file, aspect_ratio="16:9", background_video=None, background_color=(0, 0, 0),
                 font="Arial", fontsize=60, text_color="white", stroke_color="black", stroke_width=2):
    if not os.path.exists(mp3_file) or not os.path.exists(srt_file):
        raise FileNotFoundError("Ensure both MP3 and SRT files exist.")
    if background_video and not os.path.exists(background_video):
        raise FileNotFoundError(f"Background video not found: {background_video}")

    width, height = get_video_dimensions(aspect_ratio)
    audio = AudioFileClip(mp3_file)
    
    if background_video:
        background = VideoFileClip(background_video).loop(duration=audio.duration).resize((width, height))
    else:
        background = ColorClip(size=(width, height), color=background_color).set_duration(audio.duration)
    
    subtitle_clips = create_subtitle_clips(
        srt_file, video_width=width, video_height=height,
        font=font, fontsize=fontsize, text_color=text_color,
        stroke_color=stroke_color, stroke_width=stroke_width
    )
    
    final_video = CompositeVideoClip([background] + subtitle_clips).set_audio(audio).set_duration(audio.duration)
    final_video.write_videofile(output_file, fps=60, codec='libx264', audio_codec='aac', audio_fps=44100)
    
    audio.close()
    final_video.close()
    if background_video:
        background.close()

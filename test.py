from moviepy.editor import VideoFileClip, CompositeVideoClip
import os
import numpy as np

def remove_black(frame):
    # Define black color (close to [0, 0, 0])
    target_black = np.array([0, 0, 0])
    tolerance = 50  # Adjust tolerance for black color range
    
    # Extract RGB channels
    rgb_frame = frame[:, :, :3]
    
    # Create mask for pixels close to target_black
    mask = np.all(np.abs(rgb_frame - target_black) < tolerance, axis=-1)
    
    # Make black pixels transparent (keep the alpha channel intact)
    frame[mask] = [0, 0, 0, 0]  # RGBA: Set RGB to 0 and alpha to 0 (transparent)
    
    return frame

def overlay_video(main_video_path, secondary_video_path, scale_factor=0.1, position_from_bottom=30, output_path=None):
    # Validate scale_factor and check if video files exist
    if not (0 < scale_factor <= 1):
        raise ValueError("scale_factor must be between 0 and 1")
    
    if not os.path.exists(main_video_path) or not os.path.exists(secondary_video_path):
        raise FileNotFoundError("One or both video files do not exist")
    
    # Load the main and secondary videos
    main_video = VideoFileClip(main_video_path)
    secondary_video = VideoFileClip(secondary_video_path)
    
    # Check if the secondary video has RGBA (transparency)
    first_frame = secondary_video.get_frame(0)
    if first_frame.shape[2] == 4:  # RGBA format detected
        secondary_video = secondary_video.fl_image(remove_black)
    
    # Resize the secondary video according to the scale_factor
    secondary_video_resized = secondary_video.resize(width=main_video.w * scale_factor)
    
    # Position the secondary video (centered horizontally, with vertical offset)
    secondary_video_position = ('center', main_video.h - secondary_video_resized.h - position_from_bottom)
    
    # Set the start time of the secondary video (start at the middle of the main video)
    secondary_video_resized = secondary_video_resized.set_start(main_video.duration / 2)
    
    # Combine the main and secondary videos into a composite
    final_video = CompositeVideoClip([main_video, secondary_video_resized.set_position(secondary_video_position)])
    
    # Output path setup (if none provided, default to appending '_overlaid')
    if output_path is None:
        output_path = f"{os.path.splitext(main_video_path)[0]}_overlaid.mp4"
    
    # Write the final video to file
    final_video.write_videofile(output_path, codec='libx264', audio_codec='aac', threads=4, bitrate='5000k')
    
    # Close video clips to free resources
    main_video.close()
    secondary_video.close()

if __name__ == "__main__":
    try:
        main_video_path =  r"reddit_videos\un-uploaded\12-25-2024 #0.mp4"
        secondary_video_path =  "img_resources/subscribe_green.mp4"
        scale_factor = 0.15
        position_from_bottom = 30
        output_path = None  # or provide a custom path for output

        overlay_video(main_video_path, secondary_video_path, scale_factor, position_from_bottom, output_path)
        print("Video overlay completed successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

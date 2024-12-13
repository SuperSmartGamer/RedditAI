import time
from moviepy.editor import ColorClip
import subprocess

def generate_video_cpu(output_file):
    try:
        # Start measuring time
        start_time = time.time()
        
        # Generate a test video with a solid color (CPU)
        clip = ColorClip(size=(1920, 1080), color=(255, 0, 0), duration=5)  # Red color, 5 seconds
        clip.fps = 24  # Set FPS value
        clip.write_videofile(output_file, codec='libx264', threads=1)

        # Measure and print the time taken for CPU processing
        end_time = time.time()
        cpu_time = end_time - start_time
        print(f"CPU video generation time: {cpu_time:.2f} seconds")

    except Exception as e:
        print(f"Error generating CPU video: {e}")

def generate_video_gpu(output_file):
    try:
        # Start measuring time
        start_time = time.time()

        # Generate a test video with a solid color (GPU)
        clip = ColorClip(size=(1920, 1080), color=(0, 255, 0), duration=5)  # Green color, 5 seconds
        clip.fps = 24  # Set FPS value
        clip.write_videofile(output_file, codec='libx264', threads=1, ffmpeg_params=["-c:v", "h264_nvenc"])

        # Measure and print the time taken for GPU processing
        end_time = time.time()
        gpu_time = end_time - start_time
        print(f"GPU video generation time: {gpu_time:.2f} seconds")

    except Exception as e:
        print(f"Error generating GPU video: {e}")

def check_ffmpeg_gpu_support():
    try:
        # Check if ffmpeg supports GPU acceleration (CUDA)
        result = subprocess.run(['ffmpeg', '-hwaccels'], capture_output=True, text=True)
        if 'cuda' in result.stdout:
            print("CUDA GPU acceleration is supported by FFmpeg.")
            return True
        else:
            print("CUDA GPU acceleration is not supported by FFmpeg.")
            return False
    except Exception as e:
        print(f"Error checking FFmpeg GPU support: {e}")
        return False

def main():
    # Output file paths
    cpu_output_file = "cpu_test_video.mp4"
    gpu_output_file = "gpu_test_video.mp4"
    
    # Check if GPU acceleration is supported
    if not check_ffmpeg_gpu_support():
        print("Skipping GPU rendering as CUDA is not supported.")
        generate_video_cpu(cpu_output_file)
    else:
        # Generate videos on CPU and GPU
        print("Generating video on CPU...")
        generate_video_cpu(cpu_output_file)
        
        print("Generating video on GPU...")
        generate_video_gpu(gpu_output_file)

if __name__ == "__main__":
    main()

import asyncio
import edge_tts
import os
import time

def text_to_speech(
    text, output_path=None, voice="en-US-ChristopherNeural", speed_percent=20, retries=3, delay=2
):
    """
    Convert text to speech and save as an MP3 file with customizable speed. Retries if generation fails.
    
    Parameters:
    - text (str): The text to convert to speech.
    - output_path (str, optional): Full path where the MP3 file will be saved.
      If not provided, creates a file in the current directory.
    - voice (str, optional): Voice to use. Defaults to a male US English voice.
    - speed_percent (int, optional): Speech speed adjustment in percentage. 
      Positive values speed up, negative values slow down.
    - retries (int, optional): Number of times to retry if generation fails. Default is 3.
    - delay (int, optional): Delay in seconds between retries. Default is 2 seconds.

    Returns:
    - bool: True if successful, False otherwise.
    """
    async def _convert_text():
        try:
            # If no output path is provided, generate a default one
            if output_path is None:
                # Create a 'tts_output' directory if it doesn't exist
                os.makedirs('tts_output', exist_ok=True)
                
                # Generate a filename based on the first few words of the text
                safe_filename = ''.join(e for e in text[:20] if e.isalnum())
                output_file = os.path.join('tts_output', f'{safe_filename}_tts.mp3')
            else:
                output_file = output_path
            
            # Calculate rate string based on percentage
            rate = f'{speed_percent:+}%'
            
            # Create TTS communication with rate
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            
            # Save the audio file
            await communicate.save(output_file)
            return output_file
        except Exception as e:
            print(f"Error during text-to-speech conversion: {e}")
            return None

    def _is_valid_audio(file_path):
        """
        Check if the generated audio file is valid.
        """
        if not os.path.exists(file_path):
            return False
        # Check file size (small size might indicate an issue)
        return os.path.getsize(file_path) > 1024  # Minimum file size in bytes

    # Run the async function with retries
    attempt = 0
    while attempt < retries:
        try:
            audio_file = asyncio.run(_convert_text())
            if audio_file and _is_valid_audio(audio_file):
                print(f"Audio generated successfully: {audio_file}")
                return True
            else:
                print(f"Audio validation failed. Retrying... ({attempt + 1}/{retries})")
                attempt += 1
                time.sleep(delay)
        except RuntimeError as e:
            if "already running" in str(e):
                print("Detected an existing event loop; running within the current loop.")
                audio_file = asyncio.create_task(_convert_text())
                if audio_file and _is_valid_audio(audio_file):
                    return True
            else:
                raise
    print("Failed to generate valid audio after multiple attempts.")
    return False

# Example usage


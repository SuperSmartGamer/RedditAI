import asyncio
import edge_tts
import os

def text_to_speech(text, output_path=None, voice="en-US-ChristopherNeural", speed_percent=20):
    """
    Convert text to speech and save as an MP3 file with customizable speed.
    
    Parameters:
    - text (str): The text to convert to speech
    - output_path (str, optional): Full path where the MP3 file will be saved
      If not provided, creates a file in the current directory
    - voice (str, optional): Voice to use. Defaults to a male US English voice.
    - speed_percent (int, optional): Speech speed adjustment in percentage. 
      Positive values speed up, negative values slow down. 
      Range typically between -50 and 50. Default is 0 (normal speed).
    
    Returns:
    - bool: True if successful, False otherwise
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
            # Edge TTS uses strings like '+10%', '-10%', or '0%'
            rate = f'{speed_percent:+}%'
            
            # Create TTS communication with rate
            communicate = edge_tts.Communicate(text, voice, rate=rate)
            
            # Save the audio file
            await communicate.save(output_file)
            print(f"Audio saved to: {output_file}")
            return True
        except Exception as e:
            print(f"Error during text-to-speech conversion: {e}")
            return False

    # Run the async function
    return asyncio.run(_convert_text())

text_to_speech("Why don't you fear death?", "output.mp3", speed_percent=100)
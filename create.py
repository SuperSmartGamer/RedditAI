import whisper
import re

def transcribe_audio_to_srt(input_audio, output_srt_file):
    model = whisper.load_model("base")
    result = model.transcribe(input_audio)
    
    with open(output_srt_file, 'w', encoding='utf-8') as f:
        # Track the last end time to prevent overlap
        last_end_time = 0
        subtitle_counter = 1

        for segment in result['segments']:
            subtitle_text = segment.get('text', '').strip()
            
            if not subtitle_text:
                continue
            
            # More intelligent chunking
            chunks = smart_chunk_text(subtitle_text, max_length=40)
            
            # Calculate base timing
            segment_start = segment['start']
            segment_end = segment['end']
            segment_duration = segment_end - segment_start
            
            # Dynamically adjust chunk duration
            chunk_duration = segment_duration / len(chunks)
            
            for i, chunk in enumerate(chunks):
                # Calculate precise start and end times
                chunk_start = max(last_end_time, segment_start + i * chunk_duration)
                chunk_end = min(segment_end, chunk_start + max(chunk_duration, 1.0))
                
                # Ensure minimum 0.5 second display time, max 3 seconds
                display_time = max(0.5, min(chunk_end - chunk_start, 3.0))
                
                # Write subtitle
                f.write(f"{subtitle_counter}\n")
                f.write(f"{format_time(chunk_start)} --> {format_time(chunk_start + display_time)}\n")
                f.write(f"{chunk.strip()}\n\n")
                
                # Update tracking variables
                last_end_time = chunk_start + display_time
                subtitle_counter += 1

    print(f"Subtitles saved to: {output_srt_file}")

def smart_chunk_text(text, max_length=30):
    """
    Intelligently chunk text while preserving meaning and readability
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        # Prioritize meaningful breaks
        if current_length + len(word) + (1 if current_length > 0 else 0) > max_length:
            # Add current chunk and start new one
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + (1 if current_length > 0 else 0)

    # Add final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def format_time(seconds):
    """
    Precise time formatting for SRT
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"

# Example usage
# input_audio = "input.mp3"
# output_srt_file = "subtitles.srt"
# transcribe_audio_to_srt(input_audio, output_srt_file)
import whisper
import re

def transcribe_audio_to_srt(input_audio, output_srt_file):
    model = whisper.load_model("base")
    result = model.transcribe(input_audio)
    
    with open(output_srt_file, 'w') as f:
        subtitle_counter = 1  # To track subtitle numbering

        for segment in result['segments']:
            subtitle_text = segment.get('text', '')

            # Split text into sentences
            sentences = split_into_sentences(subtitle_text)
            
            # Calculate time for each sentence
            segment_duration = segment['end'] - segment['start']
            sentence_duration = segment_duration / len(sentences) if sentences else 0

            start_time = segment['start']

            # Process each sentence individually
            for sentence in sentences:
                # Break sentence into 24-character chunks
                chunks = break_into_chunks(sentence, 24)

                # Calculate time for each chunk
                chunk_duration = sentence_duration / len(chunks) if chunks else 0

                # Write each chunk with its own timestamp
                for chunk in chunks:
                    end_time = start_time + chunk_duration
                    f.write(f"{subtitle_counter}\n")
                    f.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
                    f.write(f"{chunk.strip()}\n")
                    f.write("\n")
                    subtitle_counter += 1
                    start_time = end_time  # Update start time for the next chunk

    print(f"Subtitles saved to: {output_srt_file}")

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

def split_into_sentences(text):
    # Split text into sentences based on punctuation
    return re.split(r'(?<=[.?!])\s+', text)

def break_into_chunks(text, max_length):
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        # If adding this word exceeds the max length, start a new chunk
        if len(current_chunk) + len(word) + 1 <= max_length:
            if current_chunk:
                current_chunk += " " + word
            else:
                current_chunk = word
        else:
            chunks.append(current_chunk)
            current_chunk = word

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# Example usage
#input_audio = "input.mp3"  # Replace with your audio file path
#output_srt_file = "subtitles.srt"
#transcribe_audio_to_srt(input_audio, output_srt_file)

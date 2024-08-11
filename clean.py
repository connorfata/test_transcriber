import re

def clean_transcript(transcript):
    # Remove timestamps using a regular expression
    transcript = re.sub(r'\[\d{2}:\d{2} - \d{2}:\d{2}\]', '', transcript)
    
    # Initialize an empty string to hold the cleaned transcript
    cleaned_transcript = ""
    last_speaker = None

    for line in transcript.splitlines():
        # Check if the line starts with "Speaker n:"
        speaker_match = re.match(r'(Speaker \d):', line.strip())
        
        if speaker_match:
            current_speaker = speaker_match.group(0)
            # Add the speaker label only if it's different from the last one
            if current_speaker != last_speaker:
                # Add a newline before the speaker label
                cleaned_transcript += f"\n{current_speaker} "
                last_speaker = current_speaker
            # Append the rest of the line without the speaker label
            cleaned_transcript += line[len(current_speaker)+1:].strip() + " "
        else:
            # If it's not a speaker line, just add the line
            cleaned_transcript += line.strip() + " "
    
    return cleaned_transcript.strip()

# Function to read the transcript from a file, clean it, and save the result
def process_transcript_file(input_file, output_file):
    # Read the content of the transcript file
    with open(input_file, "r") as file:
        transcript = file.read()
    
    # Clean the transcript
    cleaned_transcript = clean_transcript(transcript)
    
    # Save the cleaned transcript to a new file
    with open(output_file, "w") as file:
        file.write(cleaned_transcript)
    
    print(f"Cleaned transcript saved to {output_file}")

# Example usage
input_file = "transcription.txt"
output_file = "cleaned_transcript.txt"
process_transcript_file(input_file, output_file)

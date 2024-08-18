import boto3
import time

# Initialize Boto3 client
transcribe = boto3.client('transcribe')

# Parameters
job_name = "your_transcription_job_name"
job_uri = "s3://your-bucket-name/your-audio-file.mp3"

# Start transcription job
transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='mp3',  # Change to the correct format of your file
    LanguageCode='en-US'  # Change to the correct language code
)

# Wait for the job to complete
while True:
    status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
        break
    print("Not ready yet...")
    time.sleep(10)

# Print the transcription job details
if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
    response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    transcript_url = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
    print(f"Transcription completed. Transcript URL: {transcript_url}")
else:
    print("Transcription failed.")

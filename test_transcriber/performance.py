import os
import torchaudio
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from asteroid.models import ConvTasNet
from pyannote.audio import Pipeline
from google.cloud import speech

def download_audio(youtube_url, output_format="wav"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': output_format,
            'preferredquality': '192',
        }],
        'outtmpl': 'downloaded_audio.%(ext)s',
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return f"downloaded_audio.{output_format}"

def convert_audio(input_file, output_file="audio.wav"):
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_file, format="wav")
    return output_file

def split_audio(input_file, chunk_length_ms):
    audio = AudioSegment.from_wav(input_file)
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    return chunks

def separate_speech(audio_path, model):
    # Load audio and convert to the expected input format
    audio, _ = torchaudio.load(audio_path)
    audio = audio.unsqueeze(0)  # Add batch dimension

    # Perform separation
    separated_sources = model(audio)
    return separated_sources

def diarize_speakers(separated_sources):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
    diarization_results = []

    for i, source in enumerate(separated_sources):
        source_path = f"source_{i}.wav"
        torchaudio.save(source_path, source.squeeze(0), 16000)
        
        # Perform diarization
        diarization = pipeline({"waveform": source.squeeze(0), "sample_rate": 16000})
        diarization_results.append(diarization)
        
    return diarization_results

def transcribe_audio(source_path):
    client = speech.SpeechClient()

    with open(source_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_speaker_diarization=True,
        diarization_speaker_count=2,  # Adjust based on your needs
    )

    response = client.recognize(config=config, audio=audio)
    return response

def combine_transcription_diarization(diarization_results, transcriptions):
    combined_output = []  # Initialize the list here

    for diarization, transcription in zip(diarization_results, transcriptions):
        for result in transcription.results:
            for alternative in result.alternatives:
                # Find the corresponding speaker label in the diarization result
                # Placeholder logic: Assigning Speaker 1 for simplicity
                speaker_label = "Speaker 1" if result.speaker_tag == 1 else "Speaker 2"
                
                # You would need to map the speaker_tag to the actual speaker label from diarization_results
                combined_output.append(f"{speaker_label}: {alternative.transcript}")

    return combined_output

# Main processing flow
youtube_url = "https://www.youtube.com/watch?v=CDZ9REOh2xA"
audio_file = download_audio(youtube_url)
processed_audio_file = convert_audio(audio_file)

# Split the audio into 30-second chunks
chunks = split_audio(processed_audio_file, chunk_length_ms=30000)

# Load the model once and reuse
model = ConvTasNet.from_pretrained('JorisCos/ConvTasNet_Libri2Mix_sepclean_16k')

final_output = []
for i, chunk in enumerate(chunks):
    chunk_file = f"processed_audio_chunk_{i}.wav"
    chunk.export(chunk_file, format="wav")

    # Separate the speech into different sources (speakers)
    separated_sources = separate_speech(chunk_file, model)

    # Perform speaker diarization on the separated sources
    diarization_results = diarize_speakers(separated_sources)

    # Transcribe the separated and diarized audio
    transcriptions = []
    for j in range(len(separated_sources)):
        source_path = f"source_{j}.wav"
        transcription = transcribe_audio(source_path)
        transcriptions.append(transcription)

    # Combine transcription and diarization results
    chunk_output = combine_transcription_diarization(diarization_results, transcriptions)
    final_output.extend(chunk_output)

# Now print the final output
for line in final_output:
    print(line)

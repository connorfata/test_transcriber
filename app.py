from flask import Flask, render_template, request, jsonify
import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment
import os
import logging
from pyAudioAnalysis import audioSegmentation as aS

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def download_video(url):
    try:
        logging.debug(f"Attempting to download audio from URL: {url}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': '%(id)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = f"{info['id']}.wav"

        logging.info(f"Successfully downloaded audio to: {audio_file}")
        return audio_file
    except Exception as e:
        logging.exception(f"Error downloading video: {str(e)}")
        return f"Error: {str(e)}"

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    try:
        logging.info(f"Processing audio file: {audio_file}")
        
        # Perform speaker diarization using pyAudioAnalysis
        logging.info("Starting speaker diarization...")
        clusters, _, _ = aS.speaker_diarization(audio_file, n_speakers=2)
        logging.info(f"Speaker diarization completed. Clusters: {clusters}")

        # Load the audio file
        audio = AudioSegment.from_wav(audio_file)
        
        sample_rate = audio.frame_rate
        full_text = ""
        current_speaker = clusters[0]
        start_time = 0

        for i in range(1, len(clusters)):
            if clusters[i] != current_speaker or i == len(clusters) - 1:
                end_time = i * (audio.duration_seconds / len(clusters)) * 1000
                audio_chunk = audio[start_time:end_time]
                
                temp_file = "temp_chunk.wav"
                audio_chunk.export(temp_file, format="wav")
                
                with sr.AudioFile(temp_file) as source:
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data)
                        full_text += f"Speaker {current_speaker}: {text} "
                        logging.debug(f"Segment transcribed successfully")
                    except sr.UnknownValueError:
                        logging.warning(f"Could not understand audio in segment")
                    except sr.RequestError as e:
                        logging.error(f"Could not request results from Google Speech Recognition service; {e}")
                    
                os.remove(temp_file)
                
                current_speaker = clusters[i]
                start_time = end_time

        if full_text:
            logging.info("Transcription completed successfully")
            return full_text.strip()
        else:
            logging.error("No text was transcribed from the audio")
            return "Error: No text could be transcribed from the audio"
    except Exception as e:
        logging.error(f"Unexpected error during transcription: {str(e)}")
        return f"Error: Unexpected error during transcription: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    try:
        url = request.form['url']
        logging.info(f"Received transcription request for URL: {url}")
        
        audio_file = download_video(url)
        
        if isinstance(audio_file, str) and audio_file.startswith("Error"):
            logging.error(f"Error during video download: {audio_file}")
            return jsonify({'error': audio_file}), 400
        
        transcription = transcribe_audio(audio_file)
        os.remove(audio_file)  # Clean up the temporary file
        
        if transcription.startswith("Error"):
            logging.error(f"Error during transcription: {transcription}")
            return jsonify({'error': transcription}), 400
        
        logging.info("Transcription process completed successfully")
        return jsonify({'transcription': transcription})
    except Exception as e:
        logging.error(f"Unexpected error in transcribe_video route: {str(e)}")
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)


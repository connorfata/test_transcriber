# This downloads podcast into a folder titled 'downloaded_podcast' #

import os
import requests
import feedparser
from pydub import AudioSegment
from urllib.parse import urlparse

# Function to download and save the latest podcast episode
def download_latest_podcast(url, output_dir, convert_to_wav=False):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    filepath = os.path.join(output_dir, filename)

    # Download the audio file
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")

        # Convert to WAV if required
        if convert_to_wav:
            convert_to_wav_file(filepath)

    else:
        print(f"Failed to download: {filename}")

# Function to convert an audio file to WAV format
def convert_to_wav_file(filepath):
    if filepath.endswith('.mp3'):
        audio = AudioSegment.from_mp3(filepath)
    elif filepath.endswith('.wav'):
        print(f"File is already in WAV format: {filepath}")
        return
    else:
        print(f"Unsupported file format: {filepath}")
        return
    
    wav_filepath = filepath.rsplit('.', 1)[0] + '.wav'
    audio.export(wav_filepath, format="wav")
    print(f"Converted to WAV: {wav_filepath}")

# Function to process the latest episode from a podcast RSS feed
def process_latest_podcast_rss(feed_urls, output_dir, convert_to_wav=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)
        
        if feed.entries:
            latest_entry = feed.entries[0]
            print(f"Processing latest episode: {latest_entry.title}")
            if 'enclosures' in latest_entry:
                for enclosure in latest_entry.enclosures:
                    download_latest_podcast(enclosure.href, output_dir, convert_to_wav)
            else:
                print(f"No enclosures found for entry: {latest_entry.title}")
        else:
            print(f"No entries found in feed: {feed_url}")

# Example usage
feed_urls = [
    "https://anchor.fm/s/7c624c84/podcast/rss"
    # Add more podcast RSS feed URLs here
]
output_dir = "downloaded_podcasts"
process_latest_podcast_rss(feed_urls, output_dir, convert_to_wav=False)  # Set convert_to_wav=True if you want WAV files

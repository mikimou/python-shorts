import moviepy
from pytube import YouTube
import whisper
import json
import os
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from datetime import timedelta

# OPTIONS
ytb_video = "6T7pUEZfgdI"
bg_music_enabled = False
bg_music_video = "WE8TinxNPb0"
video_content_path = "content/video"
audio_content_path = "content/audio"
caption_content_path = "content/captions"

def download_video(link, file_name):
    yt = YouTube(link)
    yt = yt.streams.get_highest_resolution()
    try:
        yt.download(output_path=video_content_path)
        print("Download is completed successfully for " + link)
    except:
        print("Error has occured video can not be downloaded " + link)


def get_audio():
    try:
        mp4_file_path = os.path.join(video_content_path, os.listdir(video_content_path)[0])
        subprocess.run([
            'ffmpeg',
            '-i', mp4_file_path,
            os.path.join(audio_content_path, "audio.mp3")
        ])
        print("Convert is completed successfully for audio")
    except:
        print("Error has occured in conversion to audio")


# TODOOOOO
def get_ytb_transcipt():
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = SRTFormatter()
        srt_formatted = formatter.format_transcript(transcript)

        with open('main_video_captions.srt', 'w', encoding='utf-8') as f:
            f.write(srt_formatted)

        print("Transcript written to main_video_captions.srt")
    except:
        print("Transcript not found")


def audio_to_text():
    model = whisper.load_model("tiny")
    print("Whisper model loaded.")
    transcribe = model.transcribe(audio=os.path.join("content/audio", os.listdir("content/audio")[0]))
    segments = transcribe['segments']
    for segment in segments:
        startTime = str(0) + str(timedelta(seconds=int(segment['start']))) + ',000'
        endTime = str(0) + str(timedelta(seconds=int(segment['end']))) + ',000'
        text = segment['text']
        segmentId = segment['id'] + 1
        segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] == ' ' else text}\n\n"
        srtFilename = os.path.join("content/captions", f"captions.srt")
        with open(srtFilename, 'a', encoding='utf-8') as srtFile:
            srtFile.write(segment)

# download_video('https://www.youtube.com/watch?v=7MNv4_rTkfU', 'joe.mp4')
# get_audio()
audio_to_text()

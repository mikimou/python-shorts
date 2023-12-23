import moviepy
from pytube import YouTube
import whisper_timestamped
import json
import os
import subprocess

# OPTIONS
ytb_video = "6T7pUEZfgdI"
bg_music_enabled = False
bg_music_video = "WE8TinxNPb0"
content_path = "/content/"


def download_video(link, file_name):
    yt = YouTube(link)
    yt = yt.streams.get_highest_resolution()
    try:
        yt.download()
    except:
        print("Error has occured video can not be downloaded")
    print(f"Download is completed successfully for {link}")

download_video('https://www.youtube.com/watch?v=7MNv4_rTkfU', 'joe.mp4')
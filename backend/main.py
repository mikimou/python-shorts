import moviepy
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
import whisper
import json
import os
import subprocess
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from datetime import timedelta
import requests
from moviepy.config import change_settings

change_settings({'IMAGEMAGICK_BINARY': '/usr/bin/convert'})

# OPTIONS
ytb_video_link = "https://www.youtube.com/watch?v=7MNv4_rTkfU"
bg_music_enabled = False
bg_music_video = "WE8TinxNPb0"
video_content_path = "content/video"
audio_content_path = "content/audio"
caption_content_path = "content/captions"


def download_video(link):
    print('Downloading video from ytb')
    yt = YouTube(link)
    yt = yt.streams.get_highest_resolution()
    try:
        yt.download(output_path=video_content_path)
        print("Download is completed successfully for " + link)
    except:
        print("Error has occured video can not be downloaded " + link)


def get_audio():
    print('Getting audio from video file')
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


def get_ytb_transcipt(link):
    print('Locating transcript on youtube')
    try:
        video_id = link.split('=', 1)[1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = SRTFormatter()
        srt_formatted = formatter.format_transcript(transcript)

        with open(os.path.join(caption_content_path, f"captions.srt"), 'w', encoding='utf-8') as f:
            f.write(srt_formatted)

        print("Transcript downloaded from yt and written to captions.srt")
    except:
        print("Transcript not found")


def audio_to_text():
    print('Generating transcript with ai')
    try:
        model = whisper.load_model("tiny")
        print("Whisper model loaded.")
        transcribe = model.transcribe(audio=os.path.join(audio_content_path, os.listdir(audio_content_path)[0]))
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

        with open(os.path.join(caption_content_path, f"summary.txt"), 'w', encoding='utf-8') as sumfile:
            sumfile.write(transcribe['text'])

        print("Transcript generated successfully!")
    except:
        print("Generating transcript with AI failed!")


def get_top_markers(link, k=3):
    video_id = link.split('=', 1)[1]
    try:
        x = requests.get(f'http://127.0.0.1:1999/videos?part=mostReplayed&id={video_id}').json()
        print("Video markers downloaded")
        all_markers = x["items"][0]["mostReplayed"]["markers"]
        all_intensities = sorted(
            [(marker['intensityScoreNormalized'], indx) for indx, marker in enumerate(all_markers) if 4 < indx < 96],
            key=lambda x: -x[0])
        return [all_markers[indx] for (intensity, indx) in all_intensities[:k]]
    except:
        print(f"This video ({video_id}) does not contain any corresponding heat markers.")
        return None


def add_subtitles_to_video():
    generator = lambda txt: TextClip(txt, font='Noto-Sans', fontsize=40, color='yellow', bg_color='transparent')
    sub = SubtitlesClip(os.path.join(caption_content_path, os.listdir(caption_content_path)[0]), generator)
    video = VideoFileClip(os.path.join(video_content_path, os.listdir(video_content_path)[0]))
    return CompositeVideoClip([video, sub.set_position(('center', 0.7))])



def export_shorts(top_markers):
    file_num = 1
    for marker in top_markers:
        start_time = (marker["startMillis"] / 1000) - 1
        duration = 45  # must be less than 60

        # below_video = VideoFileClip(below_video_file_path).subclip(10, 10 + duration / 1e3).without_audio()
        video = add_subtitles_to_video().subclip(start_time, (start_time + duration))
        final = video.resize((1080, 1920)).speedx(1.1)
        # combined = clips_array([[video], [below_video]])
        # combined = combined.resize((1080, 1920))

        # audio_background = AudioFileClip(bgm_mp3_file_path).subclip(10, 10 + duration / 1e3).fx(
        #    moviepy.audio.fx.all.volumex, 0.9)
        # final_audio = CompositeAudioClip([combined.audio, audio_background])
        # final_clip = combined.set_audio(final_audio)

        final.write_videofile(f"out_video_{file_num}.mp4",
                              codec='libx264',
                              audio_codec='aac',
                              temp_audiofile='temp-audio.m4a',
                              remove_temp=True,
                              )
        print(f"Saved file out_video_{file_num}")
        file_num += 1


# download_video(ytb_video_link)
# get_audio()
# get_ytb_transcipt(ytb_video_link)
audio_to_text()
export_shorts(get_top_markers(ytb_video_link, k=1))

import requests
from pytube import YouTube
import moviepy
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
import os
import subprocess


def get_all_markers(video_id):
    try:
        x = requests.get(f'https://yt.lemnoslife.com/videos?part=mostReplayed&id={video_id}').json()
        print("Video markers downloaded")
        print(x["items"][0]["mostReplayed"]["markers"])
        return x["items"][0]["mostReplayed"]["markers"]
    except:
        print(f"This video ({video_id}) does not contain any corresponding heat markers.")
        return None


def get_top_k_moments(all_markers, k=10):
    all_intensities = sorted(
        [(marker['heatMarkerRenderer']['intensityScoreNormalized'], indx) for indx, marker in
         enumerate(all_markers) if indx > 4 and indx < 96], key=lambda x: -x[0])
    return [all_markers[indx] for (intensity, indx) in all_intensities[:k]]


def download_video(video_id, file_path):
    link = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(link)
    yt = yt.streams.get_highest_resolution()
    try:
        yt.download(file_path)
    except:
        print("Error has occured video can not be downloaded")
    print(f"Download is completed successfully for {video_id}")


def download_mp3(video_id, file_path):
    link = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(link)
    yt = yt.streams.get_highest_resolution()
    try:
        yt.download(file_path)

        mp4_file_path = os.path.join(file_path, os.listdir(file_path)[0])

        subprocess.run([
            'ffmpeg',
            '-i', mp4_file_path,
            os.path.join(file_path, "bgm.mp3")
        ])
    except:
        print("Error has occured video can not be downloaded")

    print(f"Download is completed successfully for {video_id}")


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = SRTFormatter()
        srt_formatted = formatter.format_transcript(transcript)

        with open('main_video_captions.srt', 'w', encoding='utf-8') as f:
            f.write(srt_formatted)

        print("Transcript written to main_video_captions.srt")
    except:
        print("Transcript not found")


def add_subtitles_to_video(video_path):
    generator = lambda txt: TextClip(txt, font='Georgia-Regular', fontsize=40, color='white', bg_color='black')
    sub = SubtitlesClip("/content/main_video_captions.srt", generator)
    video = VideoFileClip(video_path)
    return CompositeVideoClip([video, sub.set_position(('center', 'bottom'))])


def download_videos(videos):
    file_num = 1
    for video in videos:
        video.write_videofile(f"out_video_{file_num}.mp4",
                              codec='libx264',
                              audio_codec='aac',
                              temp_audiofile='temp-audio.m4a',
                              remove_temp=True
                              )
        print(f"Saved file out_video_{file_num}")
        file_num += 1


main_video_id = "6T7pUEZfgdI"
below_video_id = "Pt5_GSKIWQM"
bgm_music_video_id = "WE8TinxNPb0"
k = 2

all_markers = get_all_markers(main_video_id)
top_k_markers = get_top_k_moments(all_markers, k=k)

main_video_file_path = "/content/main_video"
below_video_file_path = "/content/below_video"
bgm_mp3_file_path = "/content/bgm_music"

download_video(main_video_id, main_video_file_path)
download_video(below_video_id, below_video_file_path)
download_mp3(bgm_music_video_id, bgm_mp3_file_path)

main_video_file_path = os.path.join(main_video_file_path, os.listdir(main_video_file_path)[0])
below_video_file_path = os.path.join(below_video_file_path, os.listdir(below_video_file_path)[0])
bgm_mp3_file_path = os.path.join(bgm_mp3_file_path, os.listdir(bgm_mp3_file_path)[0])

get_transcript(main_video_id)

main_video_with_subtitles = add_subtitles_to_video(main_video_file_path)

videos = []

for marker in top_k_markers:
    start_time = marker["heatMarkerRenderer"]["timeRangeStartMillis"]
    duration = marker["heatMarkerRenderer"]["markerDurationMillis"]

    if (duration / 1e3) > 60:
        duration = 59 * 1e3

    below_video = VideoFileClip(below_video_file_path).subclip(10, 10 + duration / 1e3).without_audio()
    video = main_video_with_subtitles.subclip(start_time / 1e3, (start_time + duration) / 1e3)

    combined = clips_array([[video], [below_video]])
    combined = combined.resize((1080, 1920))

    audio_background = AudioFileClip(bgm_mp3_file_path).subclip(10, 10 + duration / 1e3).fx(
        moviepy.audio.fx.all.volumex, 0.9)
    final_audio = CompositeAudioClip([combined.audio, audio_background])
    final_clip = combined.set_audio(final_audio)

    videos.append(final_clip)

download_videos(videos)

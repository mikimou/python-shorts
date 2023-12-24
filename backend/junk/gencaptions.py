from datetime import timedelta
import json
import os
import whisper

# with open("sample.json", "r") as read_file:
#    data = json.load(read_file)
model = whisper.load_model("tiny")
print("Whisper model loaded.")
transcribe = model.transcribe(audio=os.path.join("content/audio", os.listdir("content/audio")[0]))
segments = transcribe['segments']
# segments = data['segments']

for segment in segments:
    startTime = str(0) + str(timedelta(seconds=int(segment['start']))) + ',000'
    endTime = str(0) + str(timedelta(seconds=int(segment['end']))) + ',000'
    text = segment['text']
    segmentId = segment['id'] + 1
    segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] == ' ' else text}\n\n"

    srtFilename = os.path.join("content/captions", f"captions.srt")
    with open(srtFilename, 'a', encoding='utf-8') as srtFile:
        srtFile.write(segment)

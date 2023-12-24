import whisper_timestamped
import json

audio = whisper_timestamped.load_audio("sii-gleb.wav")
model = whisper_timestamped.load_model("tiny", device="cpu")
result = whisper_timestamped.transcribe(model, audio)
#print(json.dumps(result, indent=2, ensure_ascii=False))
with open("sample.json", "w") as outfile:
    outfile.write(json.dumps(result, indent=2, ensure_ascii=False))


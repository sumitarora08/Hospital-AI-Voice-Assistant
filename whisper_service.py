from faster_whisper import WhisperModel

print("Loading Whisper model...")
model = WhisperModel("tiny", device="cpu")
print("Whisper ready!")


def speech_to_text(audio_path):
    segments, info = model.transcribe(audio_path)

    text = ""
    for s in segments:
        text += s.text + " "

    return text.strip()

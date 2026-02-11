from whisper_service import speech_to_text

print("Speak something like:")
print("My name is Rahul I have fever at five pm")

text = speech_to_text("test.wav")
print("Whisper Text:", text)

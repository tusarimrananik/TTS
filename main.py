from scripts.get_images import download_images
from scripts.text_to_speech import load_tts, generate_audio

# download_images("nature", per_page=10)

sentences = [
    "There are four things you must never do if you want to rise.",
    "Never quit, for every champion was once a beginner who refused to give up.",
]
speaker_wav = "assets/audio/reference/Brain.wav"
tts = load_tts()
generate_audio(tts, sentences, speaker_wav)

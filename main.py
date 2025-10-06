# from scripts.get_images import download_images
# from scripts.text_to_speech import load_tts, generate_audio
from scripts.script import generate_motivational_text

# DOWNLOAD AND SAVE IMAGES
# download_images("tech", per_page=10)

# TEXT TO SPEACH
# sentences = [
#     "Every setback is a setup for a comeback that shapes your destiny.",
#     "Your thoughts become your reality, choose them with wisdom.",
#     "Success is not final, failure is not fatal: it is the courage to continue that counts.",
#     "The only limit to our realization of tomorrow will be our doubts of today.",
# ]
# speaker_wav = "assets/audio/reference/Brain.wav"
# tts = load_tts()
# generate_audio(tts, sentences, speaker_wav)

# MOTIVATIONAL SCRIPTS
prompt = "Overcoming challenges and achieving success"
print(generate_motivational_text(prompt))

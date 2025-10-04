import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
from moviepy.video.fx.all import resize

ASSETS_DIR = "assets"
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
VIDEO_DIR = os.path.join(ASSETS_DIR, "videos")
SUBTITLE_DIR = os.path.join(ASSETS_DIR, "subtitles")

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(SUBTITLE_DIR, exist_ok=True)

# ---------- Subtitle Helpers ----------
def format_timestamp(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02},{millis:03}"

def generate_srt(text, audio_duration, output_file):
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    duration_per_sentence = audio_duration / len(sentences)
    start = 0.0
    lines = []
    for i, sentence in enumerate(sentences, 1):
        end = start + duration_per_sentence
        lines.append(f"{i}\n{format_timestamp(start)} --> {format_timestamp(end)}\n{sentence}\n")
        start = end
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return output_file

def srt_to_seconds(timestamp):
    h, m, s_ms = timestamp.split(":")
    s, ms = s_ms.split(",")
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def add_subtitles(video, srt_file):
    clips = [video]
    with open(srt_file, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n")
    for block in blocks:
        if not block.strip():
            continue
        parts = block.split("\n")
        if len(parts) < 3:
            continue
        times = parts[1].split(" --> ")
        start = srt_to_seconds(times[0])
        end = srt_to_seconds(times[1])
        sentence = " ".join(parts[2:])
        txt_clip = (TextClip(sentence, fontsize=60, color="white", font="Arial-Bold", stroke_color="black", stroke_width=2)
                    .set_position(("center", "bottom"))
                    .set_duration(end - start)
                    .set_start(start))
        clips.append(txt_clip)
    return CompositeVideoClip(clips)

# ---------- Ken Burns Effect ----------
def ken_burns_effect(image_path, duration=5):
    clip = ImageClip(image_path, duration=duration)
    return (clip
            .resize(lambda t: 1 + 0.05 * (t/duration))  # slow zoom
            .set_position(lambda t: ("center", int(30 * (t/duration)))))  # slight pan

# ---------- Video Creator ----------
def create_vertical_video(images, audio_file, text, output_file="final_shorts.mp4"):
    audio = AudioFileClip(audio_file)
    audio_duration = audio.duration

    per_image_duration = audio_duration / len(images)
    video_clips = [ken_burns_effect(img, duration=per_image_duration) for img in images]
    video = concatenate_videoclips(video_clips).set_audio(audio)

    # generate and burn subtitles
    srt_file = os.path.join(SUBTITLE_DIR, "subtitles.srt")
    generate_srt(text, audio_duration, srt_file)
    final = add_subtitles(video, srt_file)

    final.write_videofile(os.path.join(VIDEO_DIR, output_file), fps=30, codec="libx264")

if __name__ == "__main__":
    # Example usage
    text = "There are four things you must never do if you want to rise. Never waste time. Never ignore learning. Never fear failure. And never give up."
    images = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if f.endswith(".jpg")]
    audio_file = os.path.join(AUDIO_DIR, "tts_output.wav")

    create_vertical_video(images, audio_file, text)

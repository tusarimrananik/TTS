from pathlib import Path
import subprocess

# ===== CONFIG =====
AUDIO_PATH = Path("assets/audio/generated/final_output.wav")
VIDEO_PATH = Path("output_shorts.mp4")              # already rendered video
ASS_PATH = Path("assets/subtitles/final_output.ass")
OUT_PATH = Path("output_shorts_subs.mp4")
MODEL = "small"
LANG = "en"
NORMAL_COLOR = "&H00FFFFFF"  # White (normal subtitle color)
HIGHLIGHT_COLOR = "&H00FF0000"  # Red (highlight color while spoken)
# ===================

def make_ass_with_whisperx(audio_path, ass_path, model_size, lang):
    import whisperx
    device = "cpu"
    print("[Subs] Transcribing with WhisperX...")
    asr = whisperx.load_model(model_size, device, compute_type="int8")  # CPU-safe
    res = asr.transcribe(str(audio_path), language=lang)
    print("[Subs] Aligning words...")
    align_model, metadata = whisperx.load_align_model(language_code=lang, device=device)
    aligned = whisperx.align(res["segments"], align_model, metadata, str(audio_path), device)

    def t(t):
        if t < 0: t = 0.0
        h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); cs = int(round((t - int(t)) * 100))
        return f"{h}:{m:02}:{s:02}.{cs:02}"

    # Modify the words_to_k function to add proper spacing between words
    def words_to_k(words):
        parts = []
        for w in words:
            if w.get("start") is None or w.get("end") is None: continue
            dur = max(1, int(round((w["end"] - w["start"]) * 100)))
            token = w.get("word", "").strip()
            if token:
                parts.append(rf"{{\k{dur}\c&H00FF0000}}{token}")  # Highlight word in red during speech
        return " ".join(parts).strip()  # Ensure there is space between words

    header = """[Script Info]
PlayResX:1080
PlayResY:1920
Alignment: 2  # Center the subtitle text
PrimaryColour: &H00FFFFFF  # Default White
SecondaryColour: &H00FF0000  # Highlight Red

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kara,Arial,54,&H00FFFFFF,&H00FF9900,&H00111111,&H64000000,0,0,0,0,100,100,0,0,1,3,0,2,60,60,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for seg in aligned["segments"]:
        start = t(seg["start"]); end = t(seg["end"])
        textk = words_to_k(seg.get("words", [])) or seg.get("text", "").strip()
        lines.append(f"Dialogue:0,{start},{end},Kara,,0,0,0,,{textk}\n")

    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text("".join(lines), encoding="utf-8")
    return ass_path

def burn_ass_ffmpeg(video_in, ass_path, out_path):
    ensure_ffmpeg()
    abs_ass = ass_path.resolve().as_posix()
    # escape drive letter on Windows for ffmpeg filter
    if abs_ass[1:3] == ':/' or abs_ass[1:3] == ':\\':
        drive = abs_ass[0]
        rest = abs_ass[2:]
        abs_ass = f"{drive}\\:{rest}"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", f"subtitles='{abs_ass}'",
        "-c:v", "libx264", "-c:a", "aac", "-preset", "medium", "-crf", "18",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)
    print(f"[Video] Wrote {out_path}")

def ensure_ffmpeg():
    if subprocess.call("ffmpeg -version", shell=True) != 0:
        raise RuntimeError("ffmpeg not found on PATH. Install and add to PATH (choco install ffmpeg on Windows).")

def main():
    make_ass_with_whisperx(AUDIO_PATH, ASS_PATH, MODEL, LANG)
    burn_ass_ffmpeg(VIDEO_PATH, ASS_PATH, OUT_PATH)

if __name__ == "__main__":
    main()

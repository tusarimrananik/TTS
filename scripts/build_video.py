from pathlib import Path
import sys
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    vfx,
)

# ============== CONFIG ==============
IMAGES_DIR = Path("assets/images")
AUDIO_PATH = Path("assets/audio/generated/final_output.wav")

OUT_BASE = Path("output_shorts")
OUT_MP4 = OUT_BASE.with_suffix(".mp4")

TARGET_W, TARGET_H = 1080, 1920  # Shorts vertical
FPS = 10                         # Tip: 24 or 30 looks smoother
MIN_PER_IMAGE = 3.0
WHIP_MAX = 0.45                  # repurposed as the max crossfade duration cap
CONTRAST = 1.08
# ====================================


# ---------- Helpers ----------
def list_images(folder: Path):
    """Return sorted list of image paths (jpg/png)."""
    imgs = sorted(
        [p for p in folder.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}],
        key=lambda p: (
            p.stem.isdigit(),
            int(p.stem) if p.stem.isdigit() else p.stem.lower(),
            p.name.lower(),
        ),
    )
    if not imgs:
        raise FileNotFoundError(f"No images found in {folder}")
    return imgs


def sample_evenly(paths, k):
    """Evenly sample k elements from list."""
    n = len(paths)
    if k <= 1:
        return [paths[0]]
    idxs = [round(i * (n - 1) / (k - 1)) for i in range(k)]
    return [paths[i] for i in idxs]


def ease_in_out_cubic(p: float) -> float:
    """Smooth ease curve used for the slow zoom."""
    p = max(0.0, min(1.0, p))
    if p < 0.5:
        return 4 * p * p * p
    return 1 - ((-2 * p + 2) ** 3) / 2


# ---------- Clip builder (simple slow zoom, centered, no pan) ----------
def make_clip(
    img_path,
    duration,
    idx,
    target_w,
    target_h,
    contrast=1.08,
    z_start=1.00,   # subtle start zoom
    z_end=1.06      # subtle end zoom (tweak to taste)
):
    """
    Image clip with a gentle, smooth Ken-Burns style zoom (centered).
    """
    base = ImageClip(str(img_path)).set_duration(duration)

    # Ensure the image covers the target frame at t=0
    cover_scale = max(target_w / base.w, target_h / base.h)
    base = base.resize(cover_scale)

    # Pre-contrast
    base = base.fx(vfx.lum_contrast, lum=0, contrast=contrast, contrast_thr=128)

    # Smooth in-out zoom curve
    def z_func(t: float) -> float:
        p = t / max(duration, 1e-6)
        e = ease_in_out_cubic(p)
        return z_start + (z_end - z_start) * e

    zoomed = base.resize(lambda t: z_func(t))

    # Always centered (no pan)
    def pos_center(t: float):
        z = z_func(t)
        Wt, Ht = base.w * z, base.h * z
        x = (target_w - Wt) / 2.0
        y = (target_h - Ht) / 2.0
        return (x, y)

    # Composite onto fixed canvas
    comp = CompositeVideoClip([zoomed.set_position(pos_center)], size=(target_w, target_h))
    comp = comp.set_duration(duration)
    return comp


# ---------- Build video (slow zoom + crossfade) ----------
def build_video(images, audio_clip):
    """
    Combine images and audio into one short-form video
    with slow zoom per image and crossfade transitions.
    """
    total = max(0.01, audio_clip.duration)

    # Decide how many images to keep (>= MIN_PER_IMAGE seconds each)
    max_images = max(1, int(total // MIN_PER_IMAGE))
    if len(images) > max_images:
        images = sample_evenly(images, max_images)

    n = len(images)
    per_img = total / n

    # Crossfade duration scales with per-image time (capped by WHIP_MAX)
    xfade = min(WHIP_MAX, max(0.25, per_img * 0.22))

    # Build base clips
    base_clips = []
    for i, p in enumerate(images):
        base_clips.append(
            make_clip(
                p,
                duration=per_img,
                idx=i,
                target_w=TARGET_W,
                target_h=TARGET_H,
                contrast=CONTRAST,
                # tiny variety in zoom amount to avoid looking identical
                z_start=1.00,
                z_end=1.06 if (i % 2 == 0) else 1.08,
            )
        )

    # Prepare crossfading sequence:
    #   - Give every clip except the first a crossfade-in of `xfade`
    #   - Use negative padding to overlap neighbors by `xfade`
    clips = [base_clips[0]] + [c.crossfadein(xfade) for c in base_clips[1:]]
    video = concatenate_videoclips(clips, method="compose", padding=-xfade)

    # Gentle global fade on the whole piece (optional)
    global_fade_in = min(0.3, per_img * 0.15)
    global_fade_out = min(0.25, per_img * 0.12)
    try:
        video = video.fadein(global_fade_in).fadeout(global_fade_out)
    except AttributeError:
        # Fallback for older MoviePy versions
        video = video.fx(vfx.fadein, global_fade_in).fx(vfx.fadeout, global_fade_out)

    # Add audio and clamp to exact audio duration
    video = video.set_audio(audio_clip).set_duration(total)
    return video


def main():
    try:
        audio = AudioFileClip(str(AUDIO_PATH))
        images = list_images(IMAGES_DIR)

        print(f"[Info] Building video from {len(images)} images and audio ({audio.duration:.2f}s)...")

        video = build_video(images, audio)
        video.write_videofile(
            str(OUT_MP4),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            bitrate="8000k",
        )
        print(f"[Video] Wrote {OUT_MP4}")

    except Exception as e:
        print("[Error]", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

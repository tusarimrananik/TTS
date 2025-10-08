from __future__ import annotations

import subprocess
from pathlib import Path
import re

def burn_subtitles(
    video_in: str | Path,
    ass_path: str | Path,
    out_path: str | Path,
    *,
    vcodec: str = "libx264",
    acodec: str = "aac",
    preset: str = "medium",
    crf: int = 18,
    pix_fmt: str = "yuv420p",
    overwrite: bool = True,
    loglevel: str = "error",  # show only errors
) -> Path:
    video_in = Path(video_in).resolve()
    ass_path = Path(ass_path).resolve()
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build a filter-safe path: POSIX slashes + escape drive colon (C\:/...)
    p = ass_path.as_posix()
    if re.match(r"^[A-Za-z]:/", p):
        p = p[0] + r"\:" + p[2:]

    # Use the subtitles filter (libass) and wrap path in single quotes
    vf = f"subtitles=filename='{p}'"

    cmd = [
        "ffmpeg",
        "-y" if overwrite else "-n",
        "-loglevel", loglevel,
        "-i", str(video_in),
        "-vf", vf,
        "-c:v", vcodec,
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", pix_fmt,
        "-c:a", acodec,   # re-encode audio to avoid muxer quirks
        str(out_path),
    ]

    subprocess.run(cmd, check=True)
    return out_path

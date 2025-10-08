from __future__ import annotations
from pathlib import Path


def generate_subtitles(
    audio_path: str | Path,
    ass_out_path: str | Path,
    *,
    text_to_align: str,
    lang: str = "en",
    device: str = "cpu",
    playres_w: int = 1080,
    playres_h: int = 1920,
    font: str = "DejaVu Sans Mono",
    fontsize: int = 54,
    primary_color: str = "&H00FFFFFF",
    outline_color: str = "&H00111111",
    alignment: int = 5,
    margin_l: int = 60,
    margin_r: int = 60,
    margin_v: int = 40,
    highlight_bg_color: str = "&H8033CCFF",
    highlight_text_color: str = "&H00000000",
) -> Path:
    import os
    from typing import List
    from pydub import AudioSegment
    import whisperx  # type: ignore

    # WhisperX and PyTorch automatically look for checkpoints in TORCH_HOME/hub/checkpoints.
    # By setting TORCH_HOME to your project's "models" folder, we make WhisperX treat:
    # models/hub/checkpoints/wav2vec2_fairseq_base_ls960_asr_ls960.pth
    # as its official local checkpoint. It will *not* search .cache or Hugging Face.
    # The two environment variables below disable all online model fetching.
    models_root = Path("models").resolve()
    ckpt = (
        models_root
        / "hub"
        / "checkpoints"
        / "wav2vec2_fairseq_base_ls960_asr_ls960.pth"
    )
    if not ckpt.exists():
        raise FileNotFoundError(f"Missing alignment checkpoint: {ckpt}")

    os.environ["TORCH_HOME"] = str(models_root)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    ass_out_path = Path(ass_out_path)
    ass_out_path.parent.mkdir(parents=True, exist_ok=True)

    duration_s = AudioSegment.from_file(audio_path).duration_seconds
    segments = [{"start": 0.0, "end": duration_s, "text": text_to_align}]

    align_model, metadata = whisperx.load_align_model(
        language_code=lang,
        device=device,
    )
    aligned = whisperx.align(segments, align_model, metadata, str(audio_path), device)

    def fmt_time(t: float) -> str:
        if t < 0:
            t = 0.0
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        cs = int(round((t - int(t)) * 100))
        return f"{h}:{m:02}:{s:02}.{cs:02}"

    def esc(text: str) -> str:
        return (
            text.replace("\\", r"\\")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("\n", r"\N")
        )

    def has_times(w: dict) -> bool:
        return w.get("start") is not None and w.get("end") is not None

    def q2(text: str) -> str:
        return r"{\q2}" + text

    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX:{playres_w}\n"
        f"PlayResY:{playres_h}\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Base,{font},{fontsize},{primary_color},&H000000FF,{outline_color},&H64000000,"
        f"0,0,0,0,100,100,0,0,1,3,0,{alignment},{margin_l},{margin_r},{margin_v},1\n"
        f"Style: HL,{font},{fontsize},{highlight_text_color},&H000000FF,&H00000000,{highlight_bg_color},"
        f"0,0,0,0,100,100,0,0,3,0,0,{alignment},{margin_l},{margin_r},{margin_v},1\n\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )

    lines: List[str] = [header]

    for seg in aligned.get("segments", []):
        words = [w for w in seg.get("words", []) if has_times(w)]
        if not words:
            continue

        display_tokens = [
            str(w.get("word", "")).strip()
            for w in words
            if str(w.get("word", "")).strip()
        ]
        base_text = " ".join(display_tokens)
        if base_text:
            lines.append(
                f"Dialogue:0,{fmt_time(seg['start'])},{fmt_time(seg['end'])},Base,,{margin_l},{margin_r},{margin_v},,{q2(esc(base_text))}\n"
            )

        for i, w in enumerate(words):
            token = str(w.get("word", "")).strip()
            if not token:
                continue
            pad_len = len(" ".join(display_tokens[:i])) + (1 if i > 0 else 0)
            overlay_text = (" " * pad_len) + token
            lines.append(
                f"Dialogue:1,{fmt_time(float(w['start']))},{fmt_time(float(w['end']))},HL,,{margin_l},{margin_r},{margin_v},,{q2(esc(overlay_text))}\n"
            )

    ass_out_path.write_text("".join(lines), encoding="utf-8")
    return ass_out_path
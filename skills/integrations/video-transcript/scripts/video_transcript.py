#!/usr/bin/env python3
"""Fetch a video's metadata and transcript from a link, ready for an agent to read.

Works on any site yt-dlp supports (YouTube, X/Twitter, TikTok, Vimeo, Instagram,
Loom, podcasts, ...) and on local video or audio files. Published captions come
first; when a video has none, the audio is transcribed with ElevenLabs Scribe or
a local MLX model.

Usage:
    python3 video_transcript.py URL [--out DIR] [--lang CODE] [--asr ENGINE]
                                    [--frames] [--cookies-from-browser BROWSER]

Writes into DIR/<site>-<id>/: transcript.md (the deliverable), info.json (raw
yt-dlp metadata), the raw caption or ASR file, and frames/ with --frames.
Prints a summary per video. Exit codes: 0 ok, 1 error, 2 no transcript
available, 3 the link is a playlist or channel (entries printed, one per line).

Stdlib only; needs yt-dlp (or uv to run it), and ffmpeg for audio and frames.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

Info = dict[str, Any]
Engine = Literal["auto", "elevenlabs", "parakeet", "whisper", "none"]

# Languages parakeet-tdt-0.6b-v3 transcribes; anything else goes to whisper.
PARAKEET_LANGS = set(
    "bg hr cs da nl en et fi fr de el hu it lv lt mt pl pt ro sk sl es sv ru uk".split()
)
WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"
SCRIBE_MODEL = "scribe_v2"
TROUBLESHOOTING = "references/troubleshooting.md"


@dataclass
class Segment:
    start: float
    end: float
    text: str
    speaker: Optional[str] = None


class Failure(Exception):
    """A user-facing error; the message says what to try next."""


# ---------------------------------------------------------------- yt-dlp


def ytdlp_base(cookies_from_browser: Optional[str]) -> list[str]:
    """The yt-dlp command: the installed binary, else the latest via uvx."""
    if shutil.which("yt-dlp"):
        cmd = ["yt-dlp"]
    elif shutil.which("uvx"):
        cmd = ["uvx", "--from", "yt-dlp[default]", "yt-dlp"]
    else:
        raise Failure("yt-dlp not found. Install it (brew install yt-dlp, or pip install 'yt-dlp[default]') or install uv.")
    cmd += ["--no-warnings", "--ignore-config"]
    if cookies_from_browser:
        cmd += ["--cookies-from-browser", cookies_from_browser]
    return cmd


def run_ytdlp(base: list[str], args: list[str]) -> str:
    proc = subprocess.run(base + args, capture_output=True, text=True)
    if proc.returncode != 0:
        err = proc.stderr.strip().splitlines()
        tail = "\n".join(err[-4:]) or f"exit {proc.returncode}"
        raise Failure(f"yt-dlp failed:\n{tail}\nSee {TROUBLESHOOTING} for bot checks, rate limits, and login-only posts.")
    return proc.stdout


def extract_info(base: list[str], url: str) -> Info:
    info: Info = json.loads(run_ytdlp(base, ["-J", "--flat-playlist", "--no-playlist", url]))
    return info


# ---------------------------------------------------------------- captions


def original_language(info: Info) -> Optional[str]:
    """The spoken language: yt-dlp's field, else YouTube's '<lang>-orig' auto track."""
    if info.get("language"):
        return str(info["language"])
    for key in info.get("automatic_captions") or {}:
        if key.endswith("-orig"):
            return str(key)[: -len("-orig")]
    return None


def same_lang(key: str, lang: str) -> bool:
    return key == lang or key.split("-")[0] == lang.split("-")[0]


def pick_track(info: Info, wanted: Optional[str]) -> Optional[tuple[str, bool]]:
    """Choose (track key, is_auto). Human captions beat auto captions, the spoken
    language beats translations, and auto-translated tracks are used only when
    the caller asked for that language explicitly."""
    manual = {k: v for k, v in (info.get("subtitles") or {}).items() if k != "live_chat" and v}
    auto = {k: v for k, v in (info.get("automatic_captions") or {}).items() if v}
    spoken = original_language(info)
    target = wanted or spoken or "en"

    order: list[tuple[str, bool]] = []
    order += [(k, False) for k in manual if same_lang(k, target)]
    order += [(k, True) for k in auto if k.endswith("-orig") and same_lang(k[: -len("-orig")], target)]
    if wanted or (spoken and same_lang(target, spoken)):
        order += [(k, True) for k in auto if k == target]
    if not wanted:
        order += [(k, False) for k in manual if same_lang(k, "en")]
        order += [(k, False) for k in manual]
        order += [(k, True) for k in auto if k.endswith("-orig")]
        if len(auto) == 1:  # non-YouTube sites expose one auto track: the spoken one
            order += [(k, True) for k in auto]
    return order[0] if order else None


def download_captions(base: list[str], info_path: Path, dest: Path, key: str, is_auto: bool) -> Optional[Path]:
    run_ytdlp(base, [
        "--load-info-json", str(info_path), "--skip-download",
        "--write-auto-subs" if is_auto else "--write-subs",
        "--sub-langs", re.escape(key), "--sub-format", "json3/vtt/srt/best",
        "-o", str(dest / "captions"),
    ])
    found = sorted(dest.glob(f"captions.{key}.*"))
    return found[0] if found else None


def parse_json3(raw: str) -> list[Segment]:
    segs: list[Segment] = []
    for ev in json.loads(raw).get("events", []):
        if "segs" not in ev:
            continue
        text = " ".join("".join(s.get("utf8", "") for s in ev["segs"]).split())
        if not text:
            continue
        start = ev.get("tStartMs", 0) / 1000
        segs.append(Segment(start, start + ev.get("dDurationMs", 0) / 1000, text))
    return segs


TIMING = re.compile(r"((?:\d+:)?\d{1,2}:\d{2}[.,]\d{3})\s*-->\s*((?:\d+:)?\d{1,2}:\d{2}[.,]\d{3})")


def clock_to_seconds(stamp: str) -> float:
    parts = [float(p) for p in stamp.replace(",", ".").split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


def parse_cues(raw: str) -> list[Segment]:
    """WebVTT or SRT. Drops the rolling repeats auto captions carry, where each
    cue restates the line before it."""
    segs: list[Segment] = []
    recent: list[str] = []
    for block in re.split(r"\n\s*\n", raw.replace("\r", "")):
        lines = block.strip().splitlines()
        timing_idx = next((i for i, ln in enumerate(lines) if TIMING.search(ln)), None)
        if timing_idx is None:
            continue
        m = TIMING.search(lines[timing_idx])
        assert m
        start, end = clock_to_seconds(m.group(1)), clock_to_seconds(m.group(2))
        for line in lines[timing_idx + 1:]:
            text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", line)).split())
            if not text or text in recent:
                continue
            recent = (recent + [text])[-3:]
            segs.append(Segment(start, end, text))
    return segs


def parse_caption_file(path: Path) -> Optional[list[Segment]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".json3":
        return parse_json3(raw)
    if path.suffix in (".vtt", ".srt"):
        return parse_cues(raw)
    return None


# ---------------------------------------------------------------- speech to text


def choose_engine(requested: Engine, lang: Optional[str]) -> Engine:
    if requested != "auto":
        return requested
    if os.environ.get("ELEVENLABS_API_KEY"):
        return "elevenlabs"
    if sys.platform == "darwin" and platform.machine() == "arm64" and shutil.which("uvx"):
        return "parakeet" if not lang or lang.split("-")[0] in PARAKEET_LANGS else "whisper"
    return "none"


def download_audio(base: list[str], info_path: Path, dest: Path) -> Path:
    run_ytdlp(base, [
        "--load-info-json", str(info_path), "-f", "ba[abr<=?128]/ba/b", "-x",
        "-o", str(dest / "audio.%(ext)s"),
    ])
    found = [p for p in dest.glob("audio.*") if p.suffix not in (".part", ".ytdl")]
    if not found:
        raise Failure("Audio download produced no file.")
    return found[0]


def words_to_segments(words: list[dict[str, Any]]) -> list[Segment]:
    """Scribe returns words with speaker ids; cut them into sentences."""
    segs: list[Segment] = []
    cur: Optional[Segment] = None
    for w in words:
        if w.get("type") == "audio_event":
            continue
        speaker = w.get("speaker_id")
        if w.get("type") == "word" and (cur is None or speaker != cur.speaker or w["start"] - cur.end > 1.5):
            if cur and cur.text.strip():
                segs.append(cur)
            cur = Segment(w["start"], w["end"], "", speaker)
        if cur is None:
            continue
        cur.text += w["text"]
        cur.end = max(cur.end, w.get("end", cur.end))
        if w.get("type") == "word" and re.search(r"[.?!]$", w["text"]):
            segs.append(cur)
            cur = None
    if cur and cur.text.strip():
        segs.append(cur)
    for s in segs:
        s.text = " ".join(s.text.split())
    return segs


def transcribe_elevenlabs(audio: Path, dest: Path, lang: Optional[str]) -> list[Segment]:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise Failure("ELEVENLABS_API_KEY is not set.")
    fields = {"model_id": SCRIBE_MODEL, "diarize": "true", "tag_audio_events": "false"}
    if lang:
        fields["language_code"] = lang.split("-")[0]
    boundary = uuid.uuid4().hex
    body = b"".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, v in fields.items()
    )
    body += (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{audio.name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + audio.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/speech-to-text", data=body, method="POST",
        headers={"xi-api-key": key, "Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=1800) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raise Failure(f"ElevenLabs Scribe failed: HTTP {e.code} {e.read().decode(errors='replace')[:300]}")
    (dest / "asr.json").write_text(raw)
    return words_to_segments(json.loads(raw).get("words", []))


def transcribe_local(engine: Engine, audio: Path, dest: Path, lang: Optional[str]) -> list[Segment]:
    if not shutil.which("uvx"):
        raise Failure("Local transcription runs through uvx; install uv first.")
    out = Path(tempfile.mkdtemp(dir=dest))
    if engine == "parakeet":
        cmd = ["uvx", "parakeet-mlx", str(audio), "--output-format", "json", "--output-dir", str(out)]
    else:
        cmd = ["uvx", "--from", "mlx-whisper", "mlx_whisper", str(audio), "--model", WHISPER_MODEL,
               "--output-format", "json", "--output-dir", str(out)]
        if lang:
            cmd += ["--language", lang.split("-")[0]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    produced = list(out.glob("*.json"))
    if proc.returncode != 0 or not produced:
        raise Failure(f"{engine} failed:\n{proc.stderr.strip()[-600:]}")
    shutil.move(str(produced[0]), dest / "asr.json")
    shutil.rmtree(out, ignore_errors=True)
    data = json.loads((dest / "asr.json").read_text())
    items = data.get("sentences") or data.get("segments") or []
    return [Segment(float(s["start"]), float(s["end"]), " ".join(s["text"].split())) for s in items if s["text"].strip()]


# ---------------------------------------------------------------- frames


def extract_frames(base: list[str], info: Info, info_path: Path, dest: Path, limit: int = 40) -> list[tuple[float, Path]]:
    """Stills from a <=720p copy for reading on-screen code, slides, and diagrams:
    one at every scene change, plus one whenever the screen has been still for a
    while (code edits rarely register as scene changes). Thinned evenly to `limit`."""
    gap = max(10, int(float(info.get("duration") or 0) / limit))
    run_ytdlp(base, [
        "--load-info-json", str(info_path), "-f", "bv*[height<=720]/b[height<=720]/bv*/b",
        "-o", str(dest / "frames-source.%(ext)s"),  # not video.*, which video-analysis keeps in the same folder
    ])
    video = next(p for p in dest.glob("frames-source.*") if p.suffix not in (".part", ".ytdl"))
    frames_dir = dest / "frames"
    frames_dir.mkdir(exist_ok=True)
    proc = subprocess.run([
        "ffmpeg", "-hide_banner", "-i", str(video),
        "-vf", f"select='eq(n,0)+gt(scene,0.3)+gte(t-prev_selected_t,{gap})',showinfo,scale='min(1280,iw)':-2",
        "-fps_mode", "vfr", "-q:v", "4", str(frames_dir / "f%04d.jpg"),
    ], capture_output=True, text=True)
    video.unlink(missing_ok=True)
    times = [float(t) for t in re.findall(r"pts_time:([\d.]+)", proc.stderr)]
    files = sorted(frames_dir.glob("f*.jpg"))
    pairs = list(zip(times, files))
    keep = set(range(0, len(pairs), max(1, -(-len(pairs) // limit))))
    result: list[tuple[float, Path]] = []
    for i, (t, f) in enumerate(pairs):
        named = frames_dir / f"{int(t):05d}s.jpg"
        if i in keep and not named.exists():
            f.rename(named)
            result.append((t, named))
        else:
            f.unlink()
    return result


# ---------------------------------------------------------------- rendering


def fmt_clock(seconds: float, duration: float) -> str:
    s = int(seconds)
    h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if duration >= 3600 else f"{m:02d}:{sec:02d}"


def fmt_count(n: Any) -> Optional[str]:
    return f"{n:,}" if isinstance(n, int) else None


def most_replayed(info: Info, top: int = 3) -> list[float]:
    """Peaks of YouTube's 'most replayed' heatmap, at least a minute apart."""
    heat = sorted(info.get("heatmap") or [], key=lambda h: -h.get("value", 0))
    picks: list[float] = []
    for h in heat:
        if all(abs(h["start_time"] - p) >= 60 for p in picks):
            picks.append(h["start_time"])
        if len(picks) == top:
            break
    return sorted(picks)


def paragraphs(segs: list[Segment], chapters: list[dict[str, Any]]) -> list[tuple[Optional[str], Segment]]:
    """Merge segments into ~1-minute paragraphs, breaking at speaker changes and
    chapter starts. Returns (chapter title if one starts here, paragraph)."""
    starts = [(float(c.get("start_time", 0)), str(c.get("title", ""))) for c in chapters]
    out: list[tuple[Optional[str], Segment]] = []
    cur: Optional[Segment] = None
    pending_chapter: Optional[str] = None
    for seg in segs:
        while starts and seg.start >= starts[0][0] - 0.5:
            pending_chapter = starts.pop(0)[1]
            if cur:
                out.append((None, cur))
                cur = None
        span = seg.end - cur.start if cur else 0
        sentence_end = bool(cur and re.search(r"[.?!\"”)]$", cur.text))
        if cur and (seg.speaker != cur.speaker or span >= 90 or (span >= 50 and sentence_end)):
            out.append((None, cur))
            cur = None
        if cur is None:
            cur = Segment(seg.start, seg.end, seg.text, seg.speaker)
            if pending_chapter is not None:
                out.append((pending_chapter, Segment(seg.start, seg.start, "")))
                pending_chapter = None
        else:
            cur.text += " " + seg.text
            cur.end = seg.end
    if cur:
        out.append((None, cur))
    return out


def render(info: Info, segs: list[Segment], source: str, frames: list[tuple[float, Path]]) -> str:
    dur = float(info.get("duration") or (segs[-1].end if segs else 0))
    url = info.get("webpage_url") or info.get("original_url") or ""
    who = info.get("channel") or info.get("uploader") or info.get("uploader_id")
    handle = info.get("uploader_id")
    date = info.get("upload_date") or ""
    stats = [
        f"{fmt_count(info.get('view_count'))} views" if fmt_count(info.get("view_count")) else None,
        f"{fmt_count(info.get('like_count'))} likes" if fmt_count(info.get("like_count")) else None,
        f"{fmt_count(info.get('comment_count'))} comments" if fmt_count(info.get("comment_count")) else None,
    ]
    lines = [f"# {info.get('title') or info.get('id')}", ""]
    meta = [
        ("URL", url),
        ("By", f"{who} (@{handle.lstrip('@')})" if who and handle and handle != who else who),
        ("Published", f"{date[:4]}-{date[4:6]}-{date[6:]}" if len(date) == 8 else None),
        ("Duration", fmt_clock(dur, dur) if dur else None),
        ("Stats", ", ".join(s for s in stats if s) or None),
        ("Language", original_language(info)),
        ("Live", info.get("live_status") if info.get("live_status") not in (None, "not_live") else None),
        ("Most replayed", ", ".join(fmt_clock(t, dur) for t in most_replayed(info)) or None),
        ("Transcript", source),
    ]
    lines += [f"- {k}: {v}" for k, v in meta if v]

    if (desc := (info.get("description") or "").strip()):
        lines += ["", "## Description", "", desc]
    chapters = info.get("chapters") or []
    if chapters:
        lines += ["", "## Chapters", ""]
        lines += [f"- [{fmt_clock(c['start_time'], dur)}] {c.get('title', '')}" for c in chapters]
    if frames:
        lines += ["", "## Frames", ""]
        lines += [f"- [{fmt_clock(t, dur)}] frames/{p.name}" for t, p in frames]

    lines += ["", "## Transcript", ""]
    speakers = {s.speaker for s in segs if s.speaker}
    names = {sp: f"Speaker {i + 1}" for i, sp in enumerate(sorted(speakers, key=lambda x: str(x)))}
    for chapter, para in paragraphs(segs, chapters):
        if chapter is not None:
            lines += [f"### {chapter}", ""]
            continue
        who_said = f"{names[para.speaker]}: " if len(speakers) > 1 and para.speaker else ""
        lines += [f"[{fmt_clock(para.start, dur)}] {who_said}{para.text}", ""]
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------- main


def process(info: Info, base: list[str], out_root: Path, args: argparse.Namespace) -> int:
    local = Path(args.url).expanduser()
    if local.is_file():  # same folder name video-analysis uses, so both tools share one workspace
        dest = out_root / f"local-{re.sub(r'[^A-Za-z0-9_-]+', '-', local.stem)}"
    else:
        site = re.sub(r"[^a-z0-9]+", "", str(info.get("extractor_key") or info.get("extractor") or "video").lower())
        dest = out_root / f"{site}-{info['id']}"
    dest.mkdir(parents=True, exist_ok=True)
    info_path = dest / "info.json"
    info_path.write_text(json.dumps(info))

    segs: Optional[list[Segment]] = None
    source = ""
    track = None if args.asr_only else pick_track(info, args.lang)
    if track:
        key, is_auto = track
        path = download_captions(base, info_path, dest, key, is_auto)
        if path and (segs := parse_caption_file(path)):
            source = f"{'auto-generated' if is_auto else 'published'} captions ({key})"
            # X in particular ships captions that stop partway; prefer speech-to-text then.
            duration = float(info.get("duration") or 0)
            coverage = segs[-1].end / duration if duration > 60 else 1.0
            if coverage < 0.5:
                source += f", covering only the first {coverage:.0%}"
                if choose_engine(args.asr, args.lang or original_language(info)) != "none":
                    segs = None

    if not segs:
        lang = args.lang or original_language(info)
        engine = choose_engine(args.asr, lang)
        if engine == "none":
            print(f"NO TRANSCRIPT: {info.get('webpage_url')} has no usable captions and no speech-to-text engine is "
                  "available (set ELEVENLABS_API_KEY, or run on Apple Silicon with uv).", file=sys.stderr)
            return 2
        audio = download_audio(base, info_path, dest)
        try:
            segs = (transcribe_elevenlabs(audio, dest, lang) if engine == "elevenlabs"
                    else transcribe_local(engine, audio, dest, lang))
        finally:
            audio.unlink(missing_ok=True)
        label = {"elevenlabs": f"ElevenLabs {SCRIBE_MODEL}, diarized", "parakeet": "parakeet-tdt-0.6b-v3 (local)",
                 "whisper": f"{WHISPER_MODEL} (local)"}[engine]
        source = f"speech-to-text: {label}"

    frames = extract_frames(base, info, info_path, dest) if args.frames else []
    text = render(info, segs or [], source, frames)
    (dest / "transcript.md").write_text(text)
    words = sum(len(s.text.split()) for s in segs or [])
    print(f"{dest / 'transcript.md'}\n  {info.get('title')}\n  {source}; {words:,} words, ~{len(text) // 4:,} tokens"
          + (f"; {len(frames)} frames" if args.frames else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", help="video link, or a local video or audio file")
    ap.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "video-transcripts"),
                    help="parent directory for the per-video folder")
    ap.add_argument("--lang", help="caption language to prefer, e.g. en, es, pt-BR (allows YouTube auto-translation)")
    ap.add_argument("--asr", default="auto", choices=["auto", "elevenlabs", "parakeet", "whisper", "none"],
                    help="speech-to-text engine when captions are missing (default: auto)")
    ap.add_argument("--asr-only", action="store_true", help="skip captions and transcribe the audio")
    ap.add_argument("--frames", action="store_true", help="also save scene-change stills to frames/")
    ap.add_argument("--cookies-from-browser", metavar="BROWSER", help="e.g. chrome, firefox, safari")
    args = ap.parse_args()

    try:
        base = ytdlp_base(args.cookies_from_browser)
        local = Path(args.url).expanduser()
        if local.is_file():
            base += ["--enable-file-urls"]
        info = extract_info(base, local.resolve().as_uri() if local.is_file() else args.url)
        out_root = Path(args.out).expanduser()
        if info.get("_type") == "playlist":
            entries = [e for e in info.get("entries") or [] if e]
            if entries and all(e.get("formats") for e in entries):  # a post with several videos
                return max(process(e, base, out_root, args) for e in entries)
            print(f"PLAYLIST: {info.get('title')} ({len(entries)} entries). Run once per entry:", file=sys.stderr)
            for e in entries:
                print(f"{e.get('url') or e.get('webpage_url')}\t{e.get('title')}")
            return 3
        return process(info, base, out_root, args)
    except Failure as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

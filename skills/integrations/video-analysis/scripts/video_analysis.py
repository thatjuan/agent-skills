#!/usr/bin/env python3
"""See what a video shows: fetch it once, then pull exactly the frames a question needs.

Every command after `fetch` takes the workspace folder that `fetch` printed.
Timestamps are seconds (`75`, `75.5`) or clock time (`1:15`, `01:02:03.5`).

    fetch  SOURCE        link, local file, or direct media URL -> workspace with
                         the video (or a stream pointer) and summary.md
    probe  WS            technical summary: codecs, resolution, fps, rotation, HDR,
                         audio, embedded subtitles, chapters
    sheet  WS            contact sheet: many moments tiled in one image, each tile
                         stamped with its time
    frames WS            full-resolution stills at given times, at an interval
                         (bursts too), or at every scene cut; optional crop
    scenes WS            timestamps of every cut
    events WS            black, frozen, and silent stretches
    gemini WS            ask Gemini about the video itself (frames + audio)

Run `<command> -h` for its flags. Stdlib only; needs ffmpeg/ffprobe, and yt-dlp
(or uv to run it) for links. Exit codes: 0 ok, 1 error, 3 the link is a
playlist or channel (entries printed, one per line).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

Info = dict[str, Any]
TROUBLESHOOTING = "the video-transcript skill's references/troubleshooting.md"


class Failure(Exception):
    """A user-facing error; the message says what to try next."""


# ---------------------------------------------------------------- time


def parse_time(text: str) -> float:
    """`75`, `75.5`, `1:15`, `01:02:03.5` -> seconds."""
    parts = text.strip().split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        raise Failure(f"Not a timestamp: {text!r}. Use seconds (75.5) or clock time (1:15, 01:02:03).")
    secs = 0.0
    for n in nums:
        secs = secs * 60 + n
    return secs


def clock(seconds: float, precise: bool = False) -> str:
    """Seconds -> `MM:SS` (or `H:MM:SS`), with hundredths when `precise`."""
    whole = int(seconds)
    h, m, s = whole // 3600, whole % 3600 // 60, whole % 60
    out = f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
    if precise:
        out += f".{int(round((seconds - whole) * 100)) % 100:02d}"
    return out


def image_tokens(w: int, h: int) -> int:
    """What a model pays to see a w x h image: one token per 28x28 patch (Claude's
    vision rule; models with a lower cap downscale large images to fit)."""
    return math.ceil(w / 28) * math.ceil(h / 28)


def thin(items: list[float], limit: int) -> list[float]:
    """Keep at most `limit` items, evenly spread, first and last included."""
    if len(items) <= limit:
        return items
    if limit == 1:
        return items[:1]
    step = (len(items) - 1) / (limit - 1)
    return [items[round(i * step)] for i in range(limit)]


# ---------------------------------------------------------------- workspace


@dataclass
class Source:
    """What ffmpeg reads for a workspace: a local file, or a remote stream."""
    path: str
    headers: Optional[str] = None  # ffmpeg -headers value for streams

    def input_args(self) -> list[str]:
        return (["-headers", self.headers] if self.headers else []) + ["-i", self.path]


def open_workspace(ws: str) -> tuple[Path, Source]:
    root = Path(ws).expanduser()
    if root.is_file():  # a bare video file works too; outputs go beside it
        return root.parent / f"{root.stem}-analysis", Source(str(root))
    if not root.is_dir():
        raise Failure(f"{ws} is not a workspace. Run `fetch` first and pass the folder it prints.")
    videos = [p for p in root.glob("video.*") if p.suffix not in (".part", ".ytdl", ".json")]
    if videos:
        return root, Source(str(videos[0].resolve()))
    stream = root / "stream.json"
    if stream.exists():
        data = json.loads(stream.read_text())
        return root, Source(data["url"], data.get("headers"))
    raise Failure(f"{ws} has no video.* or stream.json. Rerun `fetch`.")


def duration_of(root: Path, src: Source) -> float:
    cached = root / "probe.json"
    data = json.loads(cached.read_text()) if cached.exists() else ffprobe(src)
    return float(data.get("format", {}).get("duration") or 0)


# ---------------------------------------------------------------- ffmpeg


def run(cmd: list[str], what: str) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-4:])
        hint = " A 403 on a stream usually means its URL expired: rerun `fetch --stream`." if "403" in tail else ""
        raise Failure(f"{what} failed:\n{tail}{hint}")
    return proc


def ffprobe(src: Source) -> Info:
    cmd = ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", "-show_chapters"]
    if src.headers:
        cmd += ["-headers", src.headers]
    data: Info = json.loads(run(cmd + [src.path], "ffprobe").stdout)
    return data


def grab(src: Source, t: float, out: Path, vf: Optional[str] = None, raw_size: Optional[tuple[int, int]] = None) -> Optional[bytes]:
    """One frame at time t. Input-side -ss is fast and frame-accurate when
    decoding. Writes a JPEG to `out`, or returns raw RGB when `raw_size` is set."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}"] + src.input_args()
    cmd += ["-frames:v", "1", "-an", "-sn"]
    filters = [vf] if vf else []
    if raw_size:
        w, h = raw_size
        filters.append(f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x202020")
        cmd += ["-vf", ",".join(filters), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        proc = subprocess.run(cmd, capture_output=True)
        return proc.stdout if len(proc.stdout) == w * h * 3 else None
    if filters:
        cmd += ["-vf", ",".join(filters)]
    subprocess.run(cmd + ["-q:v", "2", "-y", str(out)], capture_output=True)
    return None


def scene_cuts(src: Source, threshold: float, start: float, end: Optional[float]) -> list[float]:
    """Times where the picture changes by more than `threshold` (0-1). Decodes
    the whole range, downscaled, so it takes a while on long videos."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{start:.3f}"]
    if end is not None:
        cmd += ["-to", f"{end:.3f}"]
    cmd += src.input_args() + ["-an", "-sn", "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo",
                               "-fps_mode", "vfr", "-f", "null", "-"]
    proc = run(cmd, "scene detection")
    # With input-side -ss, output timestamps restart at zero.
    return [start + float(t) for t in re.findall(r"pts_time:([\d.]+)", proc.stderr)]


# ---------------------------------------------------------------- yt-dlp


def ytdlp_base(cookies_from_browser: Optional[str]) -> list[str]:
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


def ytdlp(base: list[str], args: list[str]) -> str:
    proc = subprocess.run(base + args, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-4:]) or f"exit {proc.returncode}"
        raise Failure(f"yt-dlp failed:\n{tail}\nSee {TROUBLESHOOTING} for bot checks, rate limits, and login-only posts.")
    return proc.stdout


def most_replayed(info: Info, top: int = 3) -> list[float]:
    """Peaks of YouTube's 'most replayed' heatmap, at least a minute apart."""
    picks: list[float] = []
    for h in sorted(info.get("heatmap") or [], key=lambda h: -h.get("value", 0)):
        if all(abs(h["start_time"] - p) >= 60 for p in picks):
            picks.append(h["start_time"])
        if len(picks) == top:
            break
    return sorted(picks)


# ---------------------------------------------------------------- fetch / probe


def describe(probe: Info, info: Optional[Info], streamed: bool = False) -> str:
    """summary.md: what the video is (from the site) and what the file is (from ffprobe)."""
    fmt = probe.get("format", {})
    streams = probe.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")), None)
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    subs = [s for s in streams if s.get("codec_type") == "subtitle"]
    dur = float(fmt.get("duration") or (info or {}).get("duration") or 0)
    lines: list[str] = []

    if info:
        date = str(info.get("upload_date") or "")
        lines += [f"# {info.get('title') or info.get('id')}", ""]
        meta = [
            ("URL", info.get("webpage_url")),
            ("By", info.get("channel") or info.get("uploader")),
            ("Published", f"{date[:4]}-{date[4:6]}-{date[6:]}" if len(date) == 8 else None),
            ("Views", f"{info['view_count']:,}" if isinstance(info.get("view_count"), int) else None),
            ("Most replayed", ", ".join(clock(t) for t in most_replayed(info)) or None),
        ]
        lines += [f"- {k}: {v}" for k, v in meta if v]
    else:
        lines += [f"# {Path(str(fmt.get('filename', 'video'))).name}", ""]

    lines += ["", "## File", "", f"- Duration: {clock(dur, precise=True)} ({dur:.2f} s)"]
    if fmt.get("size"):
        lines.append(f"- Size: {int(fmt['size']) / 1e6:.1f} MB, {int(fmt.get('bit_rate') or 0) // 1000} kb/s")
    if video:
        w, h = int(video.get("width", 0)), int(video.get("height", 0))
        rotation = next((int(sd.get("rotation", 0)) for sd in video.get("side_data_list", []) if "rotation" in sd), 0)
        if rotation in (90, -90, 270, -270):
            w, h = h, w
        avg, real = video.get("avg_frame_rate", "0/1"), video.get("r_frame_rate", "0/1")
        num, _, den = avg.partition("/")
        fps = float(num) / float(den) if den and float(den) else 0.0
        vfr = avg != real and fps > 0
        hdr = video.get("color_transfer") in ("smpte2084", "arib-std-b67")
        lines.append(f"- Video: {video.get('codec_name')} {w}x{h}, {fps:.3g} fps"
                     + (" (variable frame rate)" if vfr else "")
                     + (f", rotated {rotation}°" if rotation else "")
                     + (f", HDR ({video.get('color_transfer')})" if hdr else "")
                     + (f", {video['nb_frames']} frames" if video.get("nb_frames") else ""))
    else:
        lines.append("- Video: none (audio only)")
    for a in audio:
        lang = (a.get("tags", {}).get("language") or "").replace("und", "")
        lines.append(f"- Audio: {a.get('codec_name')}, {a.get('channels')} ch, {a.get('sample_rate')} Hz" + (f", {lang}" if lang else ""))
    if not audio:
        lines.append("- Audio: not fetched (a stream reads the picture only)" if streamed else "- Audio: none")
    for s in subs:
        lang = s.get("tags", {}).get("language") or "?"
        lines.append(f"- Embedded subtitles: stream {s.get('index')} ({s.get('codec_name')}, {lang})")

    chapters = (info or {}).get("chapters") or [
        {"start_time": float(c["start_time"]), "title": c.get("tags", {}).get("title", "")} for c in probe.get("chapters", [])
    ]
    if chapters:
        lines += ["", "## Chapters", ""] + [f"- [{clock(float(c['start_time']))}] {c.get('title', '')}" for c in chapters]
    if info and (desc := (info.get("description") or "").strip()):
        lines += ["", "## Description", "", desc[:2000] + (" …" if len(desc) > 2000 else "")]
    return "\n".join(lines).rstrip() + "\n"


def cmd_fetch(args: argparse.Namespace) -> int:
    out_root = Path(args.out).expanduser()
    local = Path(args.source).expanduser()
    info: Optional[Info] = None

    if local.is_file():
        root = out_root / f"local-{re.sub(r'[^A-Za-z0-9_-]+', '-', local.stem)}"
        root.mkdir(parents=True, exist_ok=True)
        link = root / f"video{local.suffix.lower()}"
        if not link.exists():
            link.symlink_to(local.resolve())
    elif re.search(r"\.(mp4|m4v|mov|webm|mkv|m3u8|mpd)(\?|$)", args.source) and not args.ytdlp:
        # Direct media URL: ffmpeg reads it as-is, seeking with range requests.
        root = out_root / f"url-{abs(hash(args.source)) % 10**8}"
        root.mkdir(parents=True, exist_ok=True)
        (root / "stream.json").write_text(json.dumps({"url": args.source}))
    else:
        base = ytdlp_base(args.cookies_from_browser)
        info = json.loads(ytdlp(base, ["-J", "--flat-playlist", "--no-playlist", args.source]))
        assert info is not None
        if info.get("_type") == "playlist":
            entries = [e for e in info.get("entries") or [] if e]
            print(f"PLAYLIST: {info.get('title')} ({len(entries)} entries). Run once per entry:", file=sys.stderr)
            for e in entries:
                print(f"{e.get('url') or e.get('webpage_url')}\t{e.get('title')}")
            return 3
        site = re.sub(r"[^a-z0-9]+", "", str(info.get("extractor_key") or "video").lower())
        root = out_root / f"{site}-{info['id']}"
        root.mkdir(parents=True, exist_ok=True)
        info_path = root / "info.json"
        info_path.write_text(json.dumps(info))
        h = args.height
        if args.stream:
            chosen: Info = json.loads(ytdlp(base, ["--load-info-json", str(info_path), "-J",
                                                    "-f", f"bv*[height<={h}][protocol^=http]/bv*[height<={h}]/b[height<={h}]/b"]))
            fmt = (chosen.get("requested_formats") or [chosen])[0]
            headers = "".join(f"{k}: {v}\r\n" for k, v in (fmt.get("http_headers") or {}).items())
            (root / "stream.json").write_text(json.dumps({"url": fmt["url"], "headers": headers, "fetched": time.time()}))
            for old in root.glob("video.*"):
                old.unlink()
        else:
            ytdlp(base, ["--load-info-json", str(info_path), "-f", f"bv*[height<={h}]+ba/b[height<={h}]/bv*+ba/b",
                         "--merge-output-format", "mp4", "-o", str(root / "video.%(ext)s")])
            (root / "stream.json").unlink(missing_ok=True)

    root, src = open_workspace(str(root))
    probe = ffprobe(src)
    (root / "probe.json").write_text(json.dumps(probe))
    streamed = src.path.startswith(("http:", "https:"))
    summary = describe(probe, info, streamed)
    (root / "summary.md").write_text(summary)
    mode = "stream (nothing downloaded; frames are read over the network)" if streamed else src.path
    print(f"{root}\n  source: {mode}\n  summary: {root / 'summary.md'}")
    head = summary.split("\n## Description")[0]
    print("\n".join("  " + ln for ln in head.splitlines() if ln.startswith("- ")))
    return 0


def cmd_probe(args: argparse.Namespace) -> int:
    root, src = open_workspace(args.ws)
    root.mkdir(parents=True, exist_ok=True)
    probe = ffprobe(src)
    (root / "probe.json").write_text(json.dumps(probe))
    info_path = root / "info.json"
    info = json.loads(info_path.read_text()) if info_path.exists() else None
    print(describe(probe, info, src.path.startswith(("http:", "https:"))))
    return 0


# ---------------------------------------------------------------- timestamps


def pick_times(args: argparse.Namespace, root: Path, src: Source, default_count: Optional[int]) -> list[float]:
    """Resolve --at / --every / --scenes / --count within [--from, --to]."""
    dur = duration_of(root, src)
    start = parse_time(args.start) if args.start else 0.0
    end = min(parse_time(args.end), dur) if args.end else dur
    if end <= start:
        raise Failure(f"Empty range {clock(start)}-{clock(end)} (video is {clock(dur)}).")
    if args.at:
        times = [parse_time(t) for t in re.split(r"[,\s]+", args.at.strip()) if t]
    elif args.every:
        step = parse_time(args.every)
        times = [start + i * step for i in range(int((end - start) / step) + 1)]
    elif args.scenes:
        cuts = scene_cuts(src, args.threshold, start, end)
        times = [start] + [c + 0.1 for c in cuts]  # just past the cut, clear of transition blur
    else:
        count = args.count or default_count
        if not count:
            raise Failure("Say which frames: --at, --every, or --scenes.")
        times = [start + (i + 0.5) * (end - start) / count for i in range(count)]
    late = [t for t in times if t > dur]
    if late:
        print(f"Skipped {len(late)} timestamp(s) past the end ({clock(dur, True)}): "
              + ", ".join(clock(t, True) for t in late), file=sys.stderr)
    last = max(dur - 0.05, 0)
    kept = [t for t in times if t <= dur]
    if not kept:
        raise Failure(f"No timestamps inside the video (it is {clock(dur, True)} long).")
    return thin(sorted({round(min(max(t, 0), last), 3) for t in kept}), args.max)


def add_time_flags(p: argparse.ArgumentParser, max_default: int) -> None:
    p.add_argument("ws", help="workspace folder from `fetch` (or a video file)")
    p.add_argument("--at", help="comma-separated timestamps: 12,1:05,02:30.5")
    p.add_argument("--every", help="one frame every N seconds (0.25 for a burst)")
    p.add_argument("--scenes", action="store_true", help="one frame per detected shot")
    p.add_argument("--threshold", type=float, default=0.3, help="scene-change sensitivity, 0-1 (default 0.3; 0.1 for screen recordings)")
    p.add_argument("--from", dest="start", help="range start")
    p.add_argument("--to", dest="end", help="range end")
    p.add_argument("--max", type=int, default=max_default, help=f"cap, thinned evenly (default {max_default})")
    p.add_argument("--out", help="output folder (default: inside the workspace)")


# ---------------------------------------------------------------- frames


def cmd_frames(args: argparse.Namespace) -> int:
    root, src = open_workspace(args.ws)
    times = pick_times(args, root, src, None)
    out = Path(args.out or root / "frames").expanduser()
    out.mkdir(parents=True, exist_ok=True)
    filters = []
    if args.crop:
        filters.append(f"crop={args.crop.replace(',', ':')}")
    if args.width:
        filters.append(f"scale='min({args.width},iw)':-2")
    vf = ",".join(filters) or None
    precise = any(t % 1 for t in times)
    suffix = "-crop" if args.crop else ""

    def one(t: float) -> tuple[float, Path]:
        path = out / f"t{t:09.3f}{suffix}.jpg"
        grab(src, t, path, vf)
        return t, path

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(one, times))
    made = [(t, p) for t, p in results if p.exists()]
    for t, p in made:
        print(f"[{clock(t, precise)}] {p}")
    if made:
        size = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                               str(made[0][1])], capture_output=True, text=True).stdout.strip().split(",")
        if len(size) == 2:
            w, h = int(size[0]), int(size[1])
            print(f"{w}x{h} each, ~{image_tokens(w, h):,} tokens per frame to view")
    if len(made) < len(times):
        print(f"{len(times) - len(made)} timestamp(s) produced no frame (past the end, or the stream refused).", file=sys.stderr)
    return 0 if made else 1


# ---------------------------------------------------------------- contact sheets

# 5x7 bitmap glyphs, so sheets carry timestamps on any ffmpeg build (many lack drawtext).
GLYPHS = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
}


def stamp(canvas: bytearray, width: int, x0: int, y0: int, text: str, scale: int) -> None:
    """Draw `text` white on a black box at (x0, y0) of an RGB canvas."""
    pad = scale
    box_w = len(text) * 6 * scale + pad * 2 - scale
    box_h = 7 * scale + pad * 2
    for y in range(y0, y0 + box_h):
        row = (y * width + x0) * 3
        canvas[row:row + box_w * 3] = b"\x00" * (box_w * 3)
    for i, ch in enumerate(text):
        for gy, bits in enumerate(GLYPHS.get(ch, GLYPHS["."])):
            for gx, bit in enumerate(bits):
                if bit == "1":
                    px = x0 + pad + (i * 6 + gx) * scale
                    for dy in range(scale):
                        row = ((y0 + pad + gy * scale + dy) * width + px) * 3
                        canvas[row:row + scale * 3] = b"\xff" * (scale * 3)


def cmd_sheet(args: argparse.Namespace) -> int:
    root, src = open_workspace(args.ws)
    probe = json.loads((root / "probe.json").read_text()) if (root / "probe.json").exists() else ffprobe(src)
    video = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), None)
    if not video:
        raise Failure("No video stream to sheet.")
    vw, vh = int(video["width"]), int(video["height"])
    if any(abs(int(sd.get("rotation", 0))) in (90, 270) for sd in video.get("side_data_list", [])):
        vw, vh = vh, vw
    aspect = vw / vh if vh else 16 / 9
    cols = args.cols or (4 if aspect >= 1.2 else 5 if aspect >= 0.8 else 6)
    gap = 4
    tile_w = (args.width - gap * (cols + 1)) // cols // 2 * 2
    tile_h = int(tile_w / aspect) // 2 * 2
    rows_per_sheet = max(1, (args.width - gap) // (tile_h + gap))  # keep each sheet no taller than wide
    times = pick_times(args, root, src, cols * min(rows_per_sheet, 4))

    with ThreadPoolExecutor(max_workers=6) as pool:
        tiles = list(pool.map(lambda t: grab(src, t, Path(), raw_size=(tile_w, tile_h)), times))
    if not any(tiles):
        raise Failure("No frames could be read. Check the workspace with `probe`.")

    out = Path(args.out or root / "sheets").expanduser()
    out.mkdir(parents=True, exist_ok=True)
    precise = any(t % 1 for t in times)
    scale = max(2, tile_w // 120)
    per_sheet = cols * rows_per_sheet
    first_tag = f"{times[0]:08.2f}"
    for n in range(math.ceil(len(times) / per_sheet)):
        chunk = list(zip(times, tiles))[n * per_sheet:(n + 1) * per_sheet]
        rows = math.ceil(len(chunk) / cols)
        sw, sh = gap + cols * (tile_w + gap), gap + rows * (tile_h + gap)
        canvas = bytearray(b"\x20" * (sw * sh * 3))
        for i, (t, tile) in enumerate(chunk):
            x, y = gap + (i % cols) * (tile_w + gap), gap + (i // cols) * (tile_h + gap)
            if tile:
                for r in range(tile_h):
                    dst = ((y + r) * sw + x) * 3
                    canvas[dst:dst + tile_w * 3] = tile[r * tile_w * 3:(r + 1) * tile_w * 3]
            stamp(canvas, sw, x, y, clock(t, precise), scale)
        path = out / f"sheet-{first_tag}-{n + 1:02d}.jpg"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                        "-s", f"{sw}x{sh}", "-i", "-", "-frames:v", "1", "-q:v", "3", "-y", str(path)],
                       input=bytes(canvas), check=True)
        span = f"{clock(chunk[0][0], precise)}-{clock(chunk[-1][0], precise)}"
        print(f"{path}  ({len(chunk)} tiles, {span}, {sw}x{sh}, ~{image_tokens(sw, sh):,} tokens)")
    gaps = [b - a for a, b in zip(times, times[1:])]
    if gaps:
        print(f"Spacing {min(gaps):.2f} s" + (f" to {max(gaps):.2f} s" if max(gaps) - min(gaps) > 0.01 else "")
              + f"; tiles {tile_w}x{tile_h}")
    missing = sum(1 for t in tiles if not t)
    if missing:
        print(f"{missing} tile(s) left blank: no frame at that time.", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- scenes / events


def cmd_scenes(args: argparse.Namespace) -> int:
    root, src = open_workspace(args.ws)
    start = parse_time(args.start) if args.start else 0.0
    end = parse_time(args.end) if args.end else None
    cuts = scene_cuts(src, args.threshold, start, end)
    dur = end or duration_of(root, src)
    bounds = [start] + cuts + [dur]
    shots = [(a, b) for a, b in zip(bounds, bounds[1:]) if b > a]
    lines = [f"{clock(a, True)}  shot {i + 1}, {b - a:.2f} s" for i, (a, b) in enumerate(shots)]
    root.mkdir(parents=True, exist_ok=True)
    (root / "scenes.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    lengths = [b - a for a, b in shots]
    if lengths:
        print(f"{len(cuts)} cuts, {len(shots)} shots, average {sum(lengths) / len(lengths):.2f} s, "
              f"shortest {min(lengths):.2f} s, longest {max(lengths):.2f} s (threshold {args.threshold}). Saved to {root / 'scenes.txt'}")
    return 0


def cmd_events(args: argparse.Namespace) -> int:
    root, src = open_workspace(args.ws)
    has_audio = any(s.get("codec_type") == "audio" for s in ffprobe(src).get("streams", []))
    cmd = ["ffmpeg", "-hide_banner", "-nostats"] + src.input_args() + [
        "-vf", f"blackdetect=d={args.min}:pix_th=0.10,freezedetect=n=-60dB:d={max(args.min, 1.0)}"]
    cmd += ["-af", f"silencedetect=n=-50dB:d={max(args.min, 1.0)}"] if has_audio else ["-an"]
    log = run(cmd + ["-f", "null", "-"], "event detection").stderr
    events: list[tuple[float, str]] = []
    for s, e, d in re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", log):
        events.append((float(s), f"black   {clock(float(s), True)}-{clock(float(e), True)} ({float(d):.2f} s)"))
    for kind, pattern in (("frozen", r"freeze_(start|end): ([\d.]+)"), ("silent", r"silence_(start|end): ([\d.]+)")):
        opened: Optional[float] = None
        for edge, t in re.findall(pattern, log):
            if edge == "start":
                opened = float(t)
            elif opened is not None:
                events.append((opened, f"{kind:<7} {clock(opened, True)}-{clock(float(t), True)} ({float(t) - opened:.2f} s)"))
                opened = None
        if opened is not None:
            events.append((opened, f"{kind:<7} {clock(opened, True)}-end"))
    print("\n".join(line for _, line in sorted(events)) or "No black, frozen, or silent stretches found.")
    return 0


# ---------------------------------------------------------------- gemini

GEMINI = "https://generativelanguage.googleapis.com"


def gemini_call(url: str, key: str, body: Optional[bytes] = None, headers: Optional[dict[str, str]] = None,
                method: str = "GET") -> tuple[Info, Any]:
    req = urllib.request.Request(url, data=body, method=method, headers={"x-goog-api-key": key, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            raw = resp.read().decode()
            return (json.loads(raw) if raw else {}), resp.headers
    except urllib.error.HTTPError as e:
        raise Failure(f"Gemini HTTP {e.code}: {e.read().decode(errors='replace')[:400]}")


def gemini_file(root: Path, src: Source, key: str) -> tuple[str, str]:
    """Upload the workspace video to the Files API once; reuse it for 47 hours."""
    cache = root / "gemini-file.json"
    if cache.exists():
        data = json.loads(cache.read_text())
        if time.time() - data["uploaded"] < 47 * 3600:
            return data["uri"], data["mime"]
    path = Path(src.path)
    if not path.is_file():
        raise Failure("Gemini needs the video file for non-YouTube sources. Rerun `fetch` without --stream.")
    mime = {".mov": "video/quicktime", ".webm": "video/webm", ".mkv": "video/x-matroska"}.get(path.suffix.lower(), "video/mp4")
    size = path.stat().st_size
    _, head = gemini_call(f"{GEMINI}/upload/v1beta/files", key, json.dumps({"file": {"display_name": path.name}}).encode(), {
        "X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
        "X-Goog-Upload-Header-Content-Length": str(size), "X-Goog-Upload-Header-Content-Type": mime,
        "Content-Type": "application/json"}, "POST")
    uploaded, _ = gemini_call(head["x-goog-upload-url"], key, path.read_bytes(), {
        "X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize"}, "POST")
    file = uploaded["file"]
    while file.get("state") == "PROCESSING":
        time.sleep(5)
        file, _ = gemini_call(f"{GEMINI}/v1beta/{file['name']}", key)
    if file.get("state") != "ACTIVE":
        raise Failure(f"Gemini could not process the upload: {file.get('state')} {file.get('error', '')}")
    cache.write_text(json.dumps({"uri": file["uri"], "mime": mime, "uploaded": time.time()}))
    return file["uri"], mime


def cmd_gemini(args: argparse.Namespace) -> int:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise Failure("GEMINI_API_KEY is not set.")
    root, src = open_workspace(args.ws)
    info_path = root / "info.json"
    page = json.loads(info_path.read_text()).get("webpage_url", "") if info_path.exists() else ""
    if re.search(r"(youtube\.com|youtu\.be)/", page):
        uri, mime = page, "video/mp4"  # Google fetches YouTube itself; nothing to upload
    else:
        uri, mime = gemini_file(root, src, key)
    meta: Info = {}
    if args.start:
        meta["start_offset"] = f"{parse_time(args.start):.1f}s"
    if args.end:
        meta["end_offset"] = f"{parse_time(args.end):.1f}s"
    if args.fps:
        meta["fps"] = args.fps
    video_part: Info = {"file_data": {"file_uri": uri, "mime_type": mime}}
    if meta:
        video_part["video_metadata"] = meta
    body = {
        "contents": [{"parts": [video_part, {"text": args.prompt}]}],
        "generationConfig": {"mediaResolution": "MEDIA_RESOLUTION_HIGH" if args.high_res else "MEDIA_RESOLUTION_LOW"},
    }
    resp, _ = gemini_call(f"{GEMINI}/v1beta/models/{args.model}:generateContent", key, json.dumps(body).encode(),
                          {"Content-Type": "application/json"}, "POST")
    try:
        text = "".join(p.get("text", "") for p in resp["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        raise Failure(f"Gemini returned no answer: {json.dumps(resp)[:400]}")
    n = len(list(root.glob("gemini-answer-*.md"))) + 1
    path = root / f"gemini-answer-{n}.md"
    path.write_text(f"Prompt: {args.prompt}\nModel: {args.model}\nRange: {meta or 'whole video'}\n\n{text}\n")
    usage = resp.get("usageMetadata", {})
    print(f"{text}\n\n(saved to {path}; {usage.get('promptTokenCount', '?')} input tokens)")
    return 0


# ---------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("fetch", help="get the video into a workspace")
    p.add_argument("source", help="video link, local file, or direct media URL")
    p.add_argument("--out", default=os.path.join(tempfile.gettempdir(), "videos"), help="parent folder for workspaces")
    p.add_argument("--height", type=int, default=720, help="max download height (default 720; 1080+ for small text)")
    p.add_argument("--stream", action="store_true", help="skip the download; read frames from the remote stream")
    p.add_argument("--ytdlp", action="store_true", help="resolve a .mp4/.m3u8 URL with yt-dlp instead of reading it directly")
    p.add_argument("--cookies-from-browser", metavar="BROWSER", help="chrome, firefox, safari: for login-only videos")
    p.set_defaults(run=cmd_fetch)

    p = sub.add_parser("probe", help="technical summary of the video")
    p.add_argument("ws")
    p.set_defaults(run=cmd_probe)

    p = sub.add_parser("sheet", help="contact sheet of many moments, time-stamped")
    add_time_flags(p, 64)
    p.add_argument("--count", type=int, help="evenly spaced tiles over the range (default: one sheet's worth)")
    p.add_argument("--cols", type=int, help="tiles per row (default 4 landscape, 5 square, 6 portrait)")
    p.add_argument("--width", type=int, default=1568, help="sheet width in px (default 1568)")
    p.set_defaults(run=cmd_sheet)

    p = sub.add_parser("frames", help="full-resolution stills")
    add_time_flags(p, 40)
    p.set_defaults(count=None)
    p.add_argument("--crop", help="w:h:x:y in source pixels, to zoom on a region")
    p.add_argument("--width", type=int, help="downscale to at most this width")
    p.set_defaults(run=cmd_frames)

    p = sub.add_parser("scenes", help="list every cut")
    p.add_argument("ws")
    p.add_argument("--threshold", type=float, default=0.3, help="0-1 (default 0.3; 0.1 for screen recordings)")
    p.add_argument("--from", dest="start")
    p.add_argument("--to", dest="end")
    p.set_defaults(run=cmd_scenes)

    p = sub.add_parser("events", help="black, frozen, and silent stretches")
    p.add_argument("ws")
    p.add_argument("--min", type=float, default=0.5, help="shortest stretch to report, seconds (default 0.5)")
    p.set_defaults(run=cmd_events)

    p = sub.add_parser("gemini", help="ask Gemini about the video itself")
    p.add_argument("ws")
    p.add_argument("--prompt", required=True)
    p.add_argument("--from", dest="start", help="clip start")
    p.add_argument("--to", dest="end", help="clip end")
    p.add_argument("--fps", type=float, help="frames per second Gemini samples (default 1; raise for fast action)")
    p.add_argument("--high-res", action="store_true", help="~300 tokens/s instead of ~100; for small on-screen text")
    p.add_argument("--model", default="gemini-flash-latest", help="gemini-pro-latest for hard visual reasoning")
    p.set_defaults(run=cmd_gemini)

    args = ap.parse_args()
    try:
        code: int = args.run(args)
        return code
    except Failure as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

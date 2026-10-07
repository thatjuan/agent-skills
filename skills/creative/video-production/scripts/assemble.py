#!/usr/bin/env python3
"""Render an edit decision list (edit.json) to a finished video with ffmpeg. Stdlib only.

Usage:
  assemble.py edit.json              Render to the edit's "output".
  assemble.py edit.json --timeline   Print each clip's timeline start/end and the runtime; render nothing.
  assemble.py edit.json --dry-run    Print the ffmpeg command and filter graph; render nothing.

Paths inside edit.json resolve relative to edit.json. Schema (all times in seconds):

{
  "output": "final.mp4",
  "size": "1920x1080", "fps": 24,
  "loudness": -14,                       # integrated LUFS target for the final mix
  "duck": true,                          # compress the music bus under the voice bus
  "clips": [                             # picture track, in order
    {"id": "s01", "src": "clips/s01.mp4", "in": 0.4, "out": 3.4,
     "transition": "cut",                # how this clip hands off to the next: "cut" (default)
                                         # or {"type": "dissolve"|"dip"|<any xfade name>, "duration": 0.5}
     "keep_audio": false, "gain_db": 0}, # keep_audio mixes the clip's own audio (role "clip")
    {"id": "end", "src": "stills/endcard.png", "duration": 3}   # a still holds for "duration"
  ],
  "audio": [
    {"src": "audio/vo/l01.mp3", "role": "voice", "at": "s03+0.25"},  # voice | music | sfx | ambience
    {"src": "audio/music/score.mp3", "role": "music", "at": 0, "gain_db": -4,
     "in": 0, "out": 30, "fade_in": 0.5, "fade_out": 2}
  ],
  "overlays": [                          # PNGs with alpha: supers, lower thirds, logos, captions
    {"src": "gfx/tagline.png", "at": "end+0.3", "duration": 2.5, "x": "(W-w)/2", "y": "H*0.72", "fade": 0.3}
  ]
}

"at" is either a number (absolute timeline seconds) or "<clip id>" / "<clip id>+<offset>" /
"<clip id>-<offset>", anchored to that clip's timeline start, so audio stays synced when trims change.
"""
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
TRANSITION_ALIASES = {"dissolve": "fade", "dip": "fadeblack"}


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", path],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        die(f"ffprobe failed on {path}: {out.stderr.strip()}")
    info = json.loads(out.stdout)
    return {
        "duration": float(info.get("format", {}).get("duration", 0) or 0),
        "has_audio": any(s.get("codec_type") == "audio" for s in info.get("streams", [])),
    }


def transition_of(clip):
    t = clip.get("transition", "cut")
    if t == "cut" or t is None:
        return None
    if isinstance(t, str):
        t = {"type": t, "duration": 0.5}
    return {"type": TRANSITION_ALIASES.get(t["type"], t["type"]), "duration": float(t.get("duration", 0.5))}


def build_timeline(clips, base):
    """Return clips annotated with resolved path, duration, and timeline start."""
    timeline, t = [], 0.0
    for i, c in enumerate(clips):
        src = os.path.join(base, c["src"])
        if not os.path.isfile(src):
            die(f"Missing clip source: {src}")
        is_image = os.path.splitext(src)[1].lower() in IMAGE_EXT
        if is_image:
            if "duration" not in c:
                die(f"Still {c['src']} needs a duration")
            dur, has_audio = float(c["duration"]), False
            cin = 0.0
        else:
            meta = probe(src)
            cin = float(c.get("in", 0))
            cout = float(c.get("out", meta["duration"]))
            dur, has_audio = cout - cin, meta["has_audio"]
            if dur <= 0:
                die(f"Clip {c.get('id', i)} has a non-positive duration ({cin}–{cout})")
        trans = transition_of(c) if i < len(clips) - 1 else None
        timeline.append({**c, "id": c.get("id", f"c{i}"), "path": src, "image": is_image, "in": cin,
                         "dur": dur, "start": t, "trans": trans, "has_audio": has_audio})
        t += dur - (trans["duration"] if trans else 0)
    runtime = timeline[-1]["start"] + timeline[-1]["dur"] if timeline else 0
    return timeline, runtime


def resolve_at(at, starts):
    if isinstance(at, (int, float)):
        return float(at)
    m = re.fullmatch(r"\s*([A-Za-z0-9_.-]+?)\s*(?:([+-])\s*([0-9.]+))?\s*", str(at))
    if not m or m.group(1) not in starts:
        die(f"Cannot resolve 'at': {at!r} (known clip ids: {', '.join(starts)})")
    offset = float(m.group(3) or 0) * (-1 if m.group(2) == "-" else 1)
    return starts[m.group(1)] + offset


def build(edit, base):
    w, h = (int(x) for x in edit.get("size", "1920x1080").lower().split("x"))
    fps = edit.get("fps", 24)
    timeline, runtime = build_timeline(edit["clips"], base)
    starts = {c["id"]: c["start"] for c in timeline}

    inputs, graph = [], []

    def add_input(args):
        inputs.extend(args)
        return sum(1 for a in inputs if a == "-i") - 1

    # Picture: normalize every clip to one size/fps/timebase, then chain cuts and xfades.
    for i, c in enumerate(timeline):
        if c["image"]:
            idx = add_input(["-loop", "1", "-t", f"{c['dur']:.3f}", "-i", c["path"]])
        else:
            idx = add_input(["-ss", f"{c['in']:.3f}", "-t", f"{c['dur']:.3f}", "-i", c["path"]])
        c["input"] = idx
        graph.append(
            f"[{idx}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,"
            f"fps={fps},format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{i}]"
        )
    acc = "v0"
    pending_cuts = ["v0"]
    for i in range(1, len(timeline)):
        prev = timeline[i - 1]
        if prev["trans"]:
            if len(pending_cuts) > 1:
                graph.append(f"{''.join(f'[{p}]' for p in pending_cuts)}concat=n={len(pending_cuts)}:v=1:a=0[vc{i}]")
                acc = f"vc{i}"
            else:
                acc = pending_cuts[0]
            graph.append(
                f"[{acc}][v{i}]xfade=transition={prev['trans']['type']}:"
                f"duration={prev['trans']['duration']:.3f}:offset={timeline[i]['start']:.3f}[vx{i}]"
            )
            pending_cuts = [f"vx{i}"]
        else:
            pending_cuts.append(f"v{i}")
    if len(pending_cuts) > 1:
        graph.append(f"{''.join(f'[{p}]' for p in pending_cuts)}concat=n={len(pending_cuts)}:v=1:a=0[vcat]")
        vout = "vcat"
    else:
        vout = pending_cuts[0]

    # Overlays: PNGs composited over the cut, each with an optional alpha fade.
    for k, o in enumerate(edit.get("overlays", [])):
        path = os.path.join(base, o["src"])
        if not os.path.isfile(path):
            die(f"Missing overlay: {path}")
        a = resolve_at(o.get("at", 0), starts)
        d = float(o["duration"])
        f = float(o.get("fade", 0))
        idx = add_input(["-loop", "1", "-t", f"{d:.3f}", "-i", path])
        chain = f"[{idx}:v]format=rgba,setpts=PTS-STARTPTS+{a:.3f}/TB"
        if f > 0:
            chain += f",fade=in:st={a:.3f}:d={f:.3f}:alpha=1,fade=out:st={a + d - f:.3f}:d={f:.3f}:alpha=1"
        graph.append(chain + f"[ov{k}]")
        graph.append(
            f"[{vout}][ov{k}]overlay=x={o.get('x', '(W-w)/2')}:y={o.get('y', '(H-h)/2')}:"
            f"enable='between(t,{a:.3f},{a + d:.3f})':eof_action=pass[vo{k}]"
        )
        vout = f"vo{k}"
    graph.append(f"[{vout}]trim=duration={runtime:.3f},setpts=PTS-STARTPTS[vfinal]")

    # Sound: place every track on the timeline, bus by role, duck music under voice, normalize.
    tracks = []
    for c in timeline:
        if c.get("keep_audio") and c["has_audio"]:
            tracks.append({"label_src": f"{c['input']}:a", "role": "clip", "start": c["start"],
                           "dur": c["dur"], "gain_db": c.get("gain_db", 0), "fade_in": 0, "fade_out": 0})
    for t in edit.get("audio", []):
        path = os.path.join(base, t["src"])
        if not os.path.isfile(path):
            die(f"Missing audio: {path}")
        tin = float(t.get("in", 0))
        tout = float(t["out"]) if "out" in t else probe(path)["duration"]
        idx = add_input(["-ss", f"{tin:.3f}", "-t", f"{tout - tin:.3f}", "-i", path])
        tracks.append({"label_src": f"{idx}:a", "role": t.get("role", "sfx"),
                       "start": resolve_at(t.get("at", 0), starts), "dur": tout - tin,
                       "gain_db": t.get("gain_db", 0), "fade_in": t.get("fade_in", 0),
                       "fade_out": t.get("fade_out", 0)})

    buses = {"voice": [], "music": [], "fx": []}
    for n, t in enumerate(tracks):
        chain = (f"[{t['label_src']}]aformat=sample_rates=48000:channel_layouts=stereo,"
                 f"asetpts=PTS-STARTPTS,volume={t['gain_db']}dB")
        if t["fade_in"]:
            chain += f",afade=in:st=0:d={t['fade_in']}"
        if t["fade_out"]:
            chain += f",afade=out:st={max(0, t['dur'] - t['fade_out']):.3f}:d={t['fade_out']}"
        ms = max(0, int(round(t["start"] * 1000)))
        chain += f",adelay={ms}:all=1[a{n}]"
        graph.append(chain)
        bus = "voice" if t["role"] in ("voice", "dialogue") else "music" if t["role"] == "music" else "fx"
        buses[bus].append(f"a{n}")

    def mix(labels, out):
        if len(labels) == 1:
            graph.append(f"[{labels[0]}]anull[{out}]")
        else:
            graph.append(f"{''.join(f'[{l}]' for l in labels)}amix=inputs={len(labels)}:normalize=0:duration=longest[{out}]")
        return out

    stems = []
    voice = mix(buses["voice"], "voicebus") if buses["voice"] else None
    music = mix(buses["music"], "musicbus") if buses["music"] else None
    if voice and music and edit.get("duck", True):
        graph.append(f"[{voice}]asplit=2[voicemix][voicekey]")
        graph.append(f"[{music}][voicekey]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[musicducked]")
        stems += ["voicemix", "musicducked"]
    else:
        stems += [s for s in (voice, music) if s]
    if buses["fx"]:
        stems.append(mix(buses["fx"], "fxbus"))
    if stems:
        mix(stems, "premix")
        graph.append(
            f"[premix]apad,atrim=duration={runtime:.3f},"
            f"loudnorm=I={edit.get('loudness', -14)}:TP=-1.5:LRA=11,aresample=48000[afinal]"
        )
    else:
        graph.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={runtime:.3f}[afinal]")

    out = os.path.join(base, edit.get("output", "final.mp4"))
    return timeline, runtime, inputs, graph, out, fps


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        die(__doc__)
    edit_path = os.path.abspath(args[0])
    with open(edit_path) as f:
        edit = json.load(f)
    base = os.path.dirname(edit_path)
    timeline, runtime, inputs, graph, out, fps = build(edit, base)

    if "--timeline" in args:
        for c in timeline:
            t = f"  → {c['trans']['type']} {c['trans']['duration']}s" if c["trans"] else ""
            print(f"{c['id']:<12} {c['start']:7.3f} – {c['start'] + c['dur']:7.3f}  ({c['dur']:.3f}s){t}")
        print(f"{'runtime':<12} {runtime:7.3f}s")
        return

    with tempfile.NamedTemporaryFile("w", suffix=".ffgraph", delete=False) as g:
        g.write(";\n".join(graph))
        graph_file = g.name
    cmd = (["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"] + inputs +
           ["-/filter_complex", graph_file, "-map", "[vfinal]", "-map", "[afinal]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    if "--dry-run" in args:
        print(shlex.join(cmd))
        print(";\n".join(graph))
        return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    result = subprocess.run(cmd)
    os.unlink(graph_file)
    if result.returncode != 0:
        die("ffmpeg failed; rerun with --dry-run to inspect the filter graph")
    print(json.dumps({"output": out, "runtime": round(runtime, 3)}))


if __name__ == "__main__":
    main()

# ffmpeg recipes

Recipes beyond the script's commands. `V` is the workspace's `video.*` file (or the stream URL in `stream.json`); write outputs into the workspace. `-ss` before `-i` seeks fast and still lands on the exact frame.

## Sound

Waveform, to find claps, hits, music drops, and dead air at a glance. The image spans the whole input, so trim with `-ss`/`-t` to read times off it.

```bash
ffmpeg -i V -filter_complex "showwavespic=s=1568x240:split_channels=1" -frames:v 1 wave.png
```

Spectrogram, to tell speech from music from noise, or spot a tone:

```bash
ffmpeg -i V -lavfi "showspectrumpic=s=1024x384:legend=1" spec.png
```

Loudness against a broadcast or platform spec (`I:` is integrated LUFS, `LRA` the range, `Peak` the true peak):

```bash
ffmpeg -nostats -i V -af ebur128=framelog=quiet:peak=true -f null - 2>&1 | grep -A15 Summary
```

Cut a stretch of audio, for a speech-to-text pass on one part or to hand the user:

```bash
ffmpeg -ss 1:10 -to 1:40 -i V -vn -c:a libmp3lame part.mp3
```

## Change between moments

Difference image: what changed between two times shows bright, what stayed is black. Good for UI state changes and edits in code on screen.

```bash
ffmpeg -ss 70 -i V -ss 74 -i V -filter_complex \
  "[0:v]format=gbrp,setpts=PTS-STARTPTS[a];[1:v]format=gbrp,setpts=PTS-STARTPTS[b];[a][b]blend=all_mode=difference" \
  -frames:v 1 diff.jpg
```

Side by side, for before and after, or two takes or two videos (swap the second `V` for the other file; heights must match, so add `scale=-2:720` to each input when they differ):

```bash
ffmpeg -ss 70 -i V -ss 74 -i V -filter_complex "[0:v][1:v]hstack" -frames:v 1 side.jpg
```

How much of the video is static: `mpdecimate` drops near-duplicate frames, so the output count against the total shows how much moves.

```bash
ffmpeg -nostats -i V -vf mpdecimate -f null - 2>&1 | grep -oE "frame= *[0-9]+" | tail -1
ffprobe -v error -select_streams v -count_packets -show_entries stream=nb_read_packets -of csv=p=0 V
```

## Timing to the frame

Exact frame times around a moment, for measuring how long something lasts. The listing starts at the keyframe before the requested second.

```bash
ffprobe -v error -select_streams v -read_intervals 70%+2 -show_entries frame=pts_time -of csv=p=0 V
```

Keyframes only, a fast skim of a long file when a download already exists:

```bash
ffmpeg -nostats -skip_frame nokey -i V -vf showinfo -fps_mode vfr -f null - 2>&1 | grep -oE "pts_time:[0-9.]+"
```

## Picture and file

Letterboxing or pillarboxing (the most frequent `crop=` value is the active picture):

```bash
ffmpeg -nostats -ss 30 -t 5 -i V -vf cropdetect -f null - 2>&1 | grep -o "crop=[0-9:]*" | sort | uniq -c | sort -rn | head -1
```

Interlacing (many `TFF`/`BFF` frames in the summary means interlaced):

```bash
ffmpeg -nostats -t 30 -i V -vf idet -f null - 2>&1 | grep "Multi frame detection"
```

Embedded subtitles (stream index from `summary.md`), to read alongside or instead of a transcript:

```bash
ffmpeg -i V -map 0:s:0 subs.srt
```

Visual similarity of two encodes of the same video (`All:` near 1.0 means near identical):

```bash
ffmpeg -i a.mp4 -i b.mp4 -lavfi ssim -f null - 2>&1 | grep SSIM
```

## For the user

A clip of the moment, re-encoded so it starts on the exact frame:

```bash
ffmpeg -ss 1:10 -to 1:15 -i V -c:v libx264 -crf 20 -c:a aac clip.mp4
```

A GIF of a short burst:

```bash
ffmpeg -ss 1:10 -t 3 -i V -vf "fps=12,scale=640:-2:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" clip.gif
```

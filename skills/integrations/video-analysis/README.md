# video-analysis

> Lets an agent see what a video shows. It fetches the video from a link or a local file, then pulls exactly the frames a question needs, at the moments that matter, with ffmpeg.

## What it does

A transcript only holds what was said. This skill covers what is on screen: the code in a tutorial, the steps of a bug repro, the shots of an ad, the moment a logo appears, whether a file has frozen frames or dead air.

One script, `scripts/video_analysis.py`, puts each video in a workspace folder and works on it:

- **`fetch`** downloads a link (any site [yt-dlp](https://github.com/yt-dlp/yt-dlp) reads), links a local file, or, with `--stream`, reads a long video over the network without downloading it. It writes `summary.md` with the title, duration, resolution, frame rate, audio, embedded subtitles, chapters, and YouTube's most-replayed moments.
- **`sheet`** tiles many moments into one contact sheet, each tile stamped with its time. A 12-tile sheet costs the model about as much as one full frame, so the agent surveys the whole video cheaply before zooming in.
- **`frames`** pulls full-resolution stills at given times, at an interval (down to bursts of several frames a second for motion), or one per shot, with an optional crop to read small text.
- **`scenes`** lists every cut with shot lengths; **`events`** finds black, frozen, and silent stretches.
- **`gemini`** asks Gemini about the video itself (frames and audio together), for long videos and long sequences. Its answers are treated as leads and confirmed against frames.

The agent works coarse to fine: survey with sheets, locate the seconds that hold the answer, inspect them with full frames. Speech comes from the [video-transcript](../video-transcript/README.md) skill, written into the same workspace, so the agent can search the transcript to find a moment and then look at it. A reference of tested ffmpeg recipes covers the rest: waveforms, difference images, side-by-side comparisons, loudness, letterboxing, frame-exact timing, and clips or GIFs for the user.

Every claim in the answer carries a timestamp and rests on a frame the agent looked at, and the answer says how densely it sampled when a missed moment would matter.

## When to use it

- *"What code does he write in this tutorial between 4:00 and 6:00?"*
- *"Here's a screen recording of the bug. What happens right before it crashes?"*
- *"When does the product first appear in this ad, and how long are the shots?"*
- *"Summarize what's shown in this 2-hour stream."*
- *"Does this export have any black frames or silent gaps?"*

## Example

```
$ video_analysis.py fetch "https://www.youtube.com/watch?v=zQnBQ4tB3ZA" --out videos
videos/youtube-zQnBQ4tB3ZA
  - Duration: 02:24.63 (144.63 s)
  - Video: av1 1280x720, 30 fps, 4334 frames
  - [00:47] Does TypeScript compile to JavaScript?

$ video_analysis.py sheet videos/youtube-zQnBQ4tB3ZA --count 12
videos/youtube-zQnBQ4tB3ZA/sheets/sheet-00006.03-01.jpg  (12 tiles, 00:06.03-02:18.59, 1564x664)

$ video_analysis.py frames videos/youtube-zQnBQ4tB3ZA --at 1:18 --crop 640:400:600:120
[01:18.00] videos/youtube-zQnBQ4tB3ZA/frames/t00078.000-crop.jpg
```

## Requirements

- `python3` and `ffmpeg`/`ffprobe`. Contact-sheet labels use a built-in font, so any ffmpeg build works.
- For links: `yt-dlp` (or [`uv`](https://docs.astral.sh/uv/), which runs the latest yt-dlp on demand). YouTube also needs a JavaScript runtime such as `deno`.
- Optional: `GEMINI_API_KEY` for `gemini`, and the `video-transcript` skill for speech.

## Install

```bash
npx skills add thatjuan/agent-skills --skill video-analysis
npx skills add thatjuan/agent-skills --skill video-transcript
```

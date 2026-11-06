# video-analysis

> Lets an agent see what a video shows. It fetches the video from a link or a local file, then pulls exactly the frames a question needs, at the moments that matter, with ffmpeg.

## What it does

A transcript only holds what was said. This skill covers what is on screen: the code in a tutorial, the steps of a bug repro, the shots of an ad, the moment a logo appears, whether a file has frozen frames or dead air.

One script, `scripts/video_analysis.py`, puts each video in a workspace folder and works on it:

- **`fetch`** downloads a link (any site [yt-dlp](https://github.com/yt-dlp/yt-dlp) reads), links a local file, or, with `--stream`, reads a long video over the network without downloading it. It writes `summary.md` with the title, duration, resolution, frame rate, audio, embedded subtitles, chapters, and YouTube's most-replayed moments.
- **`sheet`** tiles many moments into one contact sheet, each tile stamped with its time. A 12-tile sheet costs the model about as much as one full frame, so the agent surveys the whole video cheaply before zooming in.
- **`frames`** pulls full-resolution stills at given times, at an interval (down to bursts of several frames a second for motion), or one per shot, with an optional crop to read small text.
- **`screens`** splits a recorded meeting's screen share into its distinct screens (each slide, page, or app state) and lines each one up with what the transcript says was said while it was up. See below.
- **`scenes`** lists every cut with shot lengths; **`events`** finds black, frozen, and silent stretches.
- **`gemini`** asks Gemini about the video itself (frames and audio together), for long videos and long sequences. Its answers are treated as leads and confirmed against frames.

The agent works coarse to fine: survey with sheets, locate the seconds that hold the answer, inspect them with full frames. Speech comes from the [video-transcript](../video-transcript/README.md) skill, written into the same workspace, so the agent can search the transcript to find a moment and then look at it. A reference of tested ffmpeg recipes covers the rest: waveforms, difference images, side-by-side comparisons, loudness, letterboxing, frame-exact timing, and clips or GIFs for the user.

## Meeting recordings

A Zoom, Teams, or Meet recording with a screen share, plus its transcript, is where the skill earns the most. The user asks what was on screen when pricing came up, or wants meeting notes with the slide for each topic, or every slide as a deck.

`screens` crops to the shared content, leaving out webcam tiles that never hold still. It finds each screen as a stretch where that content holds still, so a new slide, a new bullet on the same slide, or a new page each starts a screen, while a moving mouse pointer doesn't. Cut detection misses these: a new slide on the same template barely registers as a change. Each screen is saved at its settled state, just before it changed, with every build step shown. `screens.md` lists every screen's time range and frame alongside the transcript lines said over it.

The transcript can be a Zoom or Teams `.vtt`, an `.srt`, or Otter, Meet, or plain text with timestamps. Wall-clock times and notetakers that started early are fixed with one offset. A transcript without times is replaced by a fresh one from `video-transcript`, with the user's copy kept for names and wording.

```
$ video_analysis.py screens videos/local-q3-sync --crop 1600:900:0:90 --transcript otter.txt --offset=-10:30:00
videos/local-q3-sync/screens/overview-01.jpg  (5 tiles, 00:19.70-01:29.70, 1564x498, ~1,008 tokens)
5 screens (0 moving); frames and videos/local-q3-sync/screens/screens.md

## Screen 4 · 00:45-01:10 (25 s) · s004-000069.70.jpg

[00:47] Ana Lopez: Next slide. As you can see, activation is where we lose people.
```

## Answers

Every claim in the answer carries a timestamp and rests on a frame the agent looked at, and the answer says how densely it sampled when a missed moment would matter.

## When to use it

- *"What code does he write in this tutorial between 4:00 and 6:00?"*
- *"Here's a screen recording of the bug. What happens right before it crashes?"*
- *"When does the product first appear in this ad, and how long are the shots?"*
- *"Summarize what's shown in this 2-hour stream."*
- *"Does this export have any black frames or silent gaps?"*
- *"Here's the Zoom recording and the transcript. Write up the meeting with the slide for each topic."*
- *"Which screen was Ben looking at when he asked about per-seat pricing?"*

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

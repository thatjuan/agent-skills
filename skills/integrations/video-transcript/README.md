# video-transcript

> Turns a video link into a transcript with timestamps and metadata. Works on YouTube, X/Twitter, TikTok, Instagram, Vimeo, Loom, podcasts, any other site yt-dlp reads, and local video or audio files.

## What it does

One script, `scripts/video_transcript.py`, writes a `transcript.md` per video: title, channel, date, duration, views and likes, description, chapters, YouTube's most-replayed moments, and the full transcript in paragraphs about a minute long, each with a timestamp, grouped under chapter headings.

It takes the best text source available:

1. **Published captions** in the spoken language, human ones over auto-generated, fetched with [yt-dlp](https://github.com/yt-dlp/yt-dlp).
2. **Speech-to-text** when a video has no captions or only partial ones (common on X): [ElevenLabs Scribe v2](https://elevenlabs.io/speech-to-text) when `ELEVENLABS_API_KEY` is set, which labels speakers, otherwise [parakeet-mlx](https://github.com/senstella/parakeet-mlx) or [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper) running locally on Apple Silicon.

For what is on screen rather than said (code, slides, demos), the [video-analysis](../video-analysis/README.md) skill pulls frames at the moments that matter. For a quick look, `--frames` saves a still at every scene change and at regular intervals, and for YouTube videos the skill asks Gemini about the video directly, clipped to the minutes that matter.

The agent then answers from the transcript, ties each claim to a timestamp, and says when the text came from auto captions or speech-to-text.

## When to use it

- *"Summarize this: https://youtu.be/…"*
- *"What does he say about pricing in this X video?"*
- *"Pull the code from this tutorial."*
- *"Does this talk actually claim that? Give me the timestamp."*

## Example output

```
# TypeScript in 100 Seconds

- URL: https://www.youtube.com/watch?v=zQnBQ4tB3ZA
- By: Fireship (@Fireship)
- Published: 2020-11-25
- Duration: 02:25
- Transcript: auto-generated captions (en-orig)

## Transcript

### What is TypeScript used for?

[00:00] typescript validate your javascript ahead of time with static type checking …
```

## Requirements

- `python3`, `ffmpeg`, and `yt-dlp` (or [`uv`](https://docs.astral.sh/uv/), which runs the latest yt-dlp on demand). YouTube also needs a JavaScript runtime such as `deno`.
- Optional: `ELEVENLABS_API_KEY` for cloud speech-to-text, `GEMINI_API_KEY` for on-screen questions on YouTube videos.

## Install

```bash
npx skills add thatjuan/agent-skills --skill video-transcript
```

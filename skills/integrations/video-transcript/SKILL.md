---
name: video-transcript
description: "Get the transcript and metadata of a video from its link: YouTube, X/Twitter, TikTok, Instagram, Vimeo, Loom, podcasts, and any other site yt-dlp reads. Published captions first, speech-to-text when there are none, frames or Gemini for what is on screen. Use when the user shares a video link and wants it summarized, quoted, searched, fact-checked, or used as context, or asks what a video says or shows."
---

# Video transcript

One script turns a video link into a **transcript.md**: the video's metadata (title, channel, date, duration, stats, description, chapters, most-replayed moments) followed by the full transcript in timestamped paragraphs under chapter headings. Answer from that file.

## 1. Fetch

```bash
python3 <skill-dir>/scripts/video_transcript.py "<url>" --out <dir>
```

`<dir>` is your scratchpad, or wherever the user wants the transcript kept. The script prints the path of each `transcript.md` it wrote, its source, and its size in words and tokens.

It takes the best text source it can find:

1. **Published captions** in the spoken language: human captions over auto-generated ones, never an automatic translation unless `--lang` asks for one.
2. **Speech-to-text** when there are no captions, or the captions cover less than half the video (X often stops captioning partway). Engines, in `auto` order: ElevenLabs Scribe v2 when `ELEVENLABS_API_KEY` is set (most accurate, labels speakers, about $0.22 per audio hour), then local parakeet-mlx on Apple Silicon (free, 25 European languages), then local mlx-whisper for other languages.

Flags:

- `--lang <code>`: caption language to prefer (`es`, `pt-BR`); also passed to speech-to-text as a hint.
- `--asr <engine>`: force `elevenlabs`, `parakeet`, `whisper`, or `none`. Use `whisper` with `--lang` when parakeet returns the wrong language.
- `--asr-only`: skip captions and transcribe the audio, for when the captions are poor.
- `--frames`: also save stills to `frames/` at every scene change and at least every ~10 s, listed with timestamps in `transcript.md`.
- `--cookies-from-browser <browser>`: for login-only or bot-checked videos. It reads the user's browser session, so ask before using it.

Exit `2` means no captions and no speech-to-text engine available; exit `3` means the link is a playlist or channel, with entries printed one per line. Run each entry the user cares about. Any other failure: read [`references/troubleshooting.md`](references/troubleshooting.md).

## 2. Read

Read the header first; it says where the text came from (`Transcript:` line). Then read the transcript, in parts when the token count is large, and follow what the user asked: summary, quotes, a specific claim, a step-by-step.

- **Auto-generated captions** come without punctuation and misspell names and jargon. Correct a proper noun from the title, description, or chapter list when quoting, and say the quote comes from auto captions.
- **Speech-to-text** carries `Speaker N:` labels when Scribe heard more than one voice. Name a speaker only when the video says who they are.
- **Timestamps** anchor every claim you report. On YouTube, link them as `https://youtu.be/<id>?t=<seconds>`.

## 3. Look at the screen when the words are not enough

A transcript holds speech only. When the answer depends on what is shown (code, terminal commands, slides, diagrams, a UI demo), get the pixels:

- **Any site**: rerun with `--frames`, then Read the frames nearest the timestamps that matter. The frames list in `transcript.md` maps each file to its time.
- **YouTube, long or dense with visuals**: ask Gemini about the video directly, with clip offsets to stay on the part that matters. See [`references/gemini.md`](references/gemini.md).

## Done

The answer is done when every claim in it traces to a timestamp in the transcript or a frame, and it states the transcript source when that source is auto captions or speech-to-text.

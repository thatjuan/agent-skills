# Troubleshooting

Match the yt-dlp error the script printed.

## "Sign in to confirm you're not a bot", HTTP 429, empty caption files (YouTube)

YouTube rate-limits by IP. Cloud, VPN, and datacenter addresses get blocked first, and heavy runs from a home IP can trip it too. In order:

1. Retry once after a minute. Avoid `--lang` for a language the video isn't spoken in: auto-translated tracks are the first thing YouTube throttles.
2. Ask the user, then rerun with `--cookies-from-browser chrome` (or `firefox`, `safari`) so yt-dlp uses their signed-in session.
3. Use Gemini, which fetches the video on Google's side: [`gemini.md`](gemini.md), transcript prompt.

## Extraction errors mentioning signature, nsig, challenge, or "no formats"

YouTube changes often and yt-dlp follows within days. Update it (`brew upgrade yt-dlp`, `pip install -U "yt-dlp[default]"`, or uninstall it so the script falls back to `uvx`, which runs the latest). YouTube also needs a JavaScript runtime for its challenges: `yt-dlp -v <url>` lists `JS runtimes`, and an empty list means install `deno`.

## Login required

Vimeo's web client, Instagram, protected X posts, age-restricted or members-only YouTube videos, and private Loom links all need a session. Ask the user, then rerun with `--cookies-from-browser <browser>` while they are signed in to that site in that browser.

## Unsupported URL

yt-dlp's generic extractor finds most embedded players. When it fails on an article or landing page, open the page, find the embedded video's own URL (a YouTube, Vimeo, Wistia, or `.m3u8`/`.mp4` link), and run the script on that.

## Wrong language or garbled speech-to-text

parakeet covers 25 European languages and detects the language itself. For anything else, rerun with `--asr whisper --lang <code>`, or `--asr elevenlabs` when the key is set.

## Live streams

Captions and audio of a stream in progress are incomplete. Wait until it ends and YouTube has processed it, or transcribe the recording once it is posted.

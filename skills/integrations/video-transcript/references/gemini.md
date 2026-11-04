# Gemini on YouTube links

Gemini reads a public YouTube video by URL, frames and audio both, fetched on Google's side. Reach for it in two cases:

- **What is on screen** across a long video, where downloading it for `--frames` would be slow: code on screen, slide text, a UI walkthrough.
- **YouTube blocks yt-dlp** on this machine (bot check, 429). Gemini does not go through the local IP, so it can still produce a transcript.

Limits: public YouTube videos only, one video per request, `GEMINI_API_KEY` in the environment. The free tier caps YouTube input at 8 hours of video per day. For other sites, use `--frames` instead.

## Request

```bash
cat > gemini-request.json <<'EOF'
{
  "contents": [{"parts": [
    {"file_data": {"file_uri": "https://www.youtube.com/watch?v=VIDEO_ID"},
     "video_metadata": {"start_offset": "600s", "end_offset": "900s"}},
    {"text": "PROMPT"}
  ]}],
  "generationConfig": {"mediaResolution": "MEDIA_RESOLUTION_LOW"}
}
EOF
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" -H 'Content-Type: application/json' \
  -d @gemini-request.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['candidates'][0]['content']['parts'][0]['text'] if 'candidates' in d else d)"
```

- `video_metadata` offsets clip the video to the part that matters. Drop them to send the whole video.
- `MEDIA_RESOLUTION_LOW` costs about 100 tokens per second of video, against about 300 at the default. It still reads code at normal editor font sizes; drop it when the text on screen is small.
- `gemini-flash-latest` tracks the current Flash model. Use `gemini-pro-latest` for hard visual reasoning.

## Prompts

Ask for timestamps on everything, so answers line up with `transcript.md`:

- On-screen code: `Quote verbatim every code block, terminal command, and file name shown on screen, each prefixed with its [MM:SS] timestamp.`
- Slides: `List each slide shown, with its [MM:SS] timestamp, its title, and its text verbatim.`
- Transcript (blocked fallback): `Transcribe the speech verbatim in timestamped paragraphs of about a minute, each starting with [MM:SS]. Label speakers when more than one person talks.`

A Gemini transcript is model-generated and can paraphrase or drop lines. Label it as such, and prefer captions whenever yt-dlp can reach them.

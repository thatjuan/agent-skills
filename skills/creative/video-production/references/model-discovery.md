# Model Discovery

Choose models at run time, every run. Each provider adds and retires models monthly, and the request body differs per model. A choice made from memory is either stale or malformed.

## Contents

- [How to choose](#how-to-choose)
- [What each role needs](#what-each-role-needs)
- [Runway](#runway)
- [fal](#fal)
- [ElevenLabs](#elevenlabs)
- [Where to generate stills](#where-to-generate-stills)
- [Snapshot, October 2026](#snapshot-october-2026)

---

## How to choose

For each role, in this order:

1. **Capability filter.** Drop every model that lacks a capability the role needs for *this* script (table below). A vertical 9:16 spot rules out models without a 9:16 ratio. A shot that has to land on a specific final frame needs last-frame keyframes.
2. **Newest flagship.** Among the survivors, prefer the newest top-tier model from its family. Use the provider changelog and the catalog order to tell what is new. A newer model from a family usually beats the older one, and "Fast", "Lite", "Mini", and "Turbo" variants trade quality for speed.
3. **Cost.** Break ties on price. Use a cheaper sibling only for drafts.
4. **Read the schema.** For the winner, read the exact request schema: allowed `ratio` values, `duration` range, reference limits, keyframe positions, whether audio can be switched off, and prompt length. Record the constraints in `plan.json → models`.

Pick a **fallback** video model with a different architecture, so the retry ladder has somewhere to go.

## What each role needs

| Role | Must have | Strongly prefer |
|------|-----------|-----------------|
| **Image (bible + keyframes)** | Reference-image editing with several references; the exact target aspect ratio; at least 2K output | References flagged as human subjects for identity, tagged references addressable from the prompt, transparent-background output (for overlays) |
| **Video (final)** | Image-to-video with a first-frame keyframe; the target ratio at 1080p; durations that cover the longest shot | First *and* last keyframes; an unpositioned reference mode (character sheets as references); the option to switch native audio off; seed control |
| **Video (draft)** | Same input modes as the final model | A draft or preview tier of the final model that can be enhanced later, so the approved draft and the final match |
| **Speech** | The script's language; audio tags or another way to direct delivery | Timestamps output (for captions); cloned or designed voices |
| **Dialogue** | Several voices in one generation with natural turn-taking | The same model family as Speech, so voices match |
| **Sound effects** | Explicit duration; seamless loop mode for ambience | A prompt-adherence control |
| **Music** | Duration control; instrumental mode | Timed sections (a composition plan), or scoring to a video file |

## Runway

Base URL `https://api.dev.runwayml.com`; the `X-Runway-Version` header is required (`runway.py` sends it).

1. Fetch `https://docs.dev.runwayml.com/llms.txt`. It points to everything below and states the current rules.
2. Read `https://docs.dev.runwayml.com/guides/models.md`: the catalog, with a one-line description of each model plus any model-specific guides (such as draft mode).
3. Check the changelog for what's new: `https://docs.dev.runwayml.com/api-details/api_changelog.md` (newest first).
4. Read the schema for each candidate in `https://docs.dev.runwayml.com/api.md`. Every model has its own section, so grep for it rather than reading 200 KB:

   ```bash
   curl -sL https://docs.dev.runwayml.com/api.md -o /tmp/runway-api.md
   grep -n "^#### POST /v1/image_to_video - model" /tmp/runway-api.md      # list candidates
   awk -v h='#### POST /v1/image_to_video - model `seedance2_5`' \
     'index($0,h)==1{p=1;print;next} p&&/^###/{exit} p' /tmp/runway-api.md  # one model's fields
   ```

   The input-parameters page (`/assets/inputs.md`) lists per-model aspect-ratio limits for input images, and says inputs that don't match `ratio` are center-cropped.
5. Prices are only on `https://docs.dev.runwayml.com/guides/pricing.md`. Use that page for the budget and nowhere else.
6. If the Runway Dev MCP server is connected, `list_models` gives live constraints for the account.

Endpoints that matter here: `/v1/text_to_image`, `/v1/image_to_video`, `/v1/text_to_video` (also reference-only generation and draft enhancement on some models), `/v1/video_to_video` (reference, extend, and edit modes on some models), `/v1/character_performance`, `/v1/avatar_videos`, `/v1/video_upscale`, and `/v1/uploads`.

## fal

Use the `fal-ai` MCP server:

- `models` with `category` (`text-to-image`, `image-to-image`, `image-to-video`, `text-to-video`) and `status: "active"` lists the catalog. Sort mentally by `updated_at` and by family version.
- `search` with a capability phrase ("edit multiple reference images") narrows the list. Free-text search with a category can come back empty; then drop the category or list with `models`.
- `find` with `expand: ["openapi-3.0"]` returns the exact input schema for a candidate. Check reference-image limits and supported sizes there.
- `estimate_cost` before a batch; `upload` turns a local file into a URL fal can read.

Without the MCP server, use REST with `Authorization: Key $FAL_KEY`. The `fal-studio` skill's `references/generation.md` covers it.

## ElevenLabs

Base URL `https://api.elevenlabs.io`, header `xi-api-key: $ELEVENLABS_API_KEY`.

1. Live models: `curl -s https://api.elevenlabs.io/v1/models -H "xi-api-key: $ELEVENLABS_API_KEY"`. Check `can_do_text_to_speech` and the languages.
2. Read the guidance `https://elevenlabs.io/docs/overview/models.md` (all model ids, including music and sound effects) and `https://elevenlabs.io/docs/eleven-api/choosing-the-right-model.md`.
3. Find endpoint schemas from `https://elevenlabs.io/docs/llms.txt`. Each API page is available as `.md`, for example `https://elevenlabs.io/docs/api-reference/music/compose.md`.

**Always pass `model_id` explicitly.** ElevenLabs endpoint defaults lag behind the newest models: text-to-speech defaults to an older multilingual model, dialogue to an older expressive model, and music to its first-generation model.

## Where to generate stills

Use **one image model for the whole bible and every keyframe**. Mixing models mixes rendering styles, and the cut shows it.

Pick the provider whose newest model passes the image capability filter. fal's catalog usually gets new image models first. Runway keeps the whole picture pipeline on one key, and a `runway://` upload made for keyframes is reused for video. When both providers offer equivalent models, use Runway. When fal has a clearly newer or more capable model, use fal for stills and pass the downloaded keyframes to Runway as local files.

Video runs on Runway. The user set this up deliberately; switch providers only if no Runway model can do a shot, and say so at the checkpoint.

## Snapshot, October 2026

This is a calibration point, not a choice. Rediscover every run, and replace this table when it goes stale.

| Role | Leading options seen | Why |
|------|----------------------|-----|
| Image | Runway `gpt_image_2_5_sunburst`, `gemini_image3_pro` (14 refs, 5 flagged human); fal `google/nano-banana-2.1`, `blackforestlabs/flux-3` | Multi-reference editing with identity hold; sunburst also renders transparent backgrounds |
| Video | Runway `seedance2_5` | First/last keyframes *or* up to 30 references, audio references, 4–30 s, 1080p, `draft: true` previews that can be enhanced to 1080p with the same seed |
| Video, other strengths | `veo3.1` (native speech, first/last frames), `wan3` (up to 30 s, video references), `gen4.5` (Runway's own image-to-video, first frame), `aleph2` (edits an existing clip), `act_two` (performance transfer) | Fallbacks and special cases |
| Speech / dialogue | ElevenLabs `eleven_v4` | Flagship; audio tags; 90+ languages; available for text-to-dialogue |
| Sound effects | ElevenLabs `eleven_text_to_sound_v2` | Duration up to 30 s, loop mode |
| Music | ElevenLabs `music_v2_5` | Composition plans with timed chunks; also video-to-music |

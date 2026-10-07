---
name: video-production
description: "Produce a finished video from a script with generative models: break the script into shots, build a look bible of characters and locations, generate keyframes, animate them on Runway, score voice, dialogue, sound effects, and music on ElevenLabs, then cut and mix with ffmpeg. Use when a video script, storyboard, or shot list should become an actual video, or for an AI-generated ad, short film, explainer, or social clip made end to end."
---

# Video Production

Turn a script into a finished, mixed video. The script (usually from `video-script`) says what the film is; this skill makes it with generated media and keeps it looking like one film from the first frame to the last.

Generated video drifts. Faces change between shots, wardrobe wanders, locations reshuffle. Stable results come from **anchors**: every generation is pinned to images already approved, and those images are pinned to a small **bible** of reference stills. Text prompts alone don't hold a character steady, but approved images do. So the order is always bible → keyframes → motion, and no clip is generated from text alone when a character or location recurs.

## Pipeline

```
script ─▶ models ─▶ breakdown ─▶ voice ─▶ bible ─▶ keyframes ─▶ CHECKPOINT ─▶ shots ─▶ lock ─▶ score ─▶ mix ─▶ QC
          (discover)  (plan.json)  (timing)  (refs)    (anchors)    (user: look    (takes)  (edit.json) (music,  (assemble.py)
                                                                     + budget)                          sfx)
```

Leading words used throughout:

- **Bible**: the approved reference stills for the whole film: style frame, character sheets, location plates, and props. Every keyframe is generated from it.
- **Anchor**: an approved still a video generation is pinned to (first frame, last frame, or reference).
- **Take**: one video generation of one shot. A shot keeps every take on disk, and one is `selected`.
- **Chain**: a cut inside continuous action. The next shot's first frame is the last frame of the previous selected take.
- **Lock**: picture lock, when the cut's timing is final. Music and sound effects are made to the locked cut and never before it.

## Inputs and preflight

1. **Script.** A `video-script` document: five lines, brief, sound plan, and frames with Shot, Visual, On-Screen, V/O, Dialogue, SFX, Music, and Transition fields. If the user brings only an idea, run `video-script` first. If they bring a looser script or shot list, map it onto those fields and note any gaps as assumptions in `plan.json`.
2. **Format.** Runtime, aspect ratio, and channel come from the script's title line and brief. Ask only when the script doesn't settle them.
3. **Environment.** Check without printing values: `RUNWAYML_API_SECRET`, `ELEVENLABS_API_KEY`, and `FAL_KEY` (or the `fal-ai` MCP server); `ffmpeg`/`ffprobe`; `python3`. Read the Runway credit balance with `scripts/runway.py get /v1/organization`.
4. **Project folder.** Work in `production/<slug>/` under the user's working directory, or wherever they say:

```
production/<slug>/
  plan.json          # the production manifest: single source of truth, resumable
  script.md          # the script as received
  bible/             # style frame, character sheets, location plates, props
  keyframes/         # <shot>-first.png, <shot>-last.png
  clips/             # <shot>-t<n>.mp4 (every take)
  audio/vo/  audio/dialogue/  audio/sfx/  audio/music/
  gfx/               # supers, lower thirds, end card (PNG with alpha)
  review/            # contact sheets and frame grabs
  edit.json          # the cut
  out/               # renders
```

`plan.json` is the production's memory. Write every decision, prompt, seed, task id, file, and cost to it as you go, so a run that stops halfway resumes from the file and never from recollection. Its shape is in [Plan Format](references/plan-format.md).

## Workflow

### 1. Discover models

Choose the current best model for each role: image, video (final plus draft tier), speech, dialogue, sound effects, and music. Never take a model name from memory or from this skill. Catalogs change monthly, and a request built for a retired id fails. [Model Discovery](references/model-discovery.md) gives the lookup for each provider and the capabilities each role needs.

Done when `plan.json → models` names, for every role, the model id, provider, the date checked, why it won, and the constraints that matter (allowed ratios, durations, reference limits, keyframe positions). You must have read those constraints from the API schema, not from a catalog blurb.

### 2. Break down

Turn the script's frames into **shots**: one shot is one video generation. Follow the breakdown rules in [Plan Format](references/plan-format.md). Split a frame that runs longer than the video model allows or that contains two actions or two camera setups. Choose each shot's generation mode, decide which shots chain, and list the characters, locations, and props each shot needs. Snap every shot's duration to a value the video model accepts, then add handles.

Done when every script frame maps to at least one shot, every shot has a mode, anchors, an allowed duration, and a motion prompt, and every recurring character, location, and prop has a bible entry.

### 3. Record voice first

Voiceover and dialogue set the timing, so generate them before any picture. Pick or design each voice, generate one file per line with the read direction as audio tags, measure the files, and stretch any shot whose line runs long. See [Sound](references/sound.md).

Done when every V/O and dialogue line has a file in `audio/`, its measured length is in `plan.json`, and every shot is long enough for the lines it carries.

### 4. Build the bible

Generate the style frame, then each character sheet, each location plate, and the props, following [Look and Consistency](references/look-and-consistency.md). Derive every variant from an approved image by reference editing. Never regenerate a character from text.

Done when each character's sheet images show one recognizable person in fixed wardrobe, each location has a plate at the target aspect ratio, and you have looked at every image (Read it) and checked it against the bible checklist.

### 5. Generate keyframes

Compose each shot's first frame (and last frame where the mode needs one) from the bible, with references attached, at the exact aspect ratio the video model will render. Leave first frames of chained shots empty for now; they come from the previous take in step 7.

Done when every non-chained shot has its anchors on disk and each one passes the keyframe checklist in [Look and Consistency](references/look-and-consistency.md).

### 6. Checkpoint: look and budget

This is the one approval stop before the expensive part. Show the user:

- a contact sheet of the bible and all keyframes in shot order (`ffmpeg` tile, see [Assembly](references/assembly.md)), with the shot ids;
- the chosen models, and the video spend from the provider's pricing page: shots × takes × seconds × rate, drafts included, plus audio;
- anything you assumed or changed from the script.

Get a yes, or changes, before the first video generation. The approval covers this estimate. If the real spend would pass it by more than 25%, stop and ask again.

### 7. Generate shots

Draft first, then generate finals of approved drafts only. Submit independent shots in parallel and chained shots in order. Review every take against the take checklist and climb the retry ladder when one fails. Modes, prompt craft, dialogue options, and the ladder are in [Shot Generation](references/shot-generation.md).

Done when every shot has a `selected` take that passes the take checklist, and every chained shot's first frame came from its predecessor's selected take.

### 8. Lock picture

Write `edit.json`: clip order, in and out points that trim the handles, transitions from the script's Transition fields, and V/O anchored to clip ids. Check the timing with `scripts/assemble.py edit.json --timeline`, render a rough cut with picture and voice only, and review it. See [Assembly](references/assembly.md).

Done when the runtime matches the script's within the tolerance in [Assembly](references/assembly.md), every line lands in its shot, and the rough cut passes review. From here, picture timing does not change.

### 9. Score and sound

Against the locked cut, generate sound effects from each frame's SFX field, ambience beds per location, the music, and the sonic logo, then add them to `edit.json`. See [Sound](references/sound.md).

Done when every SFX and Music field in the script has audio in `edit.json` or a note in `plan.json` explaining why it was dropped.

### 10. Mix, render, QC

Render with `scripts/assemble.py edit.json`. Add supers and the end card as PNG overlays, and captions as a sidecar file. Run the QC checklist in [Assembly](references/assembly.md) and fix every failure before delivering.

### 11. Deliver

Report the final file path, runtime, total spend by provider (from `plan.json → costs`), a contact sheet of the final cut, and any shots you would regenerate with more budget. Offer cutdowns or other aspect ratios when the script lists them.

## Rules

- **Land everything.** Provider output URLs expire within hours to days. Download every output to the project folder as it arrives and record it in `plan.json`. `runway.py run` downloads for you.
- **Schema before body.** Build each request body from the model's current API schema, read in step 1. Ratios, durations, and field names differ per model, even within one endpoint.
- **Look at everything.** Read every still you generate. Review every clip through a contact sheet and frame grabs. An unseen take is not reviewed.
- **Change one thing per retry**, and record what changed in `plan.json`, so the retry teaches you something.
- **Likeness and rights.** Generate real people only with their consent, and real brands only for their owner. Runway moderation failures cost credits and repeated ones can suspend the account, so rewrite a prompt that was moderated instead of resubmitting it.
- **Turns are scarce.** Batch independent generations in one turn, write each file once, and keep narration short: the run is long.

## Scripts

| Script | Use |
|--------|-----|
| [`scripts/runway.py`](scripts/runway.py) | Runway client: `run` (submit, wait, download), `submit`, `wait`, `upload`, `get`. Any `"local:<path>"` string in a body is uploaded automatically. Stdlib only. |
| [`scripts/assemble.py`](scripts/assemble.py) | Renders `edit.json`: trims, cuts, xfade transitions, stills, PNG overlays, audio placed by clip id, music ducked under voice, and loudness normalization. Has `--timeline` and `--dry-run` modes. Its docstring is the `edit.json` schema. |

## References

| Reference | Read during |
|-----------|-------------|
| [Model Discovery](references/model-discovery.md) | Step 1, and whenever a model fails or a request is rejected |
| [Plan Format](references/plan-format.md) | Steps 2 onward: the `plan.json` shape and the shot breakdown rules |
| [Look and Consistency](references/look-and-consistency.md) | Steps 4 and 5: bible, character sheets, keyframes, chains, still checklists |
| [Shot Generation](references/shot-generation.md) | Step 7: modes, motion prompts, dialogue and lip sync, take review, the retry ladder |
| [Sound](references/sound.md) | Steps 3 and 9: voices, dialogue, sound effects, ambience, music, mix targets |
| [Assembly](references/assembly.md) | Steps 6, 8, and 10: contact sheets, `edit.json`, overlays, captions, QC |

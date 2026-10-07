# video-production

> Turns a video script into a finished, mixed video: keyframes and characters made with image models, shots animated on Runway, voice, effects, and music from ElevenLabs, all cut together with ffmpeg.

## What it does

`video-production` picks up where [`video-script`](../video-script/) stops. It reads the script's frames and makes the film they describe with generative models, keeping one look and one cast from the first shot to the last.

Generated video drifts: faces change between shots, wardrobe wanders, rooms rearrange. The skill holds the film steady by **anchoring** every generation to approved images. It first builds a **bible** of reference stills (a style frame, a character sheet for each person, a plate for each location, and the hero props), each derived from the last by reference editing. Every keyframe is then composed from the bible, and every shot is animated from its keyframes. Shots that continue each other's action are **chained**: the last frame of one take becomes the first frame of the next.

Sound runs on a deliberate clock. Voiceover and dialogue are recorded first, because they set how long each shot plays. Music and effects come last, made to the locked cut: either a composition plan whose sections match the edit's timing, or music scored straight from the cut.

The skill never hardcodes a model. Each run it reads Runway's, fal's, and ElevenLabs' current catalogs and API schemas, picks the newest model with the capabilities each role needs, and records why. Nothing expensive happens before a single checkpoint, where you see the bible, every keyframe, and a budget estimate before any video is generated.

Two bundled scripts do the mechanical work: `runway.py` submits generations, waits, and downloads, uploading local keyframes on the fly, and `assemble.py` renders an edit decision list into the finished video with trims, transitions, overlays, ducked music, and loudness normalization.

## When to use it

- *"Here's the script for the Riverside spot. Make the video."*
- *"Produce this 60-second explainer with a narrator and two characters."*
- *"Turn my storyboard into a 15-second vertical ad."*
- *"Make an AI short film from this treatment, consistent characters throughout."*
- *"Re-cut the film with the new voiceover and regenerate shot 7."*

Not the right skill if you still need the story or the script: start with [`video-script`](../video-script/). For a motion-graphics piece, animated type, or a composition built mostly from HTML, use `hyperframes` (that skill also finishes a film this one generated, when it needs designed captions or kinetic type).

## Example walkthrough

**Prompt**

> Produce the "First Light" 30s spot from `scripts/first-light.md`. 16:9 for YouTube pre-roll.

**What happens**

1. **Models.** It reads the provider catalogs and records, for example, a multi-reference image model for stills, a video model with first/last keyframes and a draft tier, and the current flagship speech, effects, and music models, with each one's allowed ratios and durations.
2. **Breakdown.** Ten script frames become twelve shots. Frame 4 splits into an insert and a reaction, and frames 5 and 6 are marked as a chain because the whip pan carries action through the cut.
3. **Voice.** The one V/O line ("You don't have to ask. We're already on the way.") is recorded first and measures 3.4 s, so the end-card shot grows from 3 s to 4 s.
4. **Bible and keyframes.** A style frame (pre-dawn blue, warm practicals, film grain), Maya's portrait and three derived angles, the bedroom and street plates, the cup with the marker sun, then a first frame for every shot.
5. **Checkpoint.** One contact sheet of bible and keyframes plus the estimate: twelve shots of drafts and finals, at the video model's per-second rate. You approve it or ask for changes.
6. **Shots.** Drafts render at 480p, are reviewed frame by frame, and the approved drafts are enhanced to 1080p. Shot 3's first draft has Maya stand too fast; the retry slows the action and passes.
7. **Lock, score, mix.** The cut is locked at 30.0 s. The piano score is a four-chunk composition plan that builds through the Conflict and resolves on the door, with bedspring and cleat effects anchored to their clips, mixed to −14 LUFS.

**Excerpt from `plan.json`**

```json
{ "id": "s03", "frame": 3, "line": "Desire, into Conflict",
  "cut_duration": 3.0, "gen_duration": 4, "mode": "first",
  "characters": ["maya"], "location": "bedroom",
  "motion_prompt": "Camera locked off. Maya leans forward to stand, slowly; the baby stirs and she freezes, then sinks back onto the bed and resumes a gentle sway. Focus racks from her shoulder to the kitchen doorway and back.",
  "takes": [
    { "n": 1, "kind": "draft", "status": "rejected", "review": "stands too quickly, sway lost" },
    { "n": 2, "kind": "draft", "change": "added 'slowly' and 'barely rising'", "status": "approved" },
    { "n": 3, "kind": "final", "from_draft": 2, "status": "selected" } ] }
```

## Installation

```bash
npx skills add thatjuan/agent-skills --skill video-production
```

Needs `RUNWAYML_API_SECRET` and `ELEVENLABS_API_KEY` in the environment, `FAL_KEY` or the `fal-ai` MCP server for fal image models, plus `ffmpeg`/`ffprobe` and Python 3.

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The pipeline, eleven steps with completion criteria, the checkpoint, and the hard rules |
| `references/model-discovery.md` | How to find and vet the current model for each role on Runway, fal, and ElevenLabs, plus a dated snapshot |
| `references/plan-format.md` | The `plan.json` production manifest and the rules for breaking frames into shots |
| `references/look-and-consistency.md` | Style frame, character sheets, location plates, keyframes, chains, and still checklists |
| `references/shot-generation.md` | Generation modes, motion prompts, dialogue and lip-sync options, take review, and the retry ladder |
| `references/sound.md` | Voices, voiceover, dialogue, sound effects, ambience, music routes, and mix levels |
| `references/assembly.md` | Contact sheets, `edit.json`, supers and captions, rendering, QC, and cutdowns |
| `scripts/runway.py` | Runway client: run, submit, wait, upload, get; auto-uploads `local:` paths |
| `scripts/assemble.py` | Renders `edit.json` with ffmpeg; `--timeline` and `--dry-run` modes |

## Tips

- **Bring a full script.** The more specific the Visual, Shot, and Sound fields, the less the skill has to invent, and the more the bible looks like what you pictured.
- **Spend your attention at the checkpoint.** Changing a keyframe costs cents; changing a finished shot costs a video generation. Push back on faces, wardrobe, and framing there.
- **Real products need real photos.** Hand over product shots and logos, and they become references instead of guesses.
- **Let dialogue hide.** Lip sync is the least reliable part of generated video. Scripts that stage speech over the shoulder, wide, or as voiceover come out cleaner.
- **Everything lives in `plan.json`.** To regenerate one shot or swap the music, ask for it; the run resumes from the manifest without redoing approved work.
- **Ask for drafts only** if you want to see motion before committing to finals on a long piece.

## Related skills

- [`video-script`](../video-script/): writes the script this skill produces.
- [`creative-director`](../creative-director/): defines a brand's visual world before you script.
- [`fal-studio`](../fal-studio/): generated stills and film for websites, and fal REST details.
- [`clean-writing`](../clean-writing/): for any copy on the end card or in supers.

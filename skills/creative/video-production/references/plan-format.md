# Plan Format

`plan.json` is the production manifest. Every step reads it and writes it back, so a stopped run resumes from the file. This page defines its shape and the rules for breaking a script into shots.

## Contents

- [Shot breakdown](#shot-breakdown)
- [Shape](#shape)
- [Statuses](#statuses)
- [Costs](#costs)

---

## Shot breakdown

A **shot** is one video generation. A script frame becomes one shot or several.

- **Split** a frame that contains two camera setups, two distinct actions, a duration longer than the video model's maximum, or a cut the script's Shot field implies ("cut to CU of her hand").
- **Keep one primary action and one camera move per shot.** Models handle one thing well and two things poorly. "She lifts the cup and turns to the window while we dolly left" is two shots or a simpler action.
- **Duration.** Use the frame's timecode length, stretched to fit any V/O or dialogue measured in step 3. Then add **handles**: about 0.5 s at each end when the model allows it, because models often ease in and settle out, and the edit trims that away. Snap up to the nearest duration the model accepts. Record both `cut_duration` (what plays in the edit) and `gen_duration` (what you generate).
- **Mode** (see [Shot Generation](shot-generation.md)): `first` (default), `first_last`, `reference`, `extend`, `performance`, or `avatar`.
- **Chains.** When two consecutive shots are continuous action in the same space (the script's Transition is a match on action, or the camera keeps moving through the cut), mark the second shot `chain_from` the first. Its first frame becomes the last frame of the first shot's selected take. Hard cuts to a new angle are **not** chains; they get fresh keyframes from the bible, which holds continuity better than a chain, because a chain carries drift forward.
- **Coverage over lip sync.** When a dialogue frame can be staged without visible lips (over-the-shoulder from behind, a wide, a cutaway to the listener, the line as V/O), note that option in the shot's `notes`. Lip sync is the weakest link in generated video.
- **Text stays out of picture.** On-Screen supers, logos, CTAs, and captions are overlays added in post, never generated into frames. Product packaging with printed text uses a real product photo as a reference.

## Shape

Fields are listed with an example value. Keep keys stable; add a field when a shot needs it.

```json
{
  "title": "First Light",
  "slug": "first-light",
  "format": { "runtime": 30, "ratio": "16:9", "size": "1920x1080", "fps": 24, "channel": "YouTube pre-roll" },
  "assumptions": ["Riverside app UI shown as a generic dark-mode order screen"],

  "models": {
    "image":  { "provider": "runway", "id": "gpt_image_2_5_sunburst", "checked": "2026-10-07",
                "why": "16 tagged refs, 4K, transparent bg", "constraints": { "ratio": "1920:1088", "max_refs": 16 } },
    "video":  { "provider": "runway", "id": "seedance2_5", "checked": "2026-10-07",
                "why": "first/last keyframes or 30 refs, 4-30s, 1080p",
                "constraints": { "ratio": "1920:1080", "duration": "4-30", "audio_toggle": true } },
    "video_draft": { "provider": "runway", "id": "seedance2_5", "params": { "draft": true } },
    "video_fallback": { "provider": "runway", "id": "veo3.1" },
    "speech": { "provider": "elevenlabs", "id": "eleven_v4" },
    "sfx":    { "provider": "elevenlabs", "id": "eleven_text_to_sound_v2" },
    "music":  { "provider": "elevenlabs", "id": "music_v2_5" }
  },

  "bible": {
    "style": { "file": "bible/style.png", "descriptor": "pre-dawn blue-black, single warm practicals, 35mm film grain, soft halation" },
    "characters": [
      { "id": "maya", "tag": "maya",
        "descriptor": "Maya, late 20s, tired warm eyes, dark hair half-up in a tortoiseshell claw clip, oversized oatmeal cardigan over a faded band t-shirt",
        "files": ["bible/maya-portrait.png", "bible/maya-full.png", "bible/maya-34.png"],
        "voice": { "voice_id": "…", "name": "…", "settings": { "stability": 0.5 } } }
    ],
    "locations": [
      { "id": "bedroom", "descriptor": "small city bedroom, unmade bed, sheer curtain, blue moonlight, warm bedside lamp camera-left",
        "files": ["bible/bedroom-plate.png"] }
    ],
    "props": [ { "id": "cup", "descriptor": "white paper cup, hand-drawn marker sun on the lid", "files": ["bible/cup.png"] } ]
  },

  "voice": [
    { "id": "vo01", "shot": "s09", "text": "[warm, dry] You don't have to ask. We're already on the way.",
      "file": "audio/vo/vo01.mp3", "duration": 3.4, "status": "done" }
  ],

  "shots": [
    { "id": "s02", "frame": 2, "line": "Situation",
      "cut_duration": 3.0, "gen_duration": 4, "mode": "first",
      "characters": ["maya"], "location": "bedroom", "props": [],
      "chain_from": null,
      "keyframes": { "first": { "file": "keyframes/s02-first.png", "prompt": "…", "refs": ["bible/maya-portrait.png", "bible/bedroom-plate.png", "bible/style.png"], "seed": 1234, "status": "approved" } },
      "motion_prompt": "Slow handheld push-in. Maya sways gently side to side, eyes half-closed; the baby's hand flexes once. Curtain drifts.",
      "audio": false,
      "takes": [
        { "n": 1, "kind": "draft", "task_id": "…", "file": "clips/s02-t1.mp4", "seed": 77, "review": "identity holds; sway too fast", "status": "rejected" },
        { "n": 2, "kind": "draft", "task_id": "…", "file": "clips/s02-t2.mp4", "seed": 78, "change": "added 'slow, barely moving'", "status": "approved" },
        { "n": 3, "kind": "final", "task_id": "…", "file": "clips/s02-t3.mp4", "from_draft": 2, "status": "selected" }
      ],
      "notes": "" }
  ],

  "sound": {
    "sfx":      [ { "id": "sfx03", "shot": "s03", "prompt": "bedsprings creak, small, close", "file": "audio/sfx/sfx03.mp3", "at": "s03+0.8" } ],
    "ambience": [ { "id": "amb-bedroom", "location": "bedroom", "prompt": "…", "loop": true, "file": "audio/sfx/amb-bedroom.mp3" } ],
    "music":    { "route": "composition_plan", "file": "audio/music/score.mp3", "plan": "audio/music/plan.json" }
  },

  "costs": [ { "step": "s02 take 2", "provider": "runway", "credits": 40 } ],
  "approvals": [ { "at": "2026-10-07T15:12", "what": "look + budget", "estimate": { "runway_credits": 2400, "elevenlabs_credits": 9000 } } ]
}
```

**Descriptors** are fixed phrases. Paste each one verbatim into every prompt where that character, location, or style appears, so the text side of the anchor never varies between shots.

## Statuses

| Object | Statuses |
|--------|----------|
| Keyframe | `pending` → `generated` → `approved` / `rejected` |
| Take | `queued` → `generated` → `approved` (draft passed) / `rejected` → `selected` (the one in the cut) |
| Voice line, SFX, music | `pending` → `done` / `rejected` |

On resume, read `plan.json`, list what is not `approved`, `selected`, or `done`, check that those files exist on disk, and continue from the first gap.

## Costs

Append an entry after every billable call: Runway's response includes `estimatedCost.credits`; fal's `estimate_cost` gives a price; ElevenLabs reports character or credit usage (`GET /v1/user/subscription` before and after a batch gives the difference). The delivery report sums this list by provider.

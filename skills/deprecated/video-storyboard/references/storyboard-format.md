# Storyboard Format

The exact markdown output specification for an all-text video storyboard, with a complete worked example. The format is the deliverable contract — agents follow it so the output is consistent, scannable, and production-ready.

## Table of Contents

- [Top-Level Structure](#top-level-structure)
- [Frame Schema](#frame-schema)
- [Field Conventions](#field-conventions)
- [Worked Example — 30s Spot](#worked-example--30s-spot)
- [Variants](#variants)

---

## Top-Level Structure

```markdown
# [Spot Title] — [Brand] | [Duration] | [Aspect Ratio]

## Logline
[One sentence — premise of the spot, customer-facing.]

## Strategic Setup
- **Audience:**
- **Single-Minded Proposition:**
- **Tone:**
- **Format:** [Duration · Channel · Aspect ratio]
- **Story Frame:** [Chosen narrative skeleton]
- **Hook Window:** [First Ns — what lands]

## Treatment
[120–250 words of director-readable prose. The spot in narrative form.]

## Audio Architecture
- **Music:**
- **V/O:** [Voice profile + approx. word budget]
- **Dialogue:** [If any]
- **SFX posture:**
- **Sonic logo:**

## Storyboard

[Frame 1, Frame 2, … Final Frame]

## Production Notes
- **Locations:**
- **Cast:**
- **Wardrobe / Props:**
- **VFX / Graphics:**
- **Mandatories:**

## Cutdown Notes (optional)
- **15s cutdown anchor frames:** [list of frame numbers]
- **6s bumper anchor frames:** [list]
- **Vertical / 9:16 reframing notes:** [...]
```

---

## Frame Schema

Each frame uses an H3 heading with frame number and timecode, followed by labeled fields:

```markdown
### Frame [N] — `MM:SS–MM:SS`
**Shot:** [size + angle + lens + movement]
**Visual:** [Rich, specific prose. Multiple sentences welcome. Cast, wardrobe, location, light, color, action, blocking, expression, motion-in-frame, foreground/midground/background.]
**On-Screen:** [Super, kinetic type, lower-third, end card, legal — or `—` if none]
**V/O:** "[Copy in quotes]" *(read direction in italics — pace and tone)*
**Dialogue:** *[Character]* "[Line]" *(delivery)*  —  or `—` if none
**SFX:** [Diegetic + designed sound]
**Music:** [Behavior at this beat — build / drop / sting / silence / needle-drop reference]
**Transition:** [Out of this frame — hard cut / match cut / J-cut / whip / dissolve / etc.]
**Note:** [Optional — director's-eye intent, one sentence]
```

Fields that don't apply to a frame use `—` rather than being dropped, so the reader can scan a column.

---

## Field Conventions

- **Timecode** — `MM:SS–MM:SS` (start–end). Use `00:00:00–00:00:03` only for content longer than a minute.
- **Shot** — terse. Compose from [Shot Language](shot-language.md) vocabulary. *"Slow push-in MCU, 35mm, eye-level."*
- **Visual** — full sentences, not script directions. The longest field. Dense with specifics. Reference [Visual Description Craft](visual-description-craft.md).
- **On-Screen** — quote text exactly as it appears: `[KINETIC]: "you tried."`. Indicate type style if material: *kinetic, sans, all-caps, bottom-third, white on black box*.
- **V/O** — copy in straight double quotes. Append the read direction in italics: `*(warm, dry, conversational — landing the joke flat)*`.
- **Dialogue** — character name italicized, line in quotes, delivery direction in italics. Note language if non-English.
- **SFX** — comma-separated list of cues, each with a brief modifier: `kettle whistle (rising), distant traffic, cat bell jingle once`.
- **Music** — describe behavior, not just tracklist: `score holds at low pad, drops to silence on the cut`.
- **Transition** — name the technique. The transition belongs to the *outgoing* frame.
- **Note** — optional. One sentence. The *why* — story job, character beat, brand integration intent.

---

## Worked Example — 30s Spot

```markdown
# "First Light" — RIVERSIDE COFFEE | 30s | 16:9

## Logline
A new mother is learning her baby's pre-dawn rhythm — and Riverside is learning it with her.

## Strategic Setup
- **Audience:** Parents of newborns / under-twos. Sleep-deprived, time-starved, finding small dignities where they can.
- **Single-Minded Proposition:** Riverside delivers your coffee before you remember you wanted it.
- **Tone:** Warm, observational, a little wry. Earned-sweet, never saccharine. Real not aspirational.
- **Format:** 30s · YouTube pre-roll + CTV · 16:9 (with 9:16 cutdown)
- **Story Frame:** Pixar Story Spine — *"Once upon a time… Every day… One day… Because of that… Until finally…"*
- **Hook Window:** First 3 seconds — the bottle, the silence, the look.

## Treatment
A young mother, *Maya,* moves through the small choreography of a 4:47am feed in a one-bedroom apartment. The world is quiet — only the building hum, a dripping tap, a baby's soft snuffle. She doesn't speak. Neither does the V/O at first. We watch her cradle, sway, settle. She reaches for her phone with her free hand, taps it twice, and slips it back. Outside, dawn is just starting. We follow the order: a cyclist clipping in, a paper bag of beans being weighed, a barista pulling a shot at our roastery six blocks away. The handoff at the door is silent — no buzzer, just a soft text-vibration. Maya opens the door to find a paper cup steaming on the mat, a tiny sun drawn on the lid in marker. She closes the door, sits, drinks. The baby is finally asleep. *"You don't have to ask. We're already on the way."* Riverside logo, sonic mark, end frame.

## Audio Architecture
- **Music:** Spare upright piano — single-finger right-hand melody, no left hand. Builds gently to a held warm chord at the door reveal. No drop, no swell.
- **V/O:** One line, end of spot. Female, late 30s, warm, dry, slight rasp — Phoebe Waller-Bridge tonality. ~15 words.
- **SFX posture:** Naturalistic and quiet. Negative space is the design choice. Phone vibration is the only sharp transient.
- **Sonic logo:** Two-note marimba mark on the brand reveal.

## Storyboard

### Frame 1 — `00:00–00:03`
**Shot:** Static ECU, 100mm.
**Visual:** A single bottle of breast-milk on a kitchen counter, its surface beaded with condensation. Behind it, soft and out of focus, the orange digits of a microwave clock read **4:47**. The world is blue-black; only a single under-cabinet LED warms the bottle from the right.
**On-Screen:** —
**V/O:** —
**Dialogue:** —
**SFX:** A faint refrigerator hum. One floorboard creak somewhere off-screen.
**Music:** Single piano note, sustained.
**Transition:** Hard cut.
**Note:** The hook. No baby yet. The audience leans in to figure out what they're looking at.

### Frame 2 — `00:03–00:07`
**Shot:** Slow push-in MS, handheld, 35mm.
**Visual:** *Maya, late 20s,* sits on the edge of an unmade bed in an oversized cardigan over an old t-shirt, sock-feet on a rug. She holds her newborn against her shoulder, swaying. Hair half-up with a clip. Single warm bedside-lamp practical, the rest of the room blue moonlight from a sheer-curtained window. She's not smiling. She's not frowning. She's just *there* — the specific exhaustion of being needed by someone who can't say thank you yet.
**On-Screen:** —
**V/O:** —
**Dialogue:** —
**SFX:** Baby's snuffly breathing. A single car passing far below.
**Music:** Piano adds a second note.
**Transition:** Hard cut on a sway.
**Note:** "Save the cat" — we are with her in three seconds.

### Frame 3 — `00:07–00:10`
**Shot:** Insert, top-down ECU, macro, locked off.
**Visual:** Maya's free thumb on her phone screen. The Riverside app, dark mode. She taps the saved order — a flat white — once. The button pulses. She sets the phone face-down on the duvet without looking at it.
**On-Screen:** Brief in-app type: `Order placed · ETA 18 min` — small, soft.
**V/O:** —
**Dialogue:** —
**SFX:** Single soft haptic tick on the tap.
**Music:** Piano holds.
**Transition:** Match cut on the dark phone screen → dark window.

### Frame 4 — `00:10–00:13`
**Shot:** WS, locked off, 28mm. Slight high angle from a third-floor window.
**Visual:** Pre-dawn city street below. Empty. Wet asphalt reflecting one yellow streetlight. A lone cyclist enters frame from the right — backlit, breath visible, an insulated delivery cube on the rear rack with a small **R** monogram on its side. He clips in and pushes off without ceremony.
**On-Screen:** —
**V/O:** —
**Dialogue:** —
**SFX:** Click of cleat into pedal. Single pigeon. Distant garbage truck two blocks away.
**Music:** Piano adds a third note — the melody starts to feel like a melody.
**Transition:** Whip pan blurs into next frame.

### Frame 5 — `00:13–00:16`
**Shot:** MS, side-on, 50mm, slight track left following hands.
**Visual:** Inside Riverside roastery — warm sodium-toned, exposed brick, hanging Edison bulbs. A *barista, mid-30s, tattooed forearms,* weighs beans on a brass scale. Steam rises from a portafilter behind him. He works with the slow precision of someone who isn't being watched.
**On-Screen:** —
**V/O:** —
**Dialogue:** —
**SFX:** Beans pouring into the hopper. Grinder spins up briefly. Steam wand hiss.
**Music:** Piano blooms — two notes become three.
**Transition:** J-cut: we hear the next SFX before we see it.

### Frame 6 — `00:16–00:19`
**Shot:** ECU insert, macro, locked off.
**Visual:** A black marker draws a tiny sun — six rays, one circle — on the white plastic lid of a paper cup. Slow, considered. The cup sits on a wooden counter still wet from being wiped down.
**On-Screen:** —
**V/O:** —
**Dialogue:** —
**SFX:** Squeak of marker on plastic. Soft.
**Music:** Held.
**Transition:** Match cut: marker sun → real sun cresting a building.

### Frame 7 — `00:19–00:22`
**Shot:** Static WS, low angle, 24mm.
**Visual:** Apartment hallway, exterior of Maya's door. The cyclist has gone — only the cup, on the doormat, a thin curl of steam rising. The hallway sconce is still on; outside the window at the end of the hall, the sky is just turning bruise-blue to peach.
**On-Screen:** —
**V/O:** —
**Dialogue:** —
**SFX:** Faint elevator distant. Building hum.
**Music:** Held warm chord — the resolution.
**Transition:** Cut on a phone vibration we *hear* before next frame.

### Frame 8 — `00:22–00:26`
**Shot:** MS, eye-level, slight push-in, 35mm.
**Visual:** Maya, baby now asleep on her chest, opens the door slowly so it doesn't creak. She looks down at the cup. She breathes out — not a smile exactly, but something close. She bends, picks it up, sees the marker sun, and *now* she smiles, briefly, privately. She closes the door with her hip.
**On-Screen:** —
**V/O:** —
**Dialogue:** —
**SFX:** Door latch — gentle.
**Music:** Held chord begins to fade.
**Transition:** Hard cut.

### Frame 9 — `00:26–00:29`
**Shot:** Static MCU, 50mm.
**Visual:** Maya, back on the edge of the bed, sips. Eyes closed. The first sip of coffee, that specific shoulders-dropping moment. The baby is asleep. The room is warm now — the sun has crept in.
**On-Screen:** —
**V/O:** "You don't have to ask. We're already on the way." *(warm, dry, half-whispered, Phoebe Waller-Bridge tonality)*
**Dialogue:** —
**SFX:** The smallest of sips.
**Music:** Piano releases. Silence.
**Transition:** Hard cut to end frame.

### Frame 10 — End Card — `00:29–00:30`
**Shot:** Static graphic.
**Visual:** Black frame. Riverside wordmark center, in a quiet warm-white serif. Below it, in a small handwritten script: *coffee, before you ask*. A small marker-drawn sun beside the wordmark — the same one from the lid.
**On-Screen:** `RIVERSIDE COFFEE` · *coffee, before you ask* · `riverside.co/app`
**V/O:** —
**Dialogue:** —
**SFX:** —
**Music:** Two-note marimba sonic logo.
**Transition:** Fade to black.

## Production Notes
- **Locations:** One small one-bed apartment (interior, hallway, exterior door); one Riverside roastery interior (existing); one quiet city street (pre-dawn, permitted block).
- **Cast:** Maya (lead, late 20s, real-feeling cast — not model casting); newborn (real or animatronic, depending on schedule); cyclist (mid-20s, athletic build); barista (mid-30s, tattoos, weathered hands).
- **Wardrobe / Props:** Maya — oversized oatmeal cardigan, faded band t-shirt, sock-feet. Cyclist — Riverside-branded delivery cube + monogram cap. Cup — kraft paper, white plastic lid, hand-drawn marker sun.
- **VFX / Graphics:** In-app UI overlay (Frame 3); end-card typography (Frame 10).
- **Mandatories:** Logo + tagline + URL on end frame (~3s held). Sonic logo on end card. Caption track for sound-off platforms.

## Cutdown Notes
- **15s cutdown anchor frames:** 1, 2, 6, 8, 10
- **6s bumper anchor frames:** 1, 8, 10
- **9:16 reframing notes:** Frames 4 and 7 require reframing — the cyclist enters from a vertical-friendly entry point; the hallway becomes a top-down insert of the cup on the doormat.
```

---

## Variants

### Vignette / Anthem Storyboards

For montage-driven anthem spots, use a single H3 per *vignette* (which may be 1–4 frames internally), then list the constituent frames as a numbered list within. Keep the V/O as a separate continuous block at the top of the storyboard, with timecode anchors that map V/O lines to frames.

### Demo / Product Hero Storyboards

Lean heavily on the **Insert** frame type. Most frames in a demo spot are inserts. Add a `Product Action:` field above `Visual:` to specifically describe what the product is doing in the shot.

### Founder / Testimonial Storyboards

Add a `Subject:` field above `Visual:` with the speaker's name, role, and a short bio sentence. Add a `Soundbite:` field for the verbatim line they deliver, separate from `V/O:` (which is reserved for narration).

### Episodic / Campaign Storyboards

Storyboard each episode in its own document, with a top-level "Campaign Bible" document containing the recurring cast bible, the campaign V/O voice, the sonic-logo treatment, the end-frame rules, and the through-line tagline.

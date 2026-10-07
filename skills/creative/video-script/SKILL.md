---
name: video-script
description: "Write a production-ready video script a crew can shoot and cut from: a five-line story spine, a treatment, and shot-by-shot frames with visuals, voiceover, dialogue, sound, and timing. Use for ads and commercials, brand films, social spots, YouTube and creator videos, explainers, founder stories, and short documentaries, or when a video idea needs its story found."
---

# Video Script

A video script here is the whole blueprint: the story, plus every frame a director, DP, editor, and sound designer need to build it. Frames are written in prose, not drawn, and the prose is specific enough that the whole crew pictures the same film.

Everything hangs off the **five lines**. Filmmaking is a long run of decisions (casting, lenses, transitions, voiceover, grade), and the core of the story gets lost among them. No camera move or edit rescues a video that doesn't know what it is about. So the five lines come first, and every later decision traces back to one of them.

## The five lines

| Line | Answers |
|------|---------|
| **Situation** | Where are we, who is here, and what does their world look like at the start? |
| **Desire** | What does the character want to obtain or reach? |
| **Conflict** | What gets in the way? Where is the tension? |
| **Change** | What shifts? A turning point: an action, an event, or a new way of seeing. |
| **Result** | How does it end? The new reality, and how it differs from the Situation. |

Write each line as one concrete sentence with names, places, and objects rather than themes. Pick a character the audience can root for: in advertising the customer is the hero and the brand is the guide that makes the Change possible; in a creator or founder video it is usually the speaker. Read the five lines alone: they must tell the whole story, and the Result must visibly differ from the Situation.

> **The Lion King.** *Situation:* Simba is a young prince, excited to rule the Pride Lands one day. *Desire:* He wants to prove he is brave and worthy of being king. *Conflict:* After his father's death he runs away, ashamed and afraid to face his past. *Change:* Grown, and pushed by his friends and a vision of his father, he returns to confront Scar. *Result:* He restores balance to the Pride Lands and steps into who he was meant to be.

[Story Craft](references/story-craft.md) holds the test for each line, the craft principles that sharpen it, worked examples, and how other frameworks (Story Spine, StoryBrand, Hero's Journey, Save the Cat) fit inside the five lines.

## Workflow

### 1. Brief

Extract: the subject or product; the one thing the viewer should feel or take away (for an ad, the single-minded proposition); audience; goal; tone; duration, channel, and aspect ratio; mandatories (logo, legal supers, pack shot, CTA, language); brand world and references; budget signals such as location count, cast size, and VFX appetite.

Ask focused questions only when a missing answer changes the script's shape: duration, channel, audience, or the story itself. Otherwise state the assumption under **Brief** in the deliverable and keep going. [Formats](references/formats.md) gives hook windows, beat counts, voiceover word budgets, and platform conventions for each duration and channel.

### 2. Five lines

Write the five lines, then test each one against [Story Craft](references/story-craft.md). When the material already holds a story (a founder's history, a creator's footage, a case study), boil it down to five lines rather than inventing one. When the brief leaves the story open, draft two or three five-line sets with different Conflicts, pick the strongest, and note the others under **Alternatives**.

Done when every line passes its test in Story Craft and the five lines read as a complete story.

### 3. Expand

Grow the five lines into beats without changing them. Expansion adds richness, never a new core; if a beat would need a line to change, rewrite the five lines first and expand again.

| Runtime | Expansion |
|---------|-----------|
| Up to 30s | Five lines straight to beats |
| 45s to 3 min | Ten lines (about two per line), then beats |
| Over 3 min | Twenty lines, grouped into sections, then beats |

Join consecutive beats with *but* or *therefore*, never *and then*: each beat is caused by the one before it or complicates it. Every beat has one job and belongs to one line.

### 4. Treatment

Write the film as prose a director would read: tone, world, who we meet, what happens, what we feel, how it ends. 120–250 words, up to 400 for long-form.

### 5. Frames

Turn each beat into one or more frames using the fields in [Script Format](references/script-format.md). Every frame carries a `Line:` tag naming the line it serves. Write the `Visual:` field to [Visual Description Craft](references/visual-description-craft.md) and the `Shot:` field in standard shot grammar: size, angle, lens, movement ("Slow push-in MCU, 50mm, eye-level").

### 6. Sound and close

Plan audio as an arc across the five lines rather than frame by frame: music and sound design build through the Conflict, turn on the Change, and settle on the Result. Silence is a choice; mark it. Count voiceover words against the budget in [Formats](references/formats.md). The picture alone must still carry the story for viewers watching with the sound off.

Close on the Result. For an ad that means an end frame with pack shot, tagline, CTA, legal supers, and sonic logo, earned by the story instead of bolted on. For creator, founder, and documentary work it is the final image and the line that lands the new reality, ideally mirroring the opening image.

### 7. Trace and critique

Run every check below. Fix what fails and run the check again; never deliver a script with a known failure.

| Check | Passes when |
|-------|-------------|
| **Five-line** | The five lines alone tell the whole story, and the Result differs from the Situation |
| **Trace** | Every frame names its line, every line has at least one frame, and no frame is there only because it looks good |
| **Causality** | Each beat follows from the last by *but* or *therefore* |
| **Hook** | The opening lands inside the channel's hook window and raises a question the audience wants answered |
| **Sound-off** | The story and the takeaway come through with no audio |
| **One idea** | A viewer could sum up the video in one sentence |
| **Specificity** | Two directors handed this script would shoot the same film |
| **Cliché** | No stock imagery: stacked hands, slow-mo high fives, sunset silhouettes, generic uplifting piano |
| **Truth** | The claims and emotions are honest; you would show it to your own family |
| **Budget** | Timecodes add up to the runtime, and voiceover fits at the read pace in Formats |

## Output

One markdown document, in this order. Field conventions, format variants, and a complete 30-second worked example are in [Script Format](references/script-format.md); read it before writing frames.

```markdown
# [Title] | [Brand or channel] | [Duration] | [Aspect ratio]

## Logline
[One sentence: the premise.]

## Five Lines
- **Situation:** [...]
- **Desire:** [...]
- **Conflict:** [...]
- **Change:** [...]
- **Result:** [...]

## Ten Lines
[Only at 45s and up. Twenty lines over 3 min. Each line tagged with the five-line line it expands.]

## Brief
- **Audience:**
- **Takeaway:** [Single-minded proposition for ads]
- **Tone:**
- **Format:** [Duration · channel · aspect ratio]
- **Hook:** [What lands, and by when]
- **Assumptions:** [Anything not given in the brief]

## Treatment
[120–250 words of prose.]

## Sound
- **Music:** [Instrumentation, tempo, and its arc across the five lines]
- **Voiceover:** [Voice profile, read direction, word count against budget]
- **Sound design:** [Posture, signature sounds, planned silences]
- **Sonic logo:** [Ads only]

## Script
[Frame 1 through the final frame, per Script Format.]

## Production Notes
- **Locations:**
- **Cast:**
- **Wardrobe and props:**
- **VFX and graphics:**
- **Mandatories:**

## Alternatives
[Only if other five-line sets were drafted: each in one line, with why it lost.]

## Cutdowns
[Ads only: anchor frames for 15s and 6s cuts, and vertical reframing notes.]
```

## Reference documents

| Reference | Use during |
|-----------|-----------|
| [Story Craft](references/story-craft.md) | Steps 2 and 3: testing each line, expanding 5 → 10 → 20, fitting other frameworks inside the five lines |
| [Formats](references/formats.md) | Steps 1, 3, and 6: durations, hook windows, beat counts, word budgets, platforms, format archetypes |
| [Script Format](references/script-format.md) | Step 5: frame fields and conventions, variants, the worked example |
| [Visual Description Craft](references/visual-description-craft.md) | Step 5: writing visuals a crew can shoot without asking what you meant |

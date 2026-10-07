# video-script

> Writes production-ready video scripts that a team can shoot and cut from, built on a five-line story spine and finished with shot-by-shot frames in filmable prose.

## What it does

`video-script` starts every video from **five lines**: Situation, Desire, Conflict, Change, Result. Filmmaking is a long chain of decisions, and the core of a story gets lost among gear, transitions, voiceover, and grade. Writing the five lines first pins that core down before anything else gets decided.

From there the skill expands the lines (to ten for a minute or two, to twenty for long-form) without changing them, writes a treatment, and turns every beat into frames. Each frame carries shot, visual, on-screen text, voiceover, dialogue, sound effects, music, transition, and a `Line:` tag naming which of the five lines it serves. Before delivery, every frame is traced back to a line, and frames that serve none are cut.

The craft draws on Robert McKee, Blake Snyder, Pixar's story rules and Andrew Stanton, Donald Miller's StoryBrand, the Heath brothers' *Made to Stick*, Luke Sullivan, David Ogilvy, Ira Glass, Trey Parker and Matt Stone's "but / therefore" rule, and Walter Murch on cutting. All of it is organized by which of the five lines it sharpens.

## When to use it

- *"Write a 30-second spot for our cold-brew launch."*
- *"Script my next YouTube video about quitting my agency job."*
- *"Turn this founder interview into a 90-second brand film."*
- *"Give me three 15s TikTok concepts for this app."*
- *"I have hours of footage and no idea what the story is."*

Use [`creative-director`](../creative-director/) first when the brand's visual world isn't defined yet. Hand the finished script to [`video-production`](../video-production/) to make the video.

## Example

**Prompt**

> 30s spot for Riverside Coffee, a delivery service for new parents in dense cities. Warm, observational, real rather than aspirational. Insight: new parents have no free hands before the baby falls back asleep.

**Five lines**

- **Situation:** At 4:47 a.m., Maya, a new mother in a one-bedroom city apartment, rocks her newborn back to sleep.
- **Desire:** She wants one small thing for herself: a real coffee.
- **Conflict:** Her arms are full, the kitchen is too far, and the baby wakes at the slightest sound.
- **Change:** One thumb-tap on a saved order, and across the dark city a cyclist and a barista start moving for her.
- **Result:** She opens the door to a steaming cup with a marker sun on the lid, the baby asleep on her chest, and takes the first sip of a morning that is hers.

**One of the ten frames**

> **Frame 3** — `00:06–00:09`
> **Line:** Desire, into Conflict
> **Shot:** OTS from behind Maya, 50mm, locked off; focus racks from her shoulder to the kitchen doorway and back.
> **Visual:** Through the bedroom doorway, across the dark galley kitchen, the coffee machine sits cold, its carafe empty. Maya leans forward to stand. The baby stirs and lets out a thin whimper. She freezes, then sinks back onto the bed and resumes the sway, eyes still on the machine.
> **SFX:** Bedsprings creak. The whimper, small and sharp.
> **Music:** The piano stops for the length of the whimper, then resumes.

The full script is in [`references/script-format.md`](references/script-format.md).

## Installation

```bash
npx skills add thatjuan/agent-skills --skill video-script
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The five lines, the seven-step workflow, the critique checks, and the output skeleton |
| `references/story-craft.md` | Tests and craft for each line, worked examples, the 5 → 10 → 20 expansion, and other frameworks mapped onto the five lines |
| `references/formats.md` | Durations, hook windows, beat counts, word budgets, platforms, and format archetypes |
| `references/script-format.md` | Frame schema, field conventions, variants (creator, anthem, demo, documentary, episodic), and a full 30s worked example |
| `references/visual-description-craft.md` | Writing visuals specific enough that every department pictures the same frame |

## Tips

- **Bring the story if you have one.** A founder's history, a creator's journey, or interview transcripts give the skill real material to boil down to five lines.
- **Give duration and channel up front.** They decide the expansion depth, hook window, and word budget.
- **Push back on the five lines first.** Changing a line is cheap before any frames exist and expensive after.
- **Reuse the five lines in production.** When the edit sprawls, check each scene against them.

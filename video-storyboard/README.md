# video-storyboard

> World-class video storyboard writer for marketing, advertising, brand films, social spots, and product videos. Produces an all-text markdown storyboard — every frame is described in rich, filmable prose instead of drawn.

## What it does

`video-storyboard` plays the role of a senior creative + director hybrid at a top-tier ad agency. It doesn't sketch frames — it **writes them in language so specific that a director, DP, casting director, and stylist can converge on the same picture**. Given a brief, it produces a complete production-ready storyboard: logline, treatment, audio architecture, frame-by-frame breakdown with shot, action, on-screen text, voiceover, dialogue, SFX, music, and transitions, plus production notes and cutdown anchors.

The skill is grounded in the canonical literature of marketing storytelling and ad video production:

- **Donald Miller** — *Building a StoryBrand* (the customer is the hero, the brand is the guide)
- **Joseph Campbell / Christopher Vogler** — *The Hero's Journey / The Writer's Journey*
- **Blake Snyder** — *Save the Cat!* (15-beat structure)
- **Pixar / Emma Coats** — 22 Rules of Storytelling, including the Story Spine
- **Chip & Dan Heath** — *Made to Stick* (the SUCCESs framework)
- **Luke Sullivan** — *Hey, Whipple, Squeeze This*
- **David Ogilvy** — *Ogilvy on Advertising*
- **Giuseppe Cristiano** — *The Storyboard Artist*
- **Robert McKee** — *Story* / *Dialogue*
- **Annette Simmons** — *The Story Factor*

It also packs the working vocabulary of the craft — shot sizes, lensing, camera movement, lighting, color grading, transitions, audio terminology, on-screen graphics — so descriptions are precise enough to shoot from.

## When to use it

Invoke this skill when the user wants a **storyboard or video concept written down**, not drawn:

- *"Storyboard a 30-second TV spot for a sustainable mattress brand."*
- *"Write a 60s YouTube pre-roll for our Series A launch."*
- *"Concept three different 15s TikTok ads for a new cold-brew SKU."*
- *"Treatment + frames for a 90s brand film about our founder's origin story."*
- *"Storyboard a product demo video for our developer tool."*
- *"I have a brief — give me a shot-by-shot for a 60s anthem spot."*

**Not the right skill if** the user wants visual mockups (→ `stitch-design`), brand identity thinking (→ `creative-director`), or actual video production. This is the upstream creative + director's deliverable that production teams shoot from.

## Example walkthrough

**Prompt**

> Storyboard a 30-second spot for Riverside Coffee — a coffee delivery service for new parents in dense cities. Tone is warm, observational, real-not-aspirational. Insight: new parents don't have hands free to order anything before the baby is back asleep.

**What the skill does**

1. **Brief intake** — names the audience (parents of newborns/under-twos), single-minded proposition (*Riverside delivers your coffee before you remember you wanted it*), tone, format, mandatories.

2. **Story setup** — casts the parent as the hero, the brand as the guide, picks the **Pixar Story Spine** as the narrative skeleton, runs it through the SUCCESs filter, locks the conflict ("4:47am, no hands free, exhausted").

3. **Treatment** — 200 words of director-readable prose describing the spot from cold open to end frame.

4. **Beat map** — 9 beats sized to 30 seconds, plus an end card.

5. **Frame-by-frame storyboard** — each frame written like:

   > **Frame 2** — `00:03–00:07`
   > **Shot:** Slow push-in MS, handheld, 35mm.
   > **Visual:** *Maya, late 20s,* sits on the edge of an unmade bed in an oversized cardigan over an old t-shirt, sock-feet on a rug. She holds her newborn against her shoulder, swaying. Hair half-up with a clip. Single warm bedside-lamp practical, the rest of the room blue moonlight from a sheer-curtained window. She's not smiling. She's not frowning. She's just *there* — the specific exhaustion of being needed by someone who can't say thank you yet.
   > **SFX:** Baby's snuffly breathing. A single car passing far below.
   > **Music:** Piano adds a second note.
   > **Transition:** Hard cut on a sway.
   > **Note:** "Save the cat" — we are with her in three seconds.

6. **Audio architecture** — music posture, V/O voice profile and word budget, SFX strategy, sonic logo.

7. **Production notes** — locations, casting briefs, wardrobe, props, VFX, mandatories.

8. **Cutdown notes** — anchor frames for the 15s and 6s versions, and reframing notes for vertical 9:16.

9. **Self-critique pass** — runs the boards through the sound-off test, the six-second test, the one-idea test, the conflict test, the cliché test, and Ogilvy's truth test before delivery.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill video-storyboard
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The 8-phase storyboard generation workflow and output format spec |
| `references/storytelling-canon.md` | Distilled frameworks from StoryBrand, Hero's Journey, Save the Cat, Pixar 22, Made to Stick, Hey Whipple, Ogilvy, Cristiano, McKee, Simmons |
| `references/ad-formats.md` | Duration-specific beat counts and platform conventions (TV, YouTube, IG/TikTok, OOH, cinema, UGC, demo, anthem, episodic) |
| `references/shot-language.md` | Shot sizes, angles, lensing, camera movement, lighting, color, transitions, audio terminology, on-screen graphics |
| `references/visual-description-craft.md` | How to write rich, specific, filmable prose — the six dimensions, specificity ladder, sensory layering, casting/wardrobe/location/light, common failure modes |
| `references/storyboard-format.md` | Exact markdown output spec with a complete 30s worked example |

## Tips

- **Feed it a rich brief.** Like all creative skills, this one scales with input quality. A vague prompt produces a vague spot. Specific audience, insight, tone reference, channel, and duration unlock real craft.
- **Specify the duration up front.** A 6s bumper, a 30s broadcast spot, and a 90s hero film are structurally different animals — the skill picks a different narrative skeleton for each.
- **Name the channel.** TV, YouTube pre-roll, TikTok, and cinema each have different hook windows, sound-on/off assumptions, aspect ratios, and end-frame conventions.
- **Tone references help.** "Tonally like *The Bear*" or "the dry warmth of an early Spike Jonze MTV bumper" give the skill texture to grade against.
- **Ask for the rationale.** Every frame has a director's-eye `Note:` field — push for it. The *why* of a frame is often more useful than the frame itself when defending the work.
- **Ask for cutdowns.** Spots ship as suites — 30s + 15s + 6s + vertical. The skill can flag which frames carry which cutdown.
- **Pair with `creative-director`** when the brand identity isn't locked yet — get the visual world established first, then storyboard inside it.

## Related skills

- [`creative-director`](../creative-director/) — upstream brand and visual-world thinking before the spot
- [`logo-studio`](../logo-studio/) — for end-frame logo and sonic-logo design counterparts
- [`stitch-design`](https://github.com/...) — for frame-grab stills if visual mockups are needed

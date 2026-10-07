# Assembly

Contact sheets, the edit, overlays, captions, rendering, and QC. `scripts/assemble.py` does the rendering; its docstring is the `edit.json` schema.

## Contents

- [Contact sheets](#contact-sheets)
- [The edit](#the-edit)
- [Supers, end cards, and captions](#supers-end-cards-and-captions)
- [Render](#render)
- [QC](#qc)
- [Cutdowns and other ratios](#cutdowns-and-other-ratios)

---

## Contact sheets

For the checkpoint, tile the bible and keyframes in shot order. Each tile is labeled by its position in the list, because this ffmpeg may lack `drawtext`. Write the order next to the sheet when you show it.

```bash
# stills → one sheet (glob order = shot order, so name files s01-, s02-, …)
ffmpeg -y -pattern_type glob -i 'keyframes/*-first.png' \
  -vf "scale=480:-2:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2,tile=4x4:padding=6:color=white" \
  -frames:v 1 review/keyframes-sheet.jpg
# a finished cut → one tile every 2 s
ffmpeg -y -i out/final.mp4 -vf "fps=1/2,scale=480:-1,tile=5x4" -frames:v 1 review/final-sheet.jpg
```

Adjust the tile grid to the count; more than 20 tiles per sheet gets too small to judge, so split into several sheets.

## The edit

Build `edit.json` from `plan.json`:

- **Clips** in script order, using each shot's `selected` take. Set `in`/`out` to trim the handles: start where the motion is already under way, end before it settles. Check with frame grabs at the planned points.
- **Transitions** come from the script's Transition field. As in the script, the transition belongs to the outgoing clip: `"cut"` (default), `{"type": "dissolve", "duration": 0.5}`, `{"type": "dip", "duration": 0.4}` (through black), or any ffmpeg `xfade` name (`wipeleft`, `slideup`, `circleopen`…). A whip pan is usually generated into the shots themselves; join them with a cut or a very short `fade`. J- and L-cuts are audio offsets: anchor the next shot's sound a little before its clip starts (`"at": "s05-0.4"`).
- **Audio** anchors to clip ids (`"at": "s03+0.25"`), so trimming a clip doesn't knock voice or effects out of sync. Use absolute seconds only for tracks that span the film (music, an overall bed).
- **Stills** (an end card, a pack shot from the image model) are clips with a `duration`.

```bash
python3 <skill-dir>/scripts/assemble.py edit.json --timeline   # clip starts, transitions, runtime
```

**Runtime tolerance:** within ±0.5 s of the script for spots of 60 s or less, ±2% for longer pieces. Fix the timing with trims, not by speeding up clips.

**Rough cut first.** Before music and effects, render picture plus voice (`audio` holding only voice entries) and review it: a final-sheet contact sheet, frame grabs at every cut, and the timeline numbers against each line's shot. This is picture lock.

## Supers, end cards, and captions

On-screen text is never generated into the video frames. It is composited in post, so it stays sharp, correct, and editable.

**Supers and end-card type** are PNGs with alpha placed through `overlays` (position with `x`/`y` expressions using `W`, `H`, `w`, `h`; `fade` in seconds). Make them with any of:

- the image model with a transparent-background option, for designed typography and logo lockups, at the delivery resolution;
- HTML/CSS rendered to a transparent PNG with a headless browser, for exact fonts and brand type;
- the `hyperframes` skill, when the piece needs animated or kinetic type, designed captions, or motion graphics. It composes HTML, takes the generated clips and the mix as media, and renders the final, so `assemble.py` is used only for the rough cut.

Check the script's On-Screen text against the overlays word for word, including legal supers.

**Captions**: build an SRT from the voice timestamps (the `/with-timestamps` responses, offset by each line's timeline start from `--timeline`), at no more than 2 lines and about 42 characters per line. Attach it as a soft subtitle track:

```bash
ffmpeg -y -i out/final.mp4 -i out/captions.srt -map 0 -map 1 -c copy -c:s mov_text -metadata:s:s:0 language=eng out/final-captioned.mp4
```

For burned-in captions (most social placements), render caption PNGs as overlays, or finish in `hyperframes`.

## Render

```bash
python3 <skill-dir>/scripts/assemble.py edit.json            # renders edit.output
python3 <skill-dir>/scripts/assemble.py edit.json --dry-run  # prints the ffmpeg command and filter graph
```

The renderer scales and crops every clip to `size`, conforms to `fps`, places every audio track, ducks music under voice, normalizes to `loudness`, and encodes H.264/AAC with fast start. When ffmpeg fails, read the `--dry-run` graph for the failing label: usually a missing audio stream (`keep_audio` on a silent clip) or a timing anchor that resolved outside the timeline.

## QC

Run every check on the final render, fix what fails, and render again:

| Check | How |
|-------|-----|
| Runtime and format | `ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact out/final.mp4` matches the script's format |
| Loudness | `ffmpeg -nostats -i out/final.mp4 -af ebur128=peak=true -f null - 2>&1 \| sed -n '/Summary/,$p'`: integrated within ±1 LU of the target, true peak ≤ −1 dBTP |
| No unintended black or freezes | `ffmpeg -i out/final.mp4 -vf "blackdetect=d=0.2,freezedetect=n=0.003:d=1" -an -f null - 2>&1 \| grep -E "black_start\|freeze_start"`: only where the script calls for it |
| Cuts | Frame grabs 2 frames either side of every cut: no flash frames, matching screen direction, chained shots continuous |
| Sync | Each voice line lands on its shot, and each hero SFX on its action (frame grab at the cue time) |
| Hook | The first frame and the first 2 s match the script's hook; the opening frame isn't a fade-in from black unless scripted |
| Text | Every On-Screen element is present, correctly spelled, inside title-safe margins (5% of the frame), and readable for its duration |
| End | The end card holds long enough to read the CTA aloud twice, and music resolves under it |
| Final watch | A contact sheet of the whole cut, read in full: the five lines still read as a story with the sound off |

## Cutdowns and other ratios

For a vertical or square version, reframing generated 16:9 shots by crop rarely holds composition. Where the script lists other ratios, plan for them at the breakdown: generate keyframes and takes natively at each ratio for hero shots, and crop only the shots whose subjects sit centered. Cutdowns (15 s, 6 s) are new `edit.json` files built from the script's Cutdowns anchor frames, reusing the same takes and audio.

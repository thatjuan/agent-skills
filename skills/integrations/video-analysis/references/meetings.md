# Meeting recordings

Details for `screens`. The workflow itself is step 4 of `SKILL.md`.

## Transcript formats

`--transcript` reads:

- **WebVTT and SRT cues.** Zoom writes `Name: text`, Teams writes `<v Name>text</v>`. Each line takes its cue's start time.
- **Text with a time near the start of a line.** Examples are `[00:12:03] Ana: ...`, `00:12:03 Ana: ...`, and `10:32:15 AM Ana: ...` (PM adds 12 hours). Otter puts a header like `Ana Lopez  12:03` with the words on the lines below. Meet puts a bare `00:05:12` line with `Name: text` lines under it. A line without a time joins the timed line above it. A new `Name:` line inside a block becomes its own line at the block's time.
- **`transcript.md` from `video-transcript`.** Its metadata header is skipped.

Convert anything else to one of these first, with the time at the start of each line. That covers `.docx`, PDF, and JSON from a notetaker's API. A time like `12:03` reads as minutes and seconds. A notetaker that prints only hours and minutes (`10:32 AM`) places a line within its minute and no closer. Use it to locate, then survey that minute with `sheet`.

## Finding the offset

`offset = video time of a moment − transcript time of the same moment`. Pass it as `--offset=-10:30:00`, with the `=`, because the value starts with a minus sign.

- Zoom names cloud recordings like `GMT20251106-153012_Recording_1920x1080.mp4`, so this one started at 15:30:12 UTC. Convert that time into the transcript's time zone before using it. In New York in November, 15:30:12 UTC is 10:30:12, so the offset is `-10:30:12`. When you don't know the transcript's time zone, don't guess it from the filename; use an anchor.
- Otherwise anchor on a moment you can see. "Can you see my screen?" matches the frame where the share appears; find it with `sheet --every 2` around the expected spot. A slide title said aloud matches the screen that shows it.
- Confirm the offset on one anchor, then check a second anchor late in the call. A wall-clock transcript keeps counting while a recording is paused, so every line after a pause is late by the pause's length. When the anchors disagree, run `screens` once per segment with `--from`/`--to`, giving each its own offset and `--out`.

## Layouts

- **Zoom** records the share with the active speaker or a strip of video tiles beside or above it, depending on the recording settings. Cloud recordings can also save shared-screen-only, speaker, and gallery files separately. A local recording is a single composite.
- **Teams and Meet** show the share large, with participant tiles along one edge.
- Whatever the layout, crop to the share and leave out anything that moves on its own. When a thumbnail overlaps the share, crop the largest rectangle that misses it.
- The presenter's screen may not fill the share area, for example a 16:10 or ultrawide screen letterboxed inside it. The `cropdetect` recipe in `ffmpeg-recipes.md` finds the active picture.
- When the layout changes mid-call (someone starts or stops sharing, or a second presenter shares), one crop no longer fits. Run `screens` over each share's span with `--from`/`--to`. With nobody sharing, the screens are just speaker switches.

## Tuning

- **Too many screens.** Compression noise or something moving inside the crop, such as a clock, an animated logo, or a GIF on a slide. Use `--noise -55` (or `-50`), tighten the crop, or raise `--shortest` to 4.
- **Too few.** Two slides merged, or a build step missed. Use `--noise -65` (or `-70`), and `--shortest 1` when the presenter clicks through slides quickly.
- **A live edit in a spreadsheet or document.** A single changed cell can stay under -60 dB. Use `-70`, or burst the span with `frames --every`.

## What users usually want

- **Notes with the screens.** Under each topic, give the frame of the screen it was discussed on and a summary of what was said. Copy the chosen frames into the user's folder with names that describe them (`03-pricing.jpg`).
- **The slide where X came up.** Search `screens.md` for X, then answer with that screen's time range and frame.
- **Every slide as a deck.** Take the settled frames of the screens not marked `moving`, and drop repeats where a slide was shown twice. When ImageMagick is installed, `magick s*.jpg slides.pdf` builds a PDF.

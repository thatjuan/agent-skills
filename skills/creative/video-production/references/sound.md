# Sound

Voice, dialogue, sound effects, ambience, and music on ElevenLabs, plus mix targets. Voice comes first, because it sets the timing; everything else is made to the locked picture.

All calls use `https://api.elevenlabs.io` with `-H "xi-api-key: $ELEVENLABS_API_KEY"`. Most return audio bytes, so write the body to a file and use `--fail-with-body` so an error doesn't land on disk as an `.mp3`:

```bash
curl -sS --fail-with-body -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID?output_format=mp3_44100_192" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d @requests/vo01.json -o audio/vo/vo01.mp3
```

Pass `model_id` on every request. Endpoint defaults point at older models. Read each endpoint's page (`https://elevenlabs.io/docs/api-reference/<area>/<op>.md`) before first use, as [Model Discovery](model-discovery.md) describes.

## Contents

- [Voices](#voices)
- [Voiceover](#voiceover)
- [Dialogue](#dialogue)
- [Retiming the shots](#retiming-the-shots)
- [Sound effects and ambience](#sound-effects-and-ambience)
- [Music](#music)
- [Mix targets](#mix-targets)

---

## Voices

Each speaker in the script (the V/O voice and every character who talks) gets one voice for the whole film, recorded in the bible.

1. **Search** the account's voices and the library: `GET /v2/voices?search=<terms>&page_size=50`, filtering by `gender`, `age`, `accent`, `language`, and `use_cases`. Build search terms from the script's voice profile ("woman, late 30s, warm, dry, slight rasp").
2. **Design** when nothing fits: `POST /v1/text-to-voice/design` with a detailed `voice_description` (age, gender, accent, timbre, pace, attitude) and a sample `text` in the character's register. It returns previews with a `generated_voice_id`. Pick one, then save it as a voice through the create-voice endpoint named on that page.
3. **Audition.** Generate the character's hardest line with the two best candidates and listen through the measured result: duration, and whether the tags landed. ElevenLabs often clones from the source closely, flaws included, so pick a clean voice.

Never clone a real person's voice without their consent.

## Voiceover

- **One file per line**, so the edit can move lines independently. Name files by line id (`vo01.mp3`) and record them in `plan.json → voice`.
- **Direction as audio tags.** Turn the script's read direction into tags at the start of the line or before the phrase it governs: `[warm, dry] You don't have to ask. [beat] We're already on the way.` Use tags that describe the voice ("[low, gravelly]", "[whispering]") so the model doesn't read them as sound-effect cues. Pauses come from tags, ellipses, and punctuation; some current models ignore SSML break tags.
- **Continuity across lines.** When lines are read in sequence, pass `previous_text` / `next_text` (or the previous request ids) so the intonation flows from line to line.
- **Captions.** Use the `/with-timestamps` variant of text-to-speech. It returns character-level timing alongside base64 audio; keep the JSON for building captions (see [Assembly](assembly.md)).
- **Stability.** Lower stability gives a more expressive, varied read; raise it when lines must sound like one continuous session.

## Dialogue

For a back-and-forth between characters, `POST /v1/text-to-dialogue` with `inputs: [{text, voice_id}, …]` gives natural turn-taking and reactions that separate TTS calls don't. Use the speech model chosen in step 1 and include audio tags per line. Then:

- If the scene plays across several shots, split the file at the turn boundaries (`ffmpeg -ss … -to …`, with timestamps from the `/with-timestamps` variant), one file per line, so each line can anchor to its own shot.
- If the scene plays in one shot, keep one file and anchor it to that shot.

For dialogue a video model will lip-sync, see [Shot Generation](shot-generation.md). Converting a clip's native speech into a character's voice uses `POST /v1/speech-to-speech/{voice_id}` (multipart `audio` file plus `model_id` from the speech-to-speech family).

## Retiming the shots

Measure every line:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 audio/vo/vo01.mp3
```

A shot carrying a line needs `cut_duration ≥ line duration + about 0.3 s` of air, more before a cut on a landing line. When a line runs long, stretch the shot (up to the model limit), split it, or tighten the copy with the user. Don't speed up the read. Update `cut_duration` and `gen_duration` in `plan.json` before the bible step.

## Sound effects and ambience

After picture lock, for each cue in the script's SFX fields:

- `POST /v1/sound-generation` with `text`, `model_id`, `duration_seconds` set to the length of the moment, and `prompt_influence` around 0.5–0.7 for literal cues (lower it for designed or abstract sounds).
- **Prompt** with the source, the material, the action, the space, and the distance: "small bedsprings creak, close, in a quiet carpeted room", "single cleat clicking into a bike pedal, crisp, outdoors at dawn". Sequences work: "footsteps on wet asphalt, then a car door shuts".
- **Ambience beds**: one per location, `loop: true`, up to 30 s per generation, repeated in the edit (`edit.json` takes several entries, or pre-loop it with `ffmpeg -stream_loop`). Room tone under every scene keeps cuts from sounding dead.
- **Designed hits** use audio vocabulary: impact, whoosh, riser, braam, drone, glitch, sub drop.
- **Sonic logo**: a short sound effect or a music generation of 3–4 s, auditioned like a voice.
- Anchor each cue in `edit.json` to its clip id with an offset matched to the action on screen. Find the frame with a frame grab at the planned time.

Generate two variants of hero cues in one turn and pick by ear: duration, transient, and fit with the music.

## Music

Make the score to the locked cut. Two routes:

**A. Composition plan**: the default when the script specifies the music's arc (it usually does: "builds through the Conflict, turns on the Change").

1. Map the script's sound arc onto **chunks** at the locked cut's section boundaries. A typical spot has one chunk per five-line line, each with `duration_ms` taken from the edit timeline (the minimum and maximum chunk lengths are on the compose page). The chunks sum to the runtime plus a 1–2 s tail.
2. Each chunk gets `text` (a section label such as `[Intro]`, or lyrics), `positive_styles` (instrumentation, tempo in BPM, key, energy, production; six or more on the first chunk, which sets the genre), `negative_styles` (include "vocals" for an instrumental chunk), and `context_adherence`.
3. `POST /v1/music` with `model_id` and `composition_plan`. To start from a prompt and refine, `POST /v1/music/plan` drafts a plan you can edit.

**B. Video-to-music**: the fast route when the arc is loose. Render the locked cut without music (picture plus voice) and send it to `POST /v1/music/video-to-music` (multipart `videos`, plus `description`, `tags`, and `model_id`). The music follows the cut's pacing.

Either way, listen through the result against the cut: the music should change where the picture changes, sit under the voice, and resolve with the end card. Silence the script calls for stays silent: cut the music there in `edit.json` with an `out` point and a fade instead of asking the model for silence.

## Mix targets

`assemble.py` buses voice, music, and effects, ducks music under voice, and normalizes the result. Set per-track `gain_db` so that, before normalization:

| Layer | Relative level |
|-------|----------------|
| Voice, dialogue | 0 dB, the reference |
| Hero SFX | −3 to −6 dB |
| Music under voice | −8 to −12 dB (ducking takes it lower while voice plays) |
| Music alone | −2 to −4 dB |
| Ambience beds | −18 to −24 dB |

Set the final integrated loudness with `edit.json → loudness`: −14 LUFS for web and social, −16 for podcasts and spoken-word platforms, −23 for EBU R128 broadcast, −24 for ATSC A/85. True peak is capped at −1.5 dBTP.

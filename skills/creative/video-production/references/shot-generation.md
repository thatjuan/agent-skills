# Shot Generation

How to turn approved keyframes into takes: choosing a mode, writing the motion prompt, handling dialogue, reviewing takes, and recovering from failures.

## Contents

- [Modes](#modes)
- [Motion prompts](#motion-prompts)
- [Dialogue and lip sync](#dialogue-and-lip-sync)
- [Running generations](#running-generations)
- [Reviewing a take](#reviewing-a-take)
- [The retry ladder](#the-retry-ladder)
- [Finishing passes](#finishing-passes)

---

## Modes

Each shot has one mode. Check the chosen model's schema for what it supports: many models refuse keyframes and unpositioned references in the same request.

| Mode | Anchors | Use when |
|------|---------|----------|
| `first` | First-frame keyframe | Default. Composition, identity, and light are locked at frame one; the prompt supplies motion. |
| `first_last` | First and last keyframes | The shot has to land somewhere exact: a reveal, a transformation, a match cut out, or a handoff into a chain. |
| `reference` | Character sheets, location plate, and props as unpositioned references; no keyframe | Characters enter, interact, or move a lot, and a fixed first frame would make the shot static or impossible; or two or more characters must hold identity together. The prompt carries the composition, so write the Shot field into it in full. |
| `extend` | A selected take | A continuous shot longer than the model's maximum: extend the take with a continuation prompt, using a video-to-video extend mode where the model has one. |
| `performance` | Character image plus a performance video | A real human performance (face, timing, gesture) should drive a generated character. Runway's character-performance endpoint; the face must stay in frame. |
| `avatar` | A Runway avatar | A presenter talking to camera for a stretch, driven by text or by an ElevenLabs audio file. |

To fix a detail in an otherwise good take (a wrong object, a flicker, a sign), use a video-editing model's edit mode on that take instead of regenerating it.

## Motion prompts

The keyframe already shows what is in the shot. The motion prompt says **what changes**.

- **One primary action**, stated concretely with its pace: "She sets the cup down slowly and lets go."
- **One camera behavior**, in shot grammar: "slow push-in", "locked off", "handheld drift", "orbit left 30°", "crane up". Say "camera locked off" when it shouldn't move; models add motion by default.
- **Secondary motion** that makes the frame live: steam, curtains, traffic, breathing, light flicker.
- **Descriptors** for the characters and the location, pasted verbatim from the bible, plus the style descriptor. With tagged references, use the tags the model expects.
- **Positive phrasing.** Describe what happens ("her face stays calm"), not what shouldn't happen. Use a dedicated negative-prompt field only where the schema has one.
- **Time order for longer shots.** On models with long prompt limits, give beats in sequence with timing words: "For the first two seconds… then… as the camera settles…".
- **Fit the length.** Use the model's prompt limit as a ceiling, not a target. Short models want one tight paragraph.

Turn native audio **off** (`audio: false`) whenever the schema allows and you are scoring in post, which is the default here. It is often cheaper, and generated room tone fights the mix. Leave it on only for a shot whose generated audio you plan to keep (see Dialogue).

## Dialogue and lip sync

On-screen speech is the least stable part of generated video. In order of preference:

1. **Stage it out of lips.** Over-the-shoulder from behind, a wide, a cutaway to the listener, or the line moved to V/O. Often the better craft choice anyway, and noted at breakdown.
2. **Audio-driven generation.** Generate the line on ElevenLabs first, then pass it as an audio reference to a video model whose docs say audio references drive the speech or performance. Check that the model actually lip-syncs to the reference: generate one short test before committing a scene. Keep the ElevenLabs file as the master in the mix, aligned at the same start time.
3. **Native speech, then voice conversion.** A model that speaks dialogue written in its prompt gives good lip sync but a random voice. Extract the clip's audio and convert it to the character's ElevenLabs voice with speech-to-speech; timing and lip sync survive and the voice matches every other shot. Mix the converted file and drop the clip's own audio.
4. **Performance transfer.** Record or source a reference performance video of the line and drive the character with the character-performance endpoint.

For multi-line exchanges, generate the whole exchange with text-to-dialogue (see [Sound](sound.md)), split it per line where shots cut, and reference each line in its own shot.

## Running generations

**Request bodies** are JSON files under `production/<slug>/requests/`, one per take, built from the model's schema. `runway.py` uploads any `"local:<path>"` value (relative to the body file) and swaps in the `runway://` URI. The shape below is only an illustration; field names and allowed values come from the schema you read in step 1.

```json
{
  "model": "<video model id>",
  "promptImage": [ { "uri": "local:../keyframes/s02-first.png", "position": "first" } ],
  "promptText": "<motion prompt>",
  "ratio": "<exact allowed ratio>",
  "duration": 4,
  "audio": false,
  "seed": 78
}
```

```bash
R=<skill-dir>/scripts/runway.py
python3 $R run /v1/image_to_video requests/s02-t2.json --out clips/s02-t2.mp4     # submit, wait, download
python3 $R submit /v1/image_to_video requests/s03-t1.json                        # fire several, then:
python3 $R wait <task-id> --out clips/s03-t1.mp4
```

- **Parallelize.** Submit every independent shot in one turn (several `submit` calls, or `run` calls as background jobs), then wait. A `THROTTLED` task is queued, not failed. Chained shots wait for their predecessor's selected take.
- **Draft, then final.** When the final model has a draft tier, render drafts of every shot first, review them, and enhance only the approved drafts. The enhance request reuses the draft's prompt and seed, so the final matches what was approved. Without a draft tier, draft on a cheaper sibling model to check motion and prompt, then run the final model with the same prompt.
- **Takes.** One final take per shot by default, two for hero shots (the hook, the Change, the end frame). More than three attempts at one shot means the shot needs rethinking (see the ladder).
- Record every take in `plan.json` (task id, seed, file, cost, the one change from the previous take) as it lands.

## Reviewing a take

Make a contact sheet and Read it, then grab the frames that matter:

```bash
ffmpeg -y -i clips/s02-t2.mp4 -vf "fps=3,scale=480:-1,tile=4x3" -frames:v 1 review/s02-t2-sheet.jpg
ffmpeg -y -ss 0 -i clips/s02-t2.mp4 -frames:v 1 review/s02-t2-in.jpg
ffmpeg -y -sseof -0.1 -i clips/s02-t2.mp4 -frames:v 1 review/s02-t2-out.jpg
```

Use a frame rate that gives at least 8 tiles for the clip's length. Check:

- **Identity holds for the whole clip.** Faces, hair, and wardrobe on the last tiles match the first.
- **No morphing.** Objects, limbs, and backgrounds keep their shape; nothing appears or melts away.
- **The action and camera match the prompt and the script's Shot field**, at the intended pace.
- **Physics.** Weight, contact, and liquids behave; hands hold things.
- **Clean in and out points** within the cut range, with no blur or settling inside the part that plays.
- **Screen direction and eyelines** agree with the neighboring shots.
- **No unwanted text**, watermarks, or flashes.

## The retry ladder

When a take fails, climb one rung at a time and change one thing per attempt:

1. **Prompt.** Tighten the motion prompt where the take went wrong: slow the action, name the camera move, re-state the descriptor.
2. **Seed.** Same request, new seed.
3. **Anchors.** Fix the keyframe (it often causes the failure), add a last frame, or switch between `first` and `reference` modes.
4. **Model.** Move to the fallback video model, rebuilding the body from its schema.
5. **Shot.** Simplify: a shorter duration, a smaller action, a tighter size, or cover the beat with a cutaway or insert. Tell the user when a script beat has to change.

Content-moderation failures skip the ladder: rewrite the prompt and anchors to remove whatever tripped the filter, because resubmitting a moderated request costs credits and risks the account.

## Finishing passes

Only on selected takes, only when the delivery needs it, and costed at the checkpoint:

- **Upscale** a take rendered below the delivery resolution with a video upscaler.
- **Frame rate**: interpolate when takes come in at a frame rate other than the delivery's and the motion judders after conversion.

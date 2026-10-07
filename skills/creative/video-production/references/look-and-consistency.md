# Look and Consistency

How to build the bible and the keyframes so that every shot looks like the same film, with the same people in the same places.

## Contents

- [Why stills first](#why-stills-first)
- [The bible](#the-bible)
- [Keyframes](#keyframes)
- [Chains](#chains)
- [Still checklists](#still-checklists)

---

## Why stills first

Video models are good at motion and bad at remembering. Given a first frame, they keep that frame's people, light, and layout for the length of the shot. Given only text, they invent new ones every time. Stills are also cheap enough to iterate on, so taste gets made at the still stage and video spend goes only to approved images.

Use one image model for every still in the production (see [Model Discovery](model-discovery.md)).

## The bible

Build in this order; each item is a reference for the next.

### 1. Style frame

One image that sets the look: grade, contrast, lens feel, grain, palette, light quality. Compose a representative wide shot from the script (usually the opening situation) and iterate until it looks like the film. Write its **descriptor**: one line naming the look in concrete terms ("pre-dawn blue-black, single warm practicals, 35mm grain, soft halation"). From now on, the style frame goes into every image request as a reference, and the descriptor goes into every prompt.

### 2. Character sheets

For each recurring character:

1. **Portrait first.** A front-facing, chest-up portrait on a plain mid-grey background, with even soft light and a neutral expression, in the scene wardrobe. Prompt from the script's Visual description plus the style descriptor. Generate several candidates in one call when the model allows, pick the one that fits the script best, and iterate on that one. This portrait is the identity.
2. **Derive the rest by editing from the portrait**, with the portrait attached as a reference (flagged as a human subject when the model supports it): a full-body shot in wardrobe, a three-quarter view, and a profile. Add expressions or poses the script needs (laughing, crying, mid-stride) the same way. Never generate a sheet image from text alone; identity drifts between independent generations.
3. **Wardrobe changes** are new sheet images edited from the portrait, recorded as a separate entry (`maya-robe`), so each shot names exactly which look it uses.
4. Write the character's **descriptor**: age, two or three distinctive facial features, hair, and the exact wardrobe. Use it verbatim in every prompt. Give the character a **tag** (3–16 letters, digits, or underscores, starting with a letter) for models that address references by tag in the prompt.

Children, animals, and stylized characters follow the same steps. For a product, use a real photograph as the portrait whenever one exists.

### 3. Location plates

For each location, an empty establishing frame at the **target aspect ratio**, at the time of day and in the light the script calls for, with the style frame as a reference. Derive other angles of the same room by editing from the plate ("the same room seen from the doorway, looking toward the window") rather than generating them independently. Note the light direction in the descriptor ("warm lamp camera-left"), because keyframes have to keep it.

### 4. Props

Hero props (the product, the cup with the sun) get their own reference image on a plain background. Product shots must use real product photos as references so labels and shapes stay correct.

## Keyframes

A keyframe is the **first frame of the shot as it begins**, not the shot's best moment. The video model animates forward from it, so compose for where the action starts and leave room for where it goes: if the camera pushes in, frame wider than the shot's end size, and if a character walks in from the right, start with them at the edge or out of frame.

**Request.** One image request per keyframe:

- References, in priority order: character sheets for everyone in frame (the portrait plus the closest-matching angle), the location plate, prop references, then the style frame. Stay within the model's reference limit, and drop the style frame before you drop an identity reference.
- Prompt structure: shot grammar from the script's Shot field (size, angle, lens) → who is in frame, by descriptor and tag, doing what, and where in the frame → location descriptor → light and time → style descriptor. Use positive phrasing: describe what should be there.
- Ratio: the **exact** ratio the video model will render at. Mismatched keyframes either get center-cropped, which can cut a character out of frame, or make the model follow the keyframe's shape instead of `ratio`: a 3:2 keyframe sent to an image-to-video request asking for `1280:720` came back 3:2. Check the first take's dimensions with `ffprobe`.
- Set a seed when the model takes one, and record it.

**Last frames** (mode `first_last`): generate the first frame, then generate the last frame by editing *from the first frame*, so both share identity, light, and space. The motion between them has to be achievable in the shot's duration. A person can cross a room in 5 s; a sunrise needs a time-lapse prompt.

**Match cuts.** When the script calls for a match cut (a dark phone screen to a dark window), generate the outgoing shot's last frame and the incoming shot's first frame together, with matching composition, and use `first_last` on the outgoing shot.

## Chains

For a shot marked `chain_from`, its first frame comes from the predecessor's **selected** take after that take exists:

```bash
ffmpeg -y -sseof -0.1 -i clips/s04-t3.mp4 -frames:v 1 -q:v 1 keyframes/s05-first.png
```

Trim to the edit's out point first if the edit cuts before the clip ends: take the frame at the planned out point (`-ss <out>`), not the clip's last frame. Inspect the extracted frame, because end frames can be soft or mid-blur. If it is, step back a few frames, or regenerate a clean keyframe by editing from the extracted frame with the character references attached, which also corrects any drift. Generate chains strictly in order.

## Still checklists

Read each still you generate and run its checklist. Record failures in `plan.json` and fix them before moving on.

**Bible image**

- One subject, plainly lit, fully visible, without cropping of hair, hands, or wardrobe that a later shot needs.
- The face matches the portrait: eye shape, nose, jaw, hairline, skin tone, age.
- The wardrobe matches the descriptor exactly: colors, layers, accessories.
- No text, watermark, or extra people.

**Keyframe**

- Everyone in frame matches their sheet (face, hair, wardrobe for this scene).
- The composition matches the script's Shot field: size, angle, and where subjects sit, with room for the planned motion.
- Location, light direction, and time of day match the plate and the neighboring shots. Screen direction is consistent across the cut: a character exiting right enters the next shot from the left.
- Hands, fingers, eyes, and object contact read correctly. Look specifically; these fail most often.
- No unwanted text or garbled signage.
- The exact target aspect ratio, at full resolution.
- It looks like the style frame.

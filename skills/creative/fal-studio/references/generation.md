# Build-time generation on fal.ai

Everything you generate before ship: the still kit, the film's anchor frame, the cover, icons, textures, voiceover. Both flows use this file.

## Access

**MCP (default).** The `fal-ai` server exposes `search` (find models by keyword), `find` (a model's exact input schema), `generate` (run it), `status` / `result` (async jobs), `cancel`, `upload` (local file → fal URL), `estimate_cost`, `models`, `pricing`.

```
generate(app_id: "fal-ai/flux-pro/v1.1-ultra", input_data: { prompt: "...", aspect_ratio: "16:9", num_images: 2, seed: 7412 })
```

**REST (no MCP server).** Same models, `Authorization: Key $FAL_KEY` — the header word is `Key`, not `Bearer`.

```bash
# sync, for fast models
curl -sS https://fal.run/fal-ai/flux/dev \
  -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" \
  -d '{"prompt":"...","image_size":"landscape_16_9","seed":7412}'

# queue, for anything slow — video always
curl -sS https://queue.fal.run/fal-ai/veo3 \
  -H "Authorization: Key $FAL_KEY" -H "Content-Type: application/json" \
  -d '{"prompt":"..."}'                      # → { request_id, status_url, response_url }
curl -sS "https://queue.fal.run/fal-ai/veo3/requests/$ID/status" -H "Authorization: Key $FAL_KEY"
curl -sS "https://queue.fal.run/fal-ai/veo3/requests/$ID"        -H "Authorization: Key $FAL_KEY"
```

## Models drift — confirm before the first call

fal's catalog turns over fast: ids get versioned, params get renamed, models get retired. Pick by **role**, then run `find` (or `search`) once per build to confirm the id and its current input schema before you commit a prompt to it. Candidates below are starting points, not promises.

| Role | Candidates |
|------|-----------|
| Fast draft image, cheap iteration | `fal-ai/flux/schnell`, `fal-ai/nano-banana` |
| Hero still, photoreal | `fal-ai/flux-pro/v1.1-ultra`, `fal-ai/bytedance/seedream/v4` |
| Legible type, logos, posters | `fal-ai/recraft-v3`, `fal-ai/ideogram/v3` |
| Edit / restyle an existing image | `fal-ai/nano-banana/edit`, `fal-ai/flux/dev/image-to-image` |
| Image → video (the film) | `fal-ai/kling-video/v2.5-turbo/pro`, `fal-ai/bytedance/seedance/v1/pro/image-to-video` |
| Text → video with sound | `fal-ai/veo3` |
| Upscale | `fal-ai/clarity-upscaler`, `fal-ai/recraft/upscale/crisp` |
| Cutout / transparent PNG | `fal-ai/birefnet` |
| Voice | `fal-ai/elevenlabs/tts/multilingual-v2` |
| Sound for a clip | `fal-ai/mmaudio-v2` |

Two models fail differently and the winner is not predictable from the prompt, so run the **hero** shot through two of them and present both. Secondary shots then run once each on the winner, so the set holds together.

## The style formula

One string, written once in `DESIGN-SPEC.md`, appended verbatim to every prompt in the kit. It carries medium, lens, light, palette, and finish — never subject. This is what makes twelve separate generations read as one shoot.

> `shot on 35mm, shallow depth of field, low winter sun raking from camera left, muted slate and oxblood palette, fine grain, no text`

Per-asset prompts then vary only the subject and the framing:

```
<subject and action> · <framing and camera position> · <STYLE FORMULA>
```

Fix one `seed` for the kit and reuse it; change it only when you want a genuinely different take. Same seed plus same formula is the cheapest coherence you can buy.

Two things worth stating in every formula because they cause most of the rework: **no text** (generated lettering is where a hero image announces itself as AI), and the palette as literal color names matching the spec tokens.

## Aspect and resolution

Ask for the slot's real shape at generation time rather than cropping later — an upscaled crop of a square looks like one. Heroes at 16:9 (or 21:9 for a full-bleed band), cards at 4:3, portraits at 3:4, cover at 1200×630 (see `cover-and-meta.md`), icons square. Generate at the largest resolution the model offers for anything full-bleed; upscale the winner rather than regenerating bigger.

## Inputs from local files

fal models read URLs, not paths. Upload first, then pass the returned URL:

```
upload(file_path: "./public/generated/hero.png")   # → https://…/hero.png
generate(app_id: "fal-ai/nano-banana/edit", input_data: { prompt: "same scene, dusk", image_urls: ["<url>"] })
```

The same URL is what image-to-video takes as its anchor frame.

## Landing and the manifest

Result URLs are temporary. Every accepted asset gets downloaded into `public/generated/` and recorded, so the kit stays regenerable and nothing in the build depends on fal staying up:

```json
{
  "styleFormula": "shot on 35mm, shallow depth of field, …",
  "seed": 7412,
  "assets": [
    { "file": "hero.png", "slot": "hero", "model": "fal-ai/flux-pro/v1.1-ultra",
      "prompt": "…", "aspectRatio": "16:9", "requestId": "…" }
  ]
}
```

An asset with no manifest row is load-bearing and un-editable — the next person cannot regenerate it, only replace it.

## The coherence pass

Once, over the landed kit, in one batch — not generation by generation:

- Do they read as one shoot? Same light direction, same palette, same grain, same lens feel.
- Hands, faces at small scale, lettering, logos, repeated architectural detail — the four things that fall apart at full size and shout "generated". Crop them out or regenerate.
- Does each asset survive its actual slot? A hero judged at thumbnail size is judged wrong.

## Cost

`estimate_cost` before video, always; before a large still batch, when the batch is large. Stills are cheap enough that iterating is correct. Video sits orders of magnitude above them, which is the whole reason the film gets one approved prompt and an anchor still rather than six attempts.

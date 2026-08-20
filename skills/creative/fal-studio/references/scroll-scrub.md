# Scroll-scrub film

The animated site's centrepiece: one generated film whose playhead is driven by scroll position rather than by playback. The visitor scrubs it.

## One take

The default is a **single continuous take**, ~10–15s, scrubbed end to end. Not four clips stitched together: separate clips drift, and the drift is exactly where a viewer notices — the roofline changes, the product's proportions move, the window count differs in every phase. One take holds the geometry.

Stage the whole journey inside the prompt instead of across clips: "opens on X, camera pushes through Y, settles on Z". A multi-scene chain is opt-in, costs several minutes and a generation per leg, and earns itself only when the brief genuinely travels between distinct worlds.

## Anchor the ending

You already know what the last frame should look like — it is the finished-state still from the kit. Pass it as the image input and describe the final beat as matching it. Constraining the end frame is the difference between a film that lands on the page's hero and one that lands somewhere adjacent.

```
generate(app_id: "fal-ai/kling-video/v2.5-turbo/pro", input_data: {
  prompt: "<staged journey> · <STYLE FORMULA>",
  image_url: "<uploaded anchor still>",
  duration: "10"
})
```

Audio off: this plays muted inside a scroll container. Confirm the run with the user first — this is the expensive generation in the build.

## Re-encode for scrubbing

A normal encode seeks to the nearest keyframe, so scrubbing snaps in chunks. All-keyframe fixes it, at maybe 3–5× the file size, which is why the film is short:

```bash
ffmpeg -i film.mp4 -an \
  -c:v libx264 -profile:v high -pix_fmt yuv420p \
  -g 1 -keyint_min 1 -sc_threshold 0 -crf 20 \
  -movflags +faststart \
  public/generated/film-scrub.mp4
```

Keep the file under ~8MB. If `-crf 20` blows past that, scale to 1280 wide before reaching for a longer GOP — resolution costs less here than seek quality.

## Wiring

The section is one tall scroll track with a sticky viewport inside it. Scroll progress maps to `currentTime`, never to `play()`:

```tsx
const trackRef = useRef<HTMLDivElement>(null)
const videoRef = useRef<HTMLVideoElement>(null)

useEffect(() => {
  const track = trackRef.current, video = videoRef.current
  if (!track || !video) return
  let frame = 0
  const onScroll = () => {
    if (frame) return
    frame = requestAnimationFrame(() => {
      frame = 0
      const { top, height } = track.getBoundingClientRect()
      const progress = Math.min(1, Math.max(0, -top / (height - window.innerHeight)))
      if (video.duration) video.currentTime = progress * video.duration
      setStage(Math.min(STAGES.length - 1, Math.floor(progress * STAGES.length)))
    })
  }
  window.addEventListener('scroll', onScroll, { passive: true })
  return () => { window.removeEventListener('scroll', onScroll); cancelAnimationFrame(frame) }
}, [])
```

```tsx
<div ref={trackRef} className="relative h-[400vh]">
  <div className="sticky top-0 h-screen overflow-hidden">
    <video ref={videoRef} src="/generated/film-scrub.mp4"
           muted playsInline preload="auto" className="h-full w-full object-cover" />
    <p className="absolute bottom-16 left-8 text-balance">{STAGES[stage]}</p>
  </div>
</div>
```

Track height sets the scrub speed: ~400vh for a 10s film feels unhurried, 200vh feels fast.

Stage captions are DOM text driven by the same progress value, never burned into the video — they have to stay readable, translatable, and editable without a regeneration.

## The two fallbacks

Both are part of the feature, not polish:

- **`prefers-reduced-motion`** — render the anchor still with the stage captions stacked beneath it as ordinary content, and skip the video element entirely.
- **Mobile** — iOS Safari refuses to scrub some encodes at all. Ship a canvas frame sequence for small viewports, or the still, and test on a real phone before calling it done.

```bash
ffmpeg -i film.mp4 -vf "fps=15,scale=960:-2" -q:v 6 public/generated/frames/%03d.jpg
```

Preload the sequence, draw the frame nearest the progress value to a canvas, and the same scroll math drives it.

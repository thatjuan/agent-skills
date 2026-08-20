# Cover and metadata

Every build ships these. A utility page, a timer, a one-screen toy — no size exception, and nothing here waits for a deploy that this skill does not do.

## What ships

| Field | What it is |
|-------|-----------|
| `og_title` | The product's name and what it is, under ~60 characters |
| `og_description` | One sentence a stranger can act on, under ~155 characters |
| `og_image` | The generated cover, 1200×630, landed at `public/generated/cover.png` |
| favicon | 512×512 source plus the derived sizes, or hand-authored SVG |

Write them once into `src/site-meta.json` (or the framework's head config, when it already owns them) and let the head render from there — one source of truth, so a rename is a one-line edit.

## The cover

Generate it like you write the copy: no permission needed, no separate approval step. Prompt it through the kit's **style formula** so the card looks like the product it opens, at 1200×630, on a typography-capable model when the cover carries the wordmark (`generation.md` names them). Land it, manifest it, reference it locally.

A hand-drawn inline-SVG favicon is fine as a favicon. It is not a cover — the card is the first frame of the product for everyone who sees a link before they see the site.

## The optional cover video

`og_video` is permission-gated: it costs a video generation, so offer it and wait for a yes. Never generate one unprompted.

## Done means

A build presented as finished with an empty `og_title` or a missing cover is unfinished. The link renders as a blank card with a URL for a title, which is the one impression the product does not get to redo.

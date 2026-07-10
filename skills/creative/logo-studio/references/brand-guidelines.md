# Brand Guidelines Document

The Phase 8 deliverable is a multi-page brand guidelines document that establishes the rules for applying the finalized visual identity across every touchpoint — product UI, decks, social, print, motion, and voice.

## Table of Contents

- [Offer and Depth Modes](#offer-and-depth-modes)
- [Document Structure](#document-structure)
- [Inputs Synthesized from Earlier Phases](#inputs-synthesized-from-earlier-phases)
- [Extension Interview](#extension-interview)
- [Section Reference](#section-reference)
- [Rendering and Output](#rendering-and-output)
- [Design Language of the Guidelines Document](#design-language-of-the-guidelines-document)

## Offer and Depth Modes

Phase 8 activates only after a final logo is selected (end of Phase 6 or Phase 7). The user is offered the deliverable explicitly — it is not produced automatically.

Three depth modes are available:

| Mode | Pages | Scope |
|------|-------|-------|
| **Essentials** | 4–6 | Cover, Logo, Color, Typography, Asset Management |
| **Standard** | 8–10 | Adds Layout & Grid, UI Components, Voice & Tone |
| **Full** | 12–14 | Adds Motion & Animation, Extended Components, Approvals |

The mode is chosen by the user; defaults to Standard when the brand brief already includes digital product context (UI, web, app).

## Document Structure

Every guidelines document produced follows this canonical section order. Sections not selected for the depth mode are omitted.

| # | Section | Required | Source |
|---|---------|----------|--------|
| 1 | Cover | Yes | Brand name, tagline, version, date |
| 2 | Introduction | Yes | Purpose statement, audience |
| 3 | Logo | Yes | Primary, variants, signature elements, clear space, don'ts |
| 4 | Color Palette | Yes | Primary, extended, semantic, usage rules, gradients |
| 5 | Typography | Yes | Families, type scale, treatments |
| 6 | Layout & Grid | Standard+ | Canvas, grid systems, border radius |
| 7 | UI Components | Standard+ | 8–12 reusable component patterns |
| 8 | Motion & Animation | Full | Core values, timings, don'ts |
| 9 | Voice & Tone | Standard+ | Attribute table, sounds-like examples |
| 10 | Asset Management | Yes | File formats, naming convention |
| 11 | Brand Questions & Approvals | Full | Contact, version, approval process |

## Inputs Synthesized from Earlier Phases

The document draws these inputs from work already completed in Phases 1–6:

| Guidelines field | Derived from |
|------------------|--------------|
| Brand name, tagline | Phase 1 Discovery |
| Audience, purpose statement | Phase 1 Discovery, Only Statement |
| Primary logo, reversed, monochrome | Phase 6 final deliverables |
| Signature element (dot, mark, counter) | Phase 4 SVG construction notes |
| Primary brand colors | Phase 2 archetype mapping + Phase 4 color variants |
| Typography families | Phase 4 typography choice |
| Tone/personality axes | Phase 1 personality spectrums |

No re-prompting is needed for these — they already exist in the session context.

## Extension Interview

For inputs not produced by earlier phases, a short extension interview is conducted before rendering. Only the questions relevant to the chosen depth mode are asked.

### Essentials mode

| Item | Example |
|------|---------|
| Version and date | "v1.0, April 2026" |
| Extended colors (0–4) | Dark/mid tints of primary for depth, hierarchy |
| Semantic colors | Alert/error color, success color (optional) |
| Minimum logo size | "80px screen, 1 inch print" typical |
| Clear space rule | "Cap height of the first letter" typical |
| File naming convention | `{brand}-{asset-type}-{variant}-{version}.{ext}` default |

### Standard mode adds

| Item | Example |
|------|---------|
| Canvas target | "16:9 deck", "product UI", "print A4", "responsive web" |
| Border radius scale | 0 / 8 / 12 / 50% typical |
| Component inventory | Which of the 12 canonical components the brand uses |
| Voice attributes (3–4) | Pulled from personality axes — e.g. Confident, Precise, Human, Earned |
| Voice sounds-like / never-like pairs | One example each per attribute |

### Full mode adds

| Item | Example |
|------|---------|
| Motion principles | Intentional, Progressive, Restrained, Consistent (the defaults) |
| Timing table | Logo entrance 400ms, headline 350ms, etc. |
| Motion don'ts | Bouncing, parallax, letter-by-letter, motion blur |
| Approval contact | Name, team, channel for brand questions |

Defaults are proposed for every item, so the user can accept the whole extension interview with one confirmation.

## Section Reference

### 1. Cover

Contains: brand wordmark (primary variant) centered, "Brand Guidelines" title in the primary heading typeface, version + date line, audience line ("For Designers, Animators & Brand Partners" default), a one-sentence brand promise formatted as `{Brand} is {adjective}.`

### 2. Introduction

A two-paragraph opener. Paragraph 1: what the document is — single source of truth, scope of what it governs. Paragraph 2: why adherence matters — consistency across touchpoints.

### 3. Logo

| Subsection | Contents |
|------------|----------|
| 3.1 Primary Logo | Primary wordmark/combination mark displayed on light background, brief usage note, never-retypeset rule |
| 3.2 Reversed Logo | Same logo on dark (charcoal) background |
| 3.3 Brand-color Background | Logo on primary brand color — marked "limited use" |
| 3.4 Signature Element | If the logo has a distinctive mark (dot, counter, monogram, negative space), document its exact color/position and rule against alteration |
| 3.5 Clear Space & Minimum Size | Clear space defined as a relative unit (cap height, x-height); minimum size for screen and print |
| 3.6 Logo Don'ts | Two-column table: "Do Not" with X / "Guidance" with check. 5–7 rows minimum |

### 4. Color Palette

| Subsection | Contents |
|------------|----------|
| 4.1 Primary Brand Colors | 3–4 color swatches with hex, name, and role (e.g. primary text, primary accent, accent background, secondary text) |
| 4.2 Extended Brand Colors | 3–5 tints/shades with role (hierarchy, supporting visuals, card backgrounds, dividers/borders) |
| 4.3 Semantic & Alert | Alert red, success green, and any signature color that has a locked role |
| 4.4 Color Usage Rules | Single-row-per-color table — when to use it, when not to |
| 4.5 Approved Gradients | Optional. 1–2 gradient recipes as CSS `linear-gradient(...)` strings |

### 5. Typography

| Subsection | Contents |
|------------|----------|
| 5.1 Type Families | Side-by-side showcase of heading + body families with role, primary weight, and Google Fonts link |
| 5.2 Type Scale | Table of roles (Hero Headline, Section Header, Body, Caption, etc.) with family, size (pt), weight, line height |
| 5.3 Signature Treatment | If applicable: two-tone headline, italic accent word, bold lead-ins. Include markup snippet |

### 6. Layout & Grid

| Subsection | Contents |
|------------|----------|
| 6.1 Canvas & Margins | Target canvas size with margin specs |
| 6.2 Grid Systems | 2–3 grid templates as CSS snippets |
| 6.3 Border Radius | Scale table: context → radius value |

### 7. UI Components

8–12 numbered components, each with name, one-paragraph spec covering typography, colors, dimensions, and radius. Components are drawn from the canonical inventory:

- Slide/Page Title Block
- Hero Headline
- Feature Grid
- Stat Block
- Progress Bar
- Section Label
- Data Row / Table
- Quote Box
- CTA Box
- Status Badge
- Container / Card
- Divider Line

### 8. Motion & Animation

| Subsection | Contents |
|------------|----------|
| 8.1 Core Motion Values | 4-row table: principle → definition |
| 8.2 Recommended Timings | Element → duration → easing table |
| 8.3 Motion Don'ts | Bulleted list of off-brand effects |

### 9. Voice & Tone

Three-column table: Attribute / "Sounds like..." / "Never sounds like..." — 4 rows minimum.

### 10. Asset Management

| Subsection | Contents |
|------------|----------|
| 10.1 File Formats | Asset type → preferred format → notes (SVG master, PNG @2x fallback, MP4/WebM for motion, etc.) |
| 10.2 Naming Convention | Pattern string + 2–3 example filenames |

### 11. Brand Questions & Approvals

Two paragraphs. First: "applications not explicitly covered require approval" + contact info. Second: version/date reminder and verification note.

## Rendering and Output

### Template

The base template is [brand-guidelines-template.html](../assets/brand-guidelines-template.html) — a self-contained HTML file with embedded CSS, `@page` rules for PDF conversion, and placeholder tokens for every field.

### Output Path

`./brand-guidelines-{brandname}.html` in the working directory.

### Opening the File

After writing, the file is opened with `open` (macOS), `xdg-open` (Linux), or `start` (Windows).

### PDF Conversion

The HTML is designed for `print-to-PDF`:

| Method | Command |
|--------|---------|
| macOS Chrome headless | `chrome --headless --print-to-pdf=brand-guidelines.pdf brand-guidelines-{brand}.html` |
| Puppeteer | `npx puppeteer-pdf brand-guidelines-{brand}.html --format A4` |
| Browser Print | Cmd/Ctrl+P → Save as PDF |

The template includes `@page { size: letter; margin: 0.75in; }` and page-break rules so section headers start on a new page at full mode.

### Token Replacement

Placeholders in the template are filled in at render time:

| Token | Value |
|-------|-------|
| `{{BRAND_NAME}}` | Brand name |
| `{{BRAND_PROMISE}}` | Tagline / only-statement short form |
| `{{VERSION}}` | Version string |
| `{{DATE}}` | Publication date |
| `{{AUDIENCE}}` | Target audience line |
| `{{LOGO_PRIMARY_SVG}}` | Inline SVG — primary variant |
| `{{LOGO_REVERSED_SVG}}` | Inline SVG — reversed variant |
| `{{LOGO_ACCENT_SVG}}` | Inline SVG on brand-color background (optional) |
| `{{COLOR_SWATCHES_HTML}}` | Generated HTML block for the color palette section |
| `{{TYPE_FAMILIES_HTML}}` | Generated HTML for the type families showcase |
| `{{TYPE_SCALE_ROWS}}` | Table rows for the type scale |
| `{{COMPONENT_SECTIONS}}` | Component entries generated from the inventory |
| `{{VOICE_ROWS}}` | Voice & tone table rows |
| `{{MOTION_ROWS}}` | Motion timing table rows |
| `{{FOOTER_LINE}}` | `{Brand} · Brand Guidelines {version} · Internal Use Only` default |

Sections omitted by the depth mode have their entire `<section>` removed from the template before writing.

## Design Language of the Guidelines Document

The document itself is styled with the brand being documented — not a generic brand-book chrome. This makes the artifact an implicit demonstration of the guidelines it contains.

| Element | Rule |
|---------|------|
| Headings | The brand's heading typeface, in the brand's primary accent color |
| Body | The brand's body typeface in its charcoal/neutral primary |
| Section numbers | Accent-color treatment matching the logo's signature element |
| Footer rule | 1px line in the brand's accent color |
| Tables | Alternating zebra rows at ~3% tint of primary accent |
| Color swatches | Square chips with name, hex, and role line below |
| Dividers | 1px in the silver/light-gray from the extended palette |

The visual reference for tone and density is the example brand book style: charcoal/teal academic layout, generous white space, section numbers as chapter markers, and tables used liberally for rules.

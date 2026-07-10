# Design Psychology

Perceptual and cognitive principles that strengthen design concepts by aligning with how humans process visual information.

## Table of Contents

- [Gestalt Principles](#gestalt-principles)
- [Color Psychology](#color-psychology)
- [Scanning Patterns](#scanning-patterns)
- [Attention & Memory](#attention--memory)
- [Interaction Laws](#interaction-laws)
- [Social Proof Design](#social-proof-design)
- [Emotional Design — Norman's Three Levels](#emotional-design--normans-three-levels)

## Gestalt Principles

The mind organizes sensory inputs into meaningful wholes. These principles govern how humans perceive grouping, separation, and relationship in visual composition.

| Principle | Definition | Design Application |
|-----------|-----------|-------------------|
| **Proximity** | Elements close together are perceived as related | Group related navigation items, form fields, content blocks; separate unrelated groups with space |
| **Similarity** | Elements sharing visual traits (color, shape, size) are perceived as related | Consistent styling for elements with the same function |
| **Closure** | The brain completes incomplete shapes | Useful for logos, icons, loading states — the viewer participates in completing the form |
| **Continuity** | Elements on a line or curve are perceived as related | Guides eye flow through layouts; useful for timelines, progress indicators |
| **Figure-Ground** | Foreground content is distinguished from background | Essential for modals, overlays, card-based designs, CTAs |
| **Common Region** | Elements within the same boundary are perceived as grouped | Cards, containers, sections create visual grouping |
| **Symmetry** | Symmetrical elements are perceived as part of the same group | Creates stability and order; bilateral symmetry feels natural |

## Color Psychology

### Emotional Response Data

| Finding | Source Context |
|---------|--------------|
| Red CTAs outperformed green by 21% | HubSpot A/B test |
| Red and orange buttons generate 32-40% higher click rates | 1.2M A/B test aggregate |
| Red "Add to Cart" outperformed black by 34% | E-commerce testing |
| Healthcare sites achieve 18% higher trust with blues/greens | Industry research |
| Users spend 42% more time on colorful designs vs. monochrome | Engagement study |
| High-contrast elements receive 23% more clicks | Interaction analysis |

### The Key Insight

There is no universal "best color." What converts is **contrast against surrounding elements**, not the color itself. A red button converts well against a blue page because it stands out, not because red is inherently better.

### Cultural Context

Color meaning shifts with culture. Red means luck/prosperity in Chinese culture, danger/urgency in Western culture. White means purity in Western culture, mourning in some East Asian cultures. Concepts for global brands must account for these differences.

## Scanning Patterns

### Z-Pattern

**Eye path**: top-left → top-right → diagonal to bottom-left → bottom-right

| Position | What to Place |
|----------|--------------|
| Top-left | Logo, brand identifier |
| Top-right | Navigation, key action |
| Center diagonal | Key visual, value proposition |
| Bottom-right | Primary CTA |

**Best for**: Landing pages, homepages, text-light pages — any page guiding eye movement in sequence.

### F-Pattern

**Eye path**: horizontal scan across top → down left side → second horizontal scan (shorter) → continues down left

| Zone | What to Place |
|------|--------------|
| First horizontal bar | Most important content, headline |
| Left edge | Headings, subheadings, key words |
| Second horizontal bar | Secondary key information |
| Below | Supporting content (diminishing attention) |

**Best for**: Text-heavy pages — blogs, news, search results, articles.

### Application Strategy

Use Z-pattern for homepages and landing pages; shift to F-pattern for content-heavy interior pages. Hero sections follow Z-pattern; article bodies follow F-pattern.

## Attention & Memory

### Von Restorff Effect (Isolation Effect)

When multiple similar objects are present, the one that differs is most likely remembered.

| Application | How |
|-------------|-----|
| **Pricing tables** | Visually distinguish the recommended plan — filled background, shadow, badge, brand-colored CTA |
| **CTA buttons** | Primary action is visually distinct in size, color, and placement |
| **Content callouts** | Filled blocks or borders separate key information |
| **Navigation** | Current page/section highlighted differently |

**Critical rule**: "There must be more 'consistents' than 'standouts'" — if everything emphasizes, nothing stands out.

### Serial Position Effect

People remember items at the beginning (primacy) and end (recency) of a sequence better than middle items.

| Application | How |
|-------------|-----|
| Navigation | Most important items first and last |
| Feature lists | Key features at start and end |
| Page content | Critical information at beginning and conclusion |
| Pricing | Best option first or last position |

## Interaction Laws

### Hick's Law

Decision time increases logarithmically with the number of choices. Reducing options speeds decisions.

| Application | Guideline |
|-------------|-----------|
| Pricing plans | 3 options (the center one is chosen most often) |
| Navigation | 5-7 top-level items |
| Form fields | Essential minimum; progressive disclosure for complexity |
| CTAs per section | 1 primary, 1 secondary maximum |

### Fitts's Law

Time to reach a target depends on its distance and size. Larger, closer targets are faster to reach.

| Application | Guideline |
|-------------|-----------|
| Primary CTAs | Large, positioned in high-traffic areas |
| Related actions | Close together spatially |
| Mobile touch targets | Minimum 44×44px |
| Frequent controls | Within thumb reach on mobile |

## Social Proof Design

90% of buyers say social proof influences their purchasing decisions.

### Types and Placement

| Type | Implementation | Placement |
|------|---------------|-----------|
| **Testimonials** | Real names, photos, specific results | Near CTAs for maximum impact |
| **Client logos** | Organized rows or ticker animations | Above the fold (2.3x engagement vs. below) |
| **Metrics** | Specific numbers ("10,000+ clients", "$50M processed") | Hero section or trust bar |
| **Reviews** | Star ratings, average scores, total review counts | Near purchase/signup decisions |
| **User content** | Customer photos, case studies | Throughout the journey at decision points |

### Psychological Mechanism

The Identifiable Victim Effect: single-person narratives with names and faces outperform aggregated data for driving action. One specific customer story with a photo and name converts better than "10,000 satisfied customers."

## Emotional Design — Norman's Three Levels

### Level 1: Visceral (Appearance)

The first impression. Automatic, subconscious, pre-rational.

| What It Governs | Design Elements |
|-----------------|----------------|
| Immediate emotional reaction | Color, shape, style, form, composition |
| Attraction or repulsion | Visual identity, branding, surface aesthetics |
| First-glance judgment | Photography, whitespace, typography weight |

"Attractive products work better" — positive visceral response creates a halo effect on perceived usability.

### Level 2: Behavioral (Usability)

The experience during use. Measurable, functional, about performance.

| What It Governs | Design Elements |
|-----------------|----------------|
| Task completion satisfaction | Layout clarity, navigation logic, interaction design |
| Perceived effort | Progressive disclosure, information architecture |
| Error recovery | Feedback systems, error states, help systems |

Positive emotions from effortless goal achievement. Frustration from friction and confusion.

### Level 3: Reflective (Meaning)

Conscious rationalization after the experience. Identity, values, and story.

| What It Governs | Design Elements |
|-----------------|----------------|
| Self-image alignment | Brand positioning, market signaling, status |
| Story the user tells | Brand narrative, values, community |
| Long-term loyalty | Emotional connection, pride of association |

Reflective satisfaction can compensate for behavioral limitations — Apple Watch succeeded despite early functional limitations because the reflective-level appeal (status, identity) justified behavioral compromises.

### Applying All Three Levels to Concepts

A complete design concept addresses all three:

1. **Visceral**: How does it *look*? (the first 50ms)
2. **Behavioral**: How does it *work*? (the experience during use)
3. **Reflective**: What does it *mean*? (the story the user tells afterward)

The strongest concepts create alignment across all three levels — where appearance, usability, and meaning all reinforce the same brand story.

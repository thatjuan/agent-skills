# big-idea

> Generates creative concepts for ads, campaigns, promotions, stunts, taglines, and headlines, worked the way the advertising canon works and tested against its landmark campaigns.

## What it does

`big-idea` treats creative work as a method rather than inspiration. It follows James Webb Young's *A Technique for Producing Ideas*: an idea is a new combination of old elements, so the skill gathers a fact sheet of raw material first (product facts, audience truths, category conventions, culture), then generates widely through a set of lenses, strikes anything a rival agency would also bring, and judges what survives against Ogilvy's big-idea questions and the rest of the canon.

The lenses, tests, and cases draw on Young, Claude Hopkins, Rosser Reeves, Ries & Trout, David Ogilvy, Bill Bernbach, Leo Burnett, George Lois, Mary Wells Lawrence, Dave Trott, Rory Sutherland, Paul Feldwick, James Hurman, Luke Sullivan, Bob Schmetterer, Ed Catmull, Cialdini, the Heath brothers, Jonah Berger, Kahneman, Ariely, Godin, and Mario Pricken. Each concept it delivers names an **ancestor**, a landmark campaign that solved a similar problem with a similar move, and says what the new idea takes from it and where it departs.

## When to use it

- *"Campaign ideas for a regional bank that wants younger customers."*
- *"A launch stunt for our new electric scooter in Lisbon."*
- *"Tagline options for a sleep-tracking ring."*
- *"We're No. 3 in the category. How do we make that work for us?"*
- *"A promotion that gets people to try our oat milk in coffee shops."*
- *"An angle for our launch post that isn't another feature list."*

**Not the right skill if** you need a brand's visual identity (→ [`creative-director`](../creative-director/)), a logo (→ [`logo-studio`](../logo-studio/)), or a shootable script for a concept you already have (→ [`video-script`](../video-script/)).

## Example walkthrough

**Prompt**

> Ideas for a neighborhood bakery that only bakes in the morning and sells out by noon. They want more people to know about them without looking like a chain.

**What the skill does**

1. **Problem:** "The problem is that people who would love this bread arrive after it's gone, and the bakery reads the sell-out as a failure to fix."
2. **Raw material:** the bake starts at 3 a.m.; the sourdough starter is 19 years old; nothing is made after 7 a.m.; the category wallpaper is "artisan," wheat fields, and flour-dusted hands.
3. **Angles:** the sell-out as a virtue (flaw as virtue); the 3 a.m. baker (inherent drama); the bakery against the all-day chain (the enemy).
4. **Generates** 40+ one-line ideas across the lenses, writes the rival's pitch ("artisan, handmade, community"), and strikes what matches it.
5. **Delivers three concepts**, such as:

   **Concept: "Gone by Noon"**
   > **The idea:** The bakery publishes the time it sells out each day, as a scoreboard.
   > **Ancestor:** Guinness, "Good things come to those who wait": the inconvenience turned into the proof of quality.
   > **Hero execution:** A chalkboard in the window reads "Yesterday: gone by 11:42." A daily post with the time. Regulars bet on it.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill big-idea
```

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The vocabulary, the seven-step workflow, the selection tests, and the output format |
| `references/canon.md` | What each book and master teaches, as a principle to apply and a question to ask |
| `references/lenses.md` | Forty-odd generative lenses, each with a prompt, its source, and a campaign that used it |
| `references/cases.md` | Landmark campaigns from Schlitz to Draw Ketchup: problem, insight, leap, and why it worked |
| `references/executions.md` | Writing headlines, body copy, taglines, print and outdoor, film, promotion mechanics, and social |

## Tips

- **Give it real facts.** A factory visit, founder notes, reviews, and support tickets are raw material; the best ideas come from details nobody thought were interesting.
- **Name the real constraint.** Budget, channel, and what the brand can actually change shape the idea more than tone words do.
- **Say what's been tried.** Past campaigns and competitors' work go straight into the wallpaper the idea has to break.
- **Ask for the also-rans.** The ideas cut in selection are often the seed of the next round.
- **Push on the strategy before the execution.** If none of the three concepts feels right, the angle is usually what's wrong.

## Related skills

- [`video-script`](../video-script/) — turn a concept's film into a shot-by-shot script.
- [`video-production`](../video-production/) — produce the video.
- [`creative-director`](../creative-director/) — the visual world around the brand.
- [`clean-writing`](../clean-writing/) — tighten long-form copy.

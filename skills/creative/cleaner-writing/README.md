# Cleaner Writing

Write prose that reads as written by a careful person. Invoke `cleaner-writing` to draft text, tighten a passage, or strip the habits that mark text as machine-written. It also applies automatically when a writing task fits.

Example: "Use cleaner-writing to edit this launch post. Keep the facts and our casual tone."

The [skill](./SKILL.md) extends [clean-writing](../clean-writing/SKILL.md): the same composition principles, followed by a revision pass against ten **reflexes**, the defaults that fill the space where a writing decision belongs. Each reflex has a target behavior and a before/after pair. It requires no tools or other skills at runtime.

1. Template shape
2. Corrective framing
3. Announced significance
4. Inflated register
5. Reflexive rhythm
6. Abstraction
7. Hedge stacking and false balance
8. Phantom authority
9. Formatting for show
10. Chat residue

## Sources and editorial choices

- William Strunk Jr. and E. B. White, *The Elements of Style*, fourth edition, via [clean-writing](../clean-writing/README.md), which lists the editions consulted.
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), WikiProject AI Cleanup. Source for announced significance, copula avoidance ("serves as"), negative parallelisms, rule of three, vague attribution, and formatting tells.
- Kobak et al., [Delving into LLM-assisted writing in biomedical publications through excess vocabulary](https://arxiv.org/abs/2406.07016). Measured excess words (delves, underscores, showcasing) across 15 million PubMed abstracts.
- Juzek and Ward, [Why Does ChatGPT "Delve" So Much?](https://aclanthology.org/2025.coling-main.426.pdf). Traces lexical overuse to preference tuning rather than pretraining, which is why tells shift between model versions.
- Matthew Vollmer, [I Asked the Machine to Tell on Itself](https://matthewvollmer.substack.com/p/i-asked-the-machine-to-tell-on-itself). Field guide covering template structure, hedge-and-reassure, false concession, aphoristic closure, and missing particulars.
- TechCrunch, [Opus 5.5 loves to tell you "this matters"](https://techcrunch.com/2026/10/01/opus-5-5-loves-to-tell-you-this-matters-and-other-ai-writing-tells), reporting Graphite's phrase-frequency analysis. Source for current frontier-model tells: "this matters," "why X matters," "dependable," "is more than an X, it's a Y," and corrective framing ("not simply X," "rather than relying on X").
- [Humanizer by @blader](https://github.com/blader/humanizer), via clean-writing.

The research converged on one shift: current models have mostly dropped the old lexical tells (em dashes, "delve"), and the durable tells are structural. The skill therefore names each reflex by its mechanism and treats word lists as examples, and it tells the agent to repair the sentence rather than swap the word. Every reflex leads with a positive target so the agent drafts toward it. Examples are illustrative; the skill forbids inventing particulars to replace abstraction. The em dash preference is a local convention carried over from clean-writing.

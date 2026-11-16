---
name: clean-writing
description: Write or edit prose that reads as written by a careful person. Use for drafting reader-facing text, tightening drafts, or stripping AI tells (template structure, corrective framing, announced significance, inflated vocabulary) from emails, docs, articles, and product copy.
---

# Clean Writing

Make the reader's work easy. Compose with Strunk and White's principles, then revise against the eleven **reflexes** below. A reflex is a default that fills the space where a decision belongs: the template stands in for a chosen order, and "robust" for a named property. Each repair makes the missing decision. Preserve the author's meaning and voice throughout.

## Compose for the reader

- Choose an order that fits the purpose. In practical writing, lead with the answer or the action required; follow with the evidence and context the reader needs.
- Give each paragraph one job. Use parallel grammar for parallel ideas.
- Name the actor and the action. Prefer active verbs; keep the passive when the actor is unknown or the recipient deserves focus. "Conduct an evaluation" becomes "evaluate."
- Choose concrete nouns and precise verbs. Keep technical terms where they add precision. Use one term for one thing, and repeat it.
- Cut words that add neither meaning nor useful rhythm. Keep the explanations and qualifications the reader needs, and the transitions that connect them.
- Keep subjects near verbs and modifiers near what they modify. Make the grammatical subject the thing the sentence is about. Put the weight at the end.
- Let voice come from observation and judgment. Match the author's register, and keep their humor and distinctive phrasing. Respect the requested genre, and any house style or dialect.

## Revise against the eleven reflexes

Read the draft once per reflex. Repair the sentence, not the word: swapping "delve" for "dig into" keeps the reflex alive. The tells listed under each reflex are current examples of a mechanism; new models drop old tells and grow new ones, so hunt the mechanism. Sentence fragments and "note that" are often blamed on models and are more common in people's writing; leave them where they work.

1. **Template shape.** Intro, three sections, recap, at every length; signposting ("First, we'll look at..."); a closing summary of what was just said. Target: length and order follow the content. A short answer is the answer. Stop when the last point lands.
   - Before: "Caching can be tricky. Let's walk through three key strategies. ... In summary, choosing the right strategy depends on your needs."
   - After: "Cache the rendered page at the CDN for five minutes. Your data changes hourly, so nothing finer is worth the invalidation work."

2. **Corrective framing.** Presenting a choice by naming the one not taken, or defining a thing by what it isn't: "Y rather than X," "instead of relying on X," "not X, it's Y," "more than an X, it's a Y," "not simply." "Rather than" is the strongest of these: models write it about four times as often as people do, and a rule against it does not stop them. Target: state the affirmative claim. Keep a contrast only when the reader actually holds the rejected view.
   - Before: "We run jobs from a Postgres table rather than adding a separate queue."
   - After: "Jobs run from a Postgres table, so there is no queue to operate."
   - Before: "This isn't just a bug fix. It's a rethink of how sessions work."
   - After: "This change moves session state into Redis, so logins survive deploys."

3. **Announced significance.** Telling the reader something is important without showing why: "this matters," "why X matters," "a pivotal moment," "a testament to," trailing "-ing" clauses ("highlighting its importance"). Target: give the consequence and let the reader judge its weight. If the source supplies no consequence, cut the claim.
   - Before: "The team shipped offline mode, marking a pivotal step in the app's evolution."
   - After: "The team shipped offline mode. Field crews can now log inspections without signal."

4. **Inflated register.** Prestige words where plain ones fit: delve, underscore, showcase, pivotal, intricate, robust, seamless, dependable, leverage, streamline, foster, landscape, realm, tapestry; newer arrivals such as "quietly" and a figurative "load-bearing"; "serves as" or "functions as" where "is" fits. Target: the plainest word that carries the meaning; is, has, uses, shows.
   - Before: "The platform serves as a robust solution that leverages AI to streamline invoicing."
   - After: "The platform uses AI to draft invoice replies."

5. **Reflexive rhythm.** Triplets by default, in adjectives ("fast, reliable, and secure") and in nouns alike ("forms, census tables, and medical records"), sentences all 15 to 25 words, paragraphs of equal size, "from X to Y" ranges that name no real range. Target: list as many items as the facts supply; let sentence and paragraph length follow the thought. Short sentences land a point; long ones carry reasoning.
   - Before: "It is fast, flexible, and secure."
   - After: "It returns most queries in under 50 ms."

6. **Abstraction.** Truisms, generic nouns, hypotheticals where a real case exists, wisdom that fits any topic. Target: the particular case, number, name, or observation that only this piece could contain. Take particulars from the source or the author; when none exist, say less.
   - Before: "Clear communication is key to any team's success."
   - After: "Standups ran 40 minutes because people read tickets aloud. Posting updates beforehand cut them to 12."

7. **Hedge stacking and false balance.** Qualifiers piled before the claim ("may potentially help in some cases"), "can provide," "generally speaking," and both-sides summaries that end "the truth lies somewhere in between." Target: make the claim, then put one qualifier on the specific uncertainty. When sources disagree, say which evidence would settle it or take the position the evidence supports.
   - Before: "This may potentially help improve performance in certain scenarios."
   - After: "This halves cold-start time on the x86 benchmarks; ARM is untested."

8. **Phantom authority.** "Experts agree," "studies show," "observers have noted," and any invented fact, quote, citation, statistic, or personal experience added for vividness. Target: name the source when one exists; otherwise state the claim as the author's, or flag it as unsupported. Preserve real uncertainty.
   - Before: "Experts agree that remote teams are more productive."
   - After: "Stanford's 2015 Ctrip trial found a 13% productivity gain for staff working from home." (Or, with no source in hand: flag the claim.)

9. **Formatting for show.** Bullets for connected reasoning, headings on a short reply, bold on every list stem, "**Label:** sentence" bullets, emoji markers, tables for two facts, title case in body text. Target: paragraphs for reasoning, lists for parallel items or ordered steps, headings where a reader navigates, bold for the one thing a skimmer must not miss. Replace em dashes with commas or full stops.
   - Before: "**Speed:** The new parser is faster. **Memory:** It uses less memory."
   - After: "The new parser is twice as fast and uses a third of the memory."

10. **Slogan headings.** Titles and headings built as comma-joined parallel imperatives or noun phrases with the "and" removed ("Pick the files, send the link"; "One command, zero config"), often with "the" pointing at things the reader hasn't met. They carry the rhythm of ad copy and hide what the section covers. Target: a heading names the section's subject or the question it answers, as a plain noun phrase or one ordinary clause. Test: the heading still works as an entry in a table of contents. If it reads as a tagline, rewrite it.
    - Before: "Pick the files, send the link"
    - After: "Sharing files by link"

11. **Chat residue.** Assistant habits leaking into finished copy: praise for the question, "I hope this email finds you well," "Let's explore," offers of further help, and the aphoristic closer ("In the end, the real question is..."). Target: start with content; end on the last substantive sentence. Close a message with the specific next step when one exists.
    - Before: "Great question! ... Hope this helps, and let me know if you'd like me to go deeper!"
    - After: "... I'll send the revised contract Thursday."

## Deliver

Compare the result against the source: facts, scope, certainty, commitments, citations, and quoted wording survive unchanged. Flag substantive ambiguity; do not resolve it silently. Leave passages that already work alone; the reflexes are diagnostics, not a quota.

Then check two habits directly, because they survive the passes above: search the result for "rather than" and "instead of," and count the items in every list. Rewrite each hit unless the reader holds the rejected view, and each list of three unless the facts supply exactly three.

Done when every reflex has had its pass, the reader can follow the point without rereading, each paragraph advances it, and no unsupported detail has entered the text. Return the finished prose. Add an editorial note only when requested or when a factual issue is unresolved.

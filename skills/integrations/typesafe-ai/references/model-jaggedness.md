# Jev 1.13 jaggedness

Known failure modes of `jev-1.13` and the documented workaround for each. Docs page last reviewed 2026-09-17; later versions may close some of these.

## Literal reading

Symptom: the model answers the question you wrote, not the one you meant; scoping words, negations, and implied conditions are read at face value.

Workaround: state the exact condition in `instructions` and put boundary cases in the criteria. When you find yourself explaining what you really meant after a wrong answer, that explanation is the missing half of the instruction. Where interpretation is unavoidable, split into two literal questions and combine them in code.

## Math and counting

Symptom: Jev is not a calculator. It does not count reliably (characters, occurrences, items in a list) and the error grows with the size of what is counted. Numeric encodings (hex colours, RGB triples, low-level or binary instructions) underperform their semantic equivalents. `score` is weak in numeric calibration, so interpolating a magnitude between two levels does not work.

Workaround: keep all arithmetic in code. To count items matching a judgment, ask one Noul per item and sum in code. Convert numeric representations to a computed number or a named bucket before sending. Use `score` only to test a threshold, never to reconstruct an exact number.

```python
result = client.system_one(
    {"items": items},
    {
        f"item_{i}": Noul(instructions=f"Is `items[{i}]` the name of a fruit?")
        for i in range(len(items))
    },
)

count = sum(result.nouls[f"item_{i}"].noul > YES for i in range(len(items)))
```

## Dates and times

Symptom: dates are read as text, not as ordered quantities. Which of two dates is first, how far apart they are, and whether one falls inside a window are unreliable, worse with mixed formats, relative references, and boundaries such as quarters.

Workaround: extraction is a judgment, so give it to the model; arithmetic is not, so keep it in code. Each date part is a small closed set, so extract month, day, and year as Choice questions with an explicit "not stated" option, then assemble the date and do ordering, duration, and weekday in code (see the date extraction cookbook).

## Indirection and double negatives

Symptom: instructions with double negatives, a property of a property, or several hops of reasoning are answered less reliably.

Workaround: write instructions as directly as possible and name the relevant parts of state by backticked path.

## Large or irrelevant state

Symptom: accuracy falls as the state grows with content unrelated to the decision; unrelated detail distracts and makes a wrong answer harder to trace. The context window is bounded (see the Models page for limits).

Workaround: retrieve and filter in code first, and send only the fields the question needs. When code cannot filter, add a Noul that judges relevance and drop what fails it (the classifying RAG passages cookbook shows this).

## Adversarial content

Symptom: state is data and is not treated as hostile by default. Injected instructions, misleading framing, or text that argues for its own classification can move the answer.

Workaround: be explicit in the criteria about what each outcome means, and test edge cases and hostile inputs before deploying to many users.

## Contradictory instructions and criteria

Symptom: when `instructions` and `criteria` ask for different things the model gets confused. A Noul whose `true` maps to no and `false` maps to yes performs worse.

Workaround: treat criteria as an extension of the instruction and align the two in plain language an average person can read. Make `true` the yes case and the case your code acts on.

## Structural invariants across questions

Symptom: the model is consistent for similar inputs, but identities you might expect between separate questions do not hold. "Is the customer asking for a refund?" as a Noul and as a yes/no Choice on the same ticket gave `noul` 0.22 against Choice `yes` 0.01 (confidence 0.97). The question and its negation as two Nouls gave 0.72 and 0.47, summing to 1.19.

Workaround: ask each decision one way, worded to mean directly what you want, and enforce identities in code. Keep a threshold tuned on a Noul away from a Choice. A Choice is relative (which option) while one Noul per option is absolute and can be low for all of them; use the Choice to pick and the Nouls to decide whether to act at all.

## Text generation

Symptom: the model is not trained to generate text. Chaining Choices to force generation works badly and slowly.

Workaround: when the answer space is bounded, produce candidate values with a regex or a generative model and let Jev pick the correct one with a Choice. For open-ended text, use a generative model.

## Reminder

From the docs page, verbatim:

> **As a reminder, avoid the following:**
>
> * Asking the model something code can compute exactly.
> * Hiding several judgments inside one question.
> * System Two tasks: more layers of indirections
> * Giving it more context in `state` than the question needs. Jev suffers from context rot, so unrelated material in the `state` costs you accuracy.

(source: model-jaggedness/jev-1.13.md)

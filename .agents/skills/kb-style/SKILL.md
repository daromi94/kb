---
name: kb-style
description: Apply this repository's teaching-first prose, explanation, and formatting standards when creating, editing, or reviewing knowledge-base notes under topics/.
---

# KB note style

## Core message

A note teaches one thing. State it in a single sentence; every
paragraph must serve it.

The opening paragraph delivers that core message — a reader grasps it
from the first paragraph alone.

When the idea has a central tradeoff or operational rule, state it near
the opening as a short bold blockquote. Use this only when it gives the
reader a memorable anchor, not as a required decoration.

## Teaching flow

A note should feel like an excellent technical explanation, not compressed
reference material. Give the reader enough intermediate reasoning to see
why the conclusion follows.

- **Lead with the thesis.** Define the idea and its central consequence
  before introducing mechanisms or edge cases.
- **Move from abstract to concrete.** Follow a principle with a small
  technical scenario, state transition, comparison, or data flow that makes
  it observable.
- **Develop one implication at a time.** Let each important consequence land
  before moving to the next. Use headings that express the question or claim
  the section resolves.
- **Recombine the pieces.** Near the end, show how the mechanisms interact
  and restate the idea as a practical design rule.

Do not force every note through the same visible template. Use the smallest
sequence that teaches the idea completely, but prefer clarity and useful
reinforcement over maximum compression.

## Teach the idea

- **The idea, not the framework.** Teach the insight that survives
  across implementations, not a tour of one ecosystem's API. Drop
  coupling to specific frameworks, wire formats, status codes, and
  runtime APIs unless they are load-bearing for the lesson. A
  concrete example grounds a pattern; a single-vendor walkthrough
  dates the note. Test: would this read the same in another
  ecosystem?
- **The model, not its config flags.** State the conceptual or
  recommended model in clean declarative sentences. Don't hedge it
  with every config flag, opt-in toggle, or dev-mode exception that
  technically violates the rule — those are reference material, not
  the lesson. Add a qualification only when the edge case is the
  common one.
- **The concept, not an analogy.** No narrative analogy — no chefs,
  cities, kitchens, sports, or "think of it like…". A concrete
  technical example is fine; a mapping to an unrelated everyday scene
  is not.

## Timeless writing

A note describes the current state of its subject, with no marker of
when it was written.

- No dated references — version numbers, "as of 2024", "currently",
  "new in v3", "modern", release-specific framing.
- No deprecation language — "deprecated since", "removed in",
  "replaced by X", migration advice from an old API. Document only
  the current approach.

## Paragraphs

- **One idea per paragraph.** Split a paragraph that carries two;
  merge two that carry one. Before splitting a long one, test it: if
  its second half can open only with a backward connective —
  "Otherwise", "Then", "But" — it was one idea all along. Tighten it
  instead.
- **Idea first.** Each paragraph opens with its point. Supporting
  detail — reasoning, mechanism, examples — comes after, never before.
- **Order by dependency.** The core message leads; supporting ideas
  follow in the order that builds understanding.
- **Earn the space.** Cut restatement that adds nothing. Keep deliberate
  reinforcement when a concrete example, comparison, failure case, or final
  principle makes an earlier abstraction easier to understand or remember.

## Prose or bullets

Choose the form that best performs each teaching job:

- Use prose for reasoning, causality, qualifications, and transitions.
- Use bullets for genuine sets of choices, consequences, requirements, or
  independent examples.
- Use tables when the reader needs to compare the same dimensions across
  several options.
- Use short ASCII diagrams for topology, data flow, state transitions,
  bottlenecks, failure propagation, and before-and-after behavior.
- Use `text` code blocks for compact pseudo-state, equations in words,
  configuration fragments, or a sequence that benefits from visual rhythm.

Visual structure is part of the explanation, not decoration. Introduce a
table or diagram in prose, explain the conclusion it reveals, and keep it
small enough to understand at a glance. Do not repeat the same information
in prose, a list, and a diagram unless each form adds a distinct insight.

## Voice

- **Active voice.** The subject performs the action. Recast a cleft —
  "what X returns is Y" — into the plain "X returns Y". Keep passive
  only when it earns its place, such as holding one topic in subject
  position across sentences.
- **Second person, not first.** Address the reader as "you" where a
  note speaks to them directly. Never "we" or "I".
- **State facts directly.** Say what something *is* or *does* before
  explaining why.
- **Teach conversationally.** Use natural transitions and direct questions
  when they guide the reader's attention. Sound like a thoughtful expert
  explaining the idea, not a specification compressing it.
- **Neutral, mechanical wording.** Describe the action, not its
  drama. No "final chance", "last wishes", "death rattle", "graceful
  curtain call" — write "runs cleanup before the process exits". No
  all-caps or exclamation marks for emphasis.
- **No anthropomorphism.** Software has no intent. Don't write that a
  service "wants", "knows", "thinks", or "is happy" — state what it
  does.

## Tense

- **Present tense** for behavior not tied to a moment in time: "the
  server sends an acknowledgment", not "will send".
- Use **"will"** only for an action that genuinely happens later than
  the surrounding text — "the file is archived the next time the
  backup runs".
- **No "would"** for hypotheticals. Recast in the present: "if you
  send an unsubscribe message, the server removes you", not "would
  then remove you".

## Sentences

- **Lead with the point.** State the fact or rule first; reasoning,
  mechanism, and examples follow it.
- **One reading is enough.** No vague term, no ambiguous "and" or
  "or", no pronoun without a plain antecedent. One idea per sentence.
- **Short and positive.** A sentence over 25 words is usually two —
  break it or cut. State things positively; avoid a double negative
  ("not uncommon" → "common").
- **Restrictive "that", nonrestrictive "which".** Use "that" for a
  clause that identifies the noun, with no comma; use "which" for a
  clause that only adds detail, set off with commas.
- **Condition before consequence.** In an if/then sentence, put the
  condition first so the reader knows whether the rest applies: "if
  the cache misses, the read falls through to disk".
- **Sound.** Every sentence is grammatically correct, and every claim
  it makes is true.

## Words

- **Cut filler and hedges:** "basically", "essentially", "in order
  to", "the fact that", "it should be noted that", "it is worth
  mentioning", "one might consider". Cut anything a neighboring
  sentence already implies.
- **Cut convoluted phrasing,** roundabout explanations, and
  unnecessary qualifiers. Get to the point.
- **No Latin abbreviations.** Write "for example" or "such as", not
  "e.g."; "that is", not "i.e.".
- **No "and/or".** Rewrite with "or", "and", or "both" — tables may
  keep "and/or" when space is tight.
- **No "etc." or "and so on".** Complete the list, or name the
  category the items belong to.
- **Serial comma.** In a list of three or more, put a comma before
  the final "and" or "or".
- **Lowercase after a colon** unless a proper noun or a complete
  sentence follows.

## Inclusive language

- Use bias-free technical terms: "allowlist" and "denylist", not
  "whitelist" and "blacklist"; "primary" and "replica" (or "leader"
  and "follower"), not "master" and "slave". When a non-inclusive
  term is fixed in an API, name the inclusive term first and give the
  literal one in parentheses.
- Use singular "they" for a person of unspecified gender — never
  generic "he" or "she", never "he/she".
- Drop ableist and violent terms — "sanity check", "dummy",
  "crazy", "cripples". Say what you mean: "quick check",
  "placeholder", "baffling", "slows down".

## Terms and jargon

Define a term when you introduce it (**Term:** its definition), and
spell out an acronym on first use. A note stands on its own — a
reader returning in six months has only the note, not the context in
which it was written.

Keep precise technical terms, but cut needless jargon: replace a
figurative insider term ("post-mortem", "dogfooding") or internet
slang ("tl;dr", "RTFM") with the plain phrase that carries the same
meaning.

## Examples

Make example values meaningful and realistic — a name, path, or
identifier that fits the context. Don't fall back on placeholder
noise like "foo", "bar", or "baz".

Use examples to expose mechanism. Prefer a minimal scenario that shows a
change in state, a request path, a capacity boundary, or a failure sequence.
When useful, contrast the system before and after the design choice so the
tradeoff becomes visible.

## Emphasis and conclusions

Use bold text for a term, compact label, or sentence fragment that deserves
attention. Use a blockquote for one central tradeoff or design principle.
Avoid scattering emphasis across every paragraph.

Horizontal rules may separate major phases of a longer explanation. Do not
place them between sections that already flow naturally.

End by sharpening the lesson into a practical principle, decision rule, or
compact comparison. A conclusion should synthesize the note rather than
repeat every section.

## Lists and links

- **Parallel structure.** List items and sibling headings share one
  grammatical form.
- **No links between notes.** A note is self-contained; it never links
  to another note. The only links are an `_index.md`'s entries and each
  note's `Return to [...](_index.md)` footer.

## Spelling

American English spelling and punctuation throughout — "behavior"
not "behaviour", "synchronize" not "synchronise".

## Numbers

- Spell out zero through nine in prose; use numerals for 10 and up.
  Use numerals at any size for technical quantities: "version 2",
  "8-bit", "3 retries", "40%".
- Group digits in a large number with commas ("1,048,576"); give a
  decimal below one a leading zero ("0.5").
- Spell out a number that opens a sentence, or reword so it doesn't.

## Hyphenation

- Hyphenate a compound modifier before the noun it modifies —
  "well-formed request", "64-bit integer", "read-only field". Don't
  hyphenate an "-ly" adverb ("publicly available").
- Write an established compound noun closed: "webpage", "hostname",
  "workaround", "lookup".
- Never put spaces around a hyphen, and don't use a hyphen where an
  em dash belongs.

## Naming the fault

When a sentence reads wrong, name the exact fault before fixing it —
weak collocation, cleft, nominalization, redundancy, repetition,
subject-verb mismatch. A precise diagnosis produces a precise fix.

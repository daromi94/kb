---
description: Polish a single KB note, paragraph by paragraph
arguments: <note-path>
---

# Knowledge Editing Skill

Polish one existing note until every paragraph is excellent. Where
`/kb:review` sweeps a whole topic for consistency and ordering,
`/kb:editor` goes deep on a single note — its core message, its
structure, and the wording of every paragraph.

Refer to `/kb:ingest` for all formatting and structural standards.

Improve how the note expresses and orders its ideas, and cut what is
redundant. Do not change its substance — what the note teaches stays
fixed.

## Workflow

### 1. Read the whole note

Read the note at `<note-path>` start to finish before changing
anything. If no path was given, ask which note to edit. Understand
what it teaches, how it is built, and where it sags.

### 2. Find the core message

State, in one sentence, the single thing the note exists to teach.
Every paragraph must serve it.

The opening paragraph must deliver that core message — a reader should
grasp it from the first paragraph alone. If it does not, that is the
first fix.

### 3. Audit the structure

Go paragraph by paragraph. Name, in twelve words or fewer, the one
idea each paragraph carries.

- **One idea per paragraph:** split a paragraph that carries two;
  merge two that carry one.
- **Idea first:** each paragraph opens with its point. Supporting
  detail — reasoning, mechanism, examples — comes after it, never
  before.
- **Order by dependency:** the core message leads; supporting ideas
  follow in the order that builds understanding.
- **Earn the space:** cut any paragraph or section that only restates
  what another already said. A heading must name the content beneath
  it, not the project or a template.

### 4. Choose prose or bullets

Prose is the default. It carries reasoning, cause and effect, and the
connective tissue between ideas.

Use a bullet list only for a genuine set of parallel, independent
items that need no connective tissue between them. Never bullet to
look tidy; never force prose onto a real list.

### 5. Polish every paragraph

Work through the note one paragraph at a time. Make each one:

- **Tight:** every word earns its place. Cut filler, hedges, and
  anything a neighboring sentence already implies.
- **Clear:** one reading is enough — no vague term, no ambiguous
  "and" or "or", no pronoun without a plain antecedent.
- **Active:** prefer active voice. Recast a cleft — "what X returns
  is Y" — into the plain "X returns Y". Keep passive only when it
  earns its place, such as holding one topic in subject position
  across sentences.
- **Sound:** grammatically correct, and every claim it makes is true.

When a sentence reads wrong, name the exact fault before fixing it:
weak collocation, cleft, nominalization, redundancy, repetition,
subject-verb mismatch. A precise diagnosis produces a precise fix.

### 6. Reflow and re-read

Re-wrap every changed paragraph to the line width in `/kb:ingest`. If
the title changed, update the `_index.md` entry and the `Return to`
footer so the link text still matches.

Then read the whole note again, top to bottom — it must flow, and the
core message must still land.

### 7. Apply and iterate

Edit the note sequentially, never in parallel. Present each revision
with the precise reason for every change.

Expect the user to keep refining the wording, down to single words —
that is how this skill is meant to be used. When they flag something
only by feel, supply the precise diagnosis and a targeted fix.

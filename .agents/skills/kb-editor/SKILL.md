---
name: kb-editor
description: Polish one existing knowledge-base note under topics/ paragraph by paragraph without changing what it teaches.
---

# Knowledge Editing Skill

Polish one existing note until every paragraph is excellent. Where
`$kb-review` sweeps a whole topic for consistency and ordering,
`$kb-editor` goes deep on a single note — its core message, its
structure, and the wording of every paragraph.

Before editing, read [kb-ingest](../kb-ingest/SKILL.md) completely for
formatting and structural standards, and read
[kb-style](../kb-style/SKILL.md) completely for prose and wording standards.

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

The opening paragraph must deliver that core message (see **Core
message** in `$kb-style`). If it does not, that is the first
fix.

### 3. Audit the structure

Go paragraph by paragraph. Name, in twelve words or fewer, the one
idea each paragraph carries, then fix it against the **Core message**
and **Paragraphs** rules in `$kb-style`. A heading must name
the content beneath it, not the project or a template.

### 4. Choose prose or bullets

Apply the **Prose or bullets** rule in `$kb-style`: prose
is the default; a bullet list serves only a genuine set of parallel,
independent items.

### 5. Polish every paragraph

Work through the note one paragraph at a time, holding each to every
rule in `$kb-style` — voice, tense, sentences, words. When a
sentence reads wrong, name the exact fault before fixing it, as
**Naming the fault** there describes.

### 6. Reflow and re-read

Re-wrap every changed paragraph to the line width in `$kb-ingest`. If
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

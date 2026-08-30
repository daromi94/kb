---
name: kb-review
description: Review knowledge-base notes under a topic for clarity, consistency, structure, and ordering, then apply approved fixes.
---

# Knowledge Review Skill

Review existing Zettelkasten notes for readability, consistency, and
learning impact. The goal is to make every note clearer and more
memorable without changing its substance.

Before reviewing, read [kb-ingest](../kb-ingest/SKILL.md) completely for
formatting and structural standards, and read
[kb-style](../kb-style/SKILL.md) completely for prose and wording standards.

## Workflow

### 1. Load notes

- Use `rg --files topics/<topic-path>` to find all notes
- Read `_index.md` and every note in the topic

### 2. Read-through

Read each note as a whole and assess whether it reads well. Does it
flow naturally from start to finish? Does the structure serve the
content? Are sections in the right order? Does each paragraph earn
its place? Flag anything that feels off — orphaned thoughts,
awkward transitions, sections that don't belong where they are.

### 3. Check format compliance

Verify each note against the formatting and structural standards in
`$kb-ingest`: tables, titles, links, and index structure. List any
deviations.

### 4. Check readability and clarity

Check every note against `$kb-style` — each rule there
applies: core message, paragraphs, voice, tense, sentences, words.
Flag every deviation.

Then assess what that file does not cover:

- **Missing arguments:** Does the note assert something without
  explaining why, when the "why" is not obvious?
- **Thin sections:** Are there sections of only 1-2 sentences that
  feel underdeveloped? Flesh them out or fold them into another
  section.
- **Consistency within the topic:** Are the same concepts described
  the same way across notes? Are there contradictions?

### 5. Check index ordering

Assess whether the `_index.md` reads like a book top-to-bottom:

- General/foundational notes first
- Related notes grouped together
- Specialized/niche notes last
- If the ordering could be improved, propose a reordering with the
  grouping rationale

### 6. Present findings

Report issues in a numbered list grouped by category:

1. **Flow issues** — structural problems, orphaned thoughts, awkward
   transitions
2. **Format issues** — deviations from `$kb-ingest` standards
3. **Style issues** — deviations from `$kb-style`
4. **Clarity issues** — missing arguments, thin sections
5. **Consistency issues** — contradictions between notes, same concept
   described differently
6. **Ordering** — index reordering suggestions (if any)

For each issue, state: the file, the problem, and a suggested fix.
Ask the user to confirm before making changes.

### 7. Apply fixes

Edit files sequentially (not in parallel) to avoid file-modified
conflicts. Do not change substance — only improve how existing ideas
are expressed.

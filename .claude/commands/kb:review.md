---
description: Review and polish KB notes for clarity, consistency, and impact
arguments: <topic-path>
---

# Knowledge Review Skill

Review existing Zettelkasten notes for readability, consistency, and
learning impact. The goal is to make every note clearer and more
memorable without changing its substance.

Refer to `/kb:ingest` for all formatting and structural standards.

## Workflow

### 1. Load notes

- Glob `topics/<topic-path>/**/*.md` to find all notes
- Read `_index.md` and every note in the topic

### 2. Read-through

Read each note as a whole and assess whether it reads well. Does it
flow naturally from start to finish? Does the structure serve the
content? Are sections in the right order? Does each paragraph earn
its place? Flag anything that feels off — orphaned thoughts,
awkward transitions, sections that don't belong where they are.

### 3. Check format compliance

Verify each note against the standards defined in `/kb:ingest`:
formatting, tables, titles, links, index descriptions, prose style.
List any deviations.

### 4. Check readability and clarity

For each note, assess:

- **Opening paragraph:** Does it say what the thing *is* or *does*
  before explaining why? Can a reader grasp the core concept in the
  first sentence?
- **Vague concepts:** Are any terms or ideas used without being clearly
  defined? Would a reader coming back in 6 months understand this
  without context?
- **Ambiguous phrasing:** Are there sentences with "or" or "and" that
  could be misread? Conditionals that are unclear about when they
  apply?
- **Missing arguments:** Does the note assert something without
  explaining why, when the "why" is not obvious?
- **Thin sections:** Are there sections with only 1-2 sentences that
  feel underdeveloped? Either flesh them out or fold them into another
  section
- **Filler:** Does any sentence add nothing that the reader doesn't
  already know from the preceding text? Cut it
- **Consistency within the topic:** Are the same concepts described
  the same way across different notes? Are there contradictions?

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
2. **Format issues** — deviations from `/kb:ingest` standards
3. **Clarity issues** — vague concepts, ambiguous phrasing, missing
   arguments, thin sections
4. **Consistency issues** — contradictions between notes, same concept
   described differently
5. **Ordering** — index reordering suggestions (if any)

For each issue, state: the file, the problem, and a suggested fix.
Ask the user to confirm before making changes.

### 7. Apply fixes

Edit files sequentially (not in parallel) to avoid file-modified
conflicts. Do not change substance — only improve how existing ideas
are expressed.

---
description: Deep-dive a source and its references, then ingest as one lesson-focused note
arguments: <topic> [source]
---

# Deep Knowledge Acquisition Skill

Capture the *lesson* from a substantive source — a blog post, paper, talk,
chapter, or pasted text — together with what its references add as context.
Produces a single tight Zettelkasten note, reviewed before hand-off.

This is the "lesson over details" path. For quick capture without the
deep-dive phase, use `/kb:ingest`.

## Workflow

### 1. Initialize

- Glob `topics/<topic>/**/*.md` to check if the topic exists
- Read `_index.md` if present to see what's already covered

### 2. Receive Input

Accept any of these forms for the source:

- **URL** passed as the second argument
- **File path** passed as the second argument
- **Inline text** pasted by the user
- **Book reference** typed by the user

If no source is in the arguments, ask: "How would you like to provide the
source? (1) URL (2) Paste (3) Book reference (4) File"

Save the raw input to `/tmp/deep-ingest-input.md` to keep it out of
context. Read from that file for the rest of the workflow. Delete it once
the notes are written.

### 3. Deep-Dive the Source

Read the source as a whole. Extract:

- The **core lesson** the author is trying to land — usually one sentence
- 3–5 **supporting insights** that build the lesson
- Verbatim **quotes** that capture the punchlines, for fact-checking later
- The **list of references** the source cites

Do not write notes yet. This phase is about understanding the source well
enough to restate its lesson without distorting it.

### 4. Deep-Dive the References (in Parallel)

References sharpen the note but are **not** the subject of the note. The
source is the subject; references provide context. Their job is to:

- Confirm formal definitions or claims the source quotes
- Surface concrete examples the source alludes to but does not spell out
- Reveal sister-concepts worth a one-line mention

Fetch up to ~5 substantive references **in parallel** — one tool call per
reference, all in a single message. Skip navigation, social, and footer
links. Ask each fetch only the questions that enrich the lesson, not for
exhaustive coverage.

If a reference clearly carries its own distinct transferable lesson, flag
it to the user — do not silently expand scope.

### 5. Match Existing Notes

Semantically match the lesson against existing notes in the topic. Read
titles and descriptions in `_index.md`, and read any note whose title is
close. If the new content extends an existing concept, prefer merging
into that note over creating a new one.

### 6. Plan the Note(s)

Default to **one tight note** that captures the full lesson. Split into
multiple notes only when the source carries clearly distinct transferable
ideas that would each be linked from different contexts. Atomicity is a
property of the idea, not the file count.

Present the plan to the user before writing:

- Note title and path
- The lesson in one sentence
- The section headings
- A short "what the references add" table mapping reference → section

Wait for the user to approve or redirect.

### 7. Write the Note(s)

Follow all standards from `/kb:ingest` for format, voice, structure,
cross-references, and index updates. In particular:

- Sentence-case title
- ~80 char lines
- Bold for newly introduced terms
- Plain text for technical terms (no backticks in prose)
- Cross-references confined to `## Related` at the bottom
- Lead each section with the claim, then explain
- Footer: `Return to [Topic](_index.md)`
- Update `_index.md` in narrative order, with a short stable description

### 8. Review Pass

After writing, run the equivalent of `/kb:review` on the new note:

- Re-read top-to-bottom for flow
- Check format compliance against `/kb:ingest`
- Check that every section delivers what its heading promises
- Check for vague terms, ambiguous phrasing, thin sections, filler
- Check voice consistency with sibling notes in the topic

Present findings as a numbered list grouped by category. Ask the user to
confirm fixes — they may reject specific phrasings and ask for
alternatives. Iterate until the user is satisfied.

Hand the note back to the user once they sign off. Committing is a
separate, manual step.

## Examples

```
/kb:deep-ingest distributed-systems/concepts https://brooker.co.za/blog/2021/05/24/metastable.html

/kb:deep-ingest practices/sre  (then paste the content)

/kb:deep-ingest languages/rust ~/notes/ownership-chapter.md
```

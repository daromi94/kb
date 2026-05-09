---
description: Record and organize knowledge into atomic Zettelkasten notes
arguments: <topic>
---

# Knowledge Acquisition Skill

Record knowledge into clean, atomic Zettelkasten notes. Each note must be
readable and recallable in under 5 minutes.

## Directory Structure

```
topics/<topic>/
  _index.md         # Topic overview
  <note-slug>.md    # Individual notes
  <subtopic>/       # Optional nested subtopic
```

## Workflow

### 1. Initialize

- Glob `topics/<topic>/**/*.md` to check if topic exists
- Read `_index.md` if present to see what's covered

### 2. Gather Input

Ask: "How would you like to provide content? (1) URL (2) Paste (3) Book reference (4) File"

**Critical:** Save all input to `/tmp/ingest-input.md` before processing. This prevents
raw content from polluting conversation context:

- **URL:** Fetch content, write to `/tmp/ingest-input.md`
- **Paste:** User pastes content, write to `/tmp/ingest-input.md`
- **Book reference:** User provides text, write to `/tmp/ingest-input.md`
- **File:** Copy file contents to `/tmp/ingest-input.md` (or use directly if already a tmp file)

Then read from `/tmp/ingest-input.md` for all subsequent processing steps. Delete the tmp
file after notes are created.

### 3. Match Existing Notes

After receiving content, semantically match against existing notes:

- Read note titles and descriptions from `_index.md`
- For potential matches, read the actual note to assess overlap
- Consider conceptual similarity, not just keyword overlap
- Merge into existing notes when the new content extends the same concept

### 4. Identify Notes

Analyze content for distinct pieces of knowledge. Each note should be
**self-contained** and cover **one thing well**:

- Concept explanation
- Principle or pattern
- Technique or method
- Comparison or analysis

**High-scoring match?** Read that note and merge new content into it rather
than creating a duplicate.

### 5. Process Content

**Remove:** Self-references, filler, redundant explanations, marketing language,
sales pitches (competitive positioning, "unlike X we do Y", "best-in-class",
customer testimonials, pricing/business arguments for adoption),
dated references (version numbers, "as of 2024", "currently", "new in v3",
release-specific features, "modern" without context),
deprecation notes ("deprecated since", "removed in", "replaced by X in v4",
migration advice from old APIs — just document the current approach),
convoluted phrasing, roundabout explanations, unnecessary qualifiers

**Writing style:** Get to the point. Use short, direct sentences. Lead with
the fact or rule, not the context. Say what something *is* or *does* before
explaining why. Avoid hedging ("it should be noted that", "it is worth
mentioning", "one might consider"). Cut filler words ("basically",
"essentially", "in order to", "the fact that"). Prefer active voice.
Each note must be scannable and recallable in under 5 minutes.

**Preserve:** Core explanations, essential examples, tables/comparisons,
code samples, LaTeX notation, depth and nuance — but express them concisely

**Format:** Fix inconsistencies, remove trailing whitespace, no double spaces in
prose (table padding is fine), consistent heading hierarchy, ~80 char lines.
Class/interface names in prose are plain text (Channel, ByteBuf), not
backtick-quoted — reserve backticks for code literals like method calls,
package paths, and inline snippets

**Tables:** Every row must fit on a single line — never wrap a cell across
multiple lines. Condense prose to fit. Pad all cells so columns align. Ensure
space before every `|` in content rows. Separator row has no spaces, just
dashes filling the column width:

```markdown
| Short | Longer header |
|-------|---------------|
| A     | Description   |
| Abc   | More text     |
```

**ASCII diagrams:** Use ASCII box-drawing for architecture/flow diagrams. Show
data flow with arrows and label the operations:

```
+-------------------+
|  Component A      |
|        |          |
|        | operation|
|        v          |
+-------------------+
|  Component B      |
+-------------------+
```

### 6. Fact-Check

Before writing notes, verify claims against trusted sources. Launch a
general-purpose subagent (via the Task tool) with instructions to:

- Identify the key factual claims in the processed content (API names, method
  signatures, default values, behavioral descriptions, class hierarchies)
- Search for the **official documentation**, **Javadocs**, or **GitHub source
  code** for the relevant project — the agent must find these sources itself
- Cross-reference each claim against what the source says
- Return a list of issues found, each with: the claim, what the source says,
  and a link to the source

Present the findings to the user in a numbered list. For each issue, show:
the claim made, what the source says, and the source link. Ask the user if
they want to accept all corrections, reject all, or specify which to reject
by number. Fix accepted issues before writing the notes. If the agent finds
no issues, proceed as-is.

**Skip this step** when the input source is itself authoritative (e.g., the
content was fetched directly from official docs or source code for the same
project being documented).

### 7. Note Format

```markdown
# Note title

Opening paragraph establishing the concept.

## Section

Substantive content. Prose when it serves clarity.

| Comparison | Option A    | Option B    |
|------------|-------------|-------------|
| Aspect     | Description | Description |

**Term:** Definition when introducing vocabulary.

---

Return to [Topic](_index.md)
```

**Titles and headings:** Sentence case at every level — capitalize only
the first word and proper nouns/acronyms. Applies to `#`, `##`, and `###`
headings alike. Examples: "# Consistent hashing", "## Write path",
"### Sequence numbers". Never prefix the H1 title with the parent topic
name; the directory path already provides context ("# Consistency" not
"# Cassandra consistency").

**Link text must match titles:** In `_index.md` entries and
`Return to [...](_index.md)` footers, the link text must match the
target's `# Title` exactly.

Standards: Single blank lines between elements, language tags on code blocks.

### 8. Index File

```markdown
# Topic name

Brief description.

## Subtopics

- [Subtopic](subtopic/_index.md) - Description

## Notes

- [Note name](note-name.md) - Short, stable description

---

Return to [Parent topic](../_index.md)
```

Include Subtopics/Notes sections only when entries exist. Omit the
return link for top-level topics (those directly under `topics/`).

**Descriptions:** Keep descriptions short (3-5 words) and stable. Describe
the note's *topic area*, not its contents or internal structure. Do not
list sections, enumerate sub-concepts, or reveal what the note covers —
that couples the index to the note's internals and goes stale when the
note changes. The title already carries most of the meaning; the
description just disambiguates.

Good: `- [Supervision](supervision.md) - Parent-child fault handling`
Good: `- [Context deep dive](context-deep-dive.md) - Context mechanics in depth`
Bad:  `- [Supervision](supervision.md) - Restart strategies, error types`
Bad:  `- [Context deep dive](context-deep-dive.md) - Scope, thread propagation, W3C headers, Baggage`

**Ordering:** Arrange entries so the index reads like a book top-to-bottom:
general to specific, with related topics grouped together. Overviews and
foundational concepts come first, specialized or niche topics last. When
adding a new entry, insert it at the position that maintains this narrative
flow rather than appending to the end.

### 9. Save and Report

- Create `topics/<topic>/` if needed
- Write notes as `<slug>.md` (kebab-case)
- Update `_index.md` with new entries only
- For nested subtopics, update parent `_index.md`
- Report what was created/updated with brief summaries

### 10. Fixing Issues

When fixing issues across multiple files, edit files sequentially (not in
parallel) to avoid file-modified conflicts. Avoid batch scripts which may break
ASCII diagrams or other structured content.

## Filename Convention

- "WTFs per Minute" -> `wtfs-per-minute.md`
- "Law of Demeter" -> `law-of-demeter.md`
- "Chapter 4: Ownership" -> `ownership.md`

## Examples

```
/ingest practices/clean-code + paste -> Created:
  shutdown-surgery.md - Decommissioning legacy systems
  _index.md - Updated

/ingest languages/java/concurrency + paste -> Created:
  topics/languages/java/concurrency/threads.md
  topics/languages/java/concurrency/executor-service.md
  Updated topics/languages/java/_index.md with subtopic link

/ingest performance/async-io + paste (with match) -> Updated:
  asynchronous-io.md - Added event loop section
  Created blocking.md - When sync I/O fits

/ingest databases/postgres + file ~/notes/postgres-indexes.md -> Created:
  btree-indexes.md - B-tree index structure and usage
  index-only-scans.md - Covering indexes for query optimization
```

---
description: Record and organize knowledge into atomic Zettelkasten notes
arguments: <topic>
---

# Knowledge Acquisition Skill

Record knowledge into clean, atomic notes using Zettelkasten principles.

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

**Critical:** Save all input to `/tmp/kb-input.md` before processing. This prevents
raw content from polluting conversation context:

- **URL:** Fetch content, write to `/tmp/kb-input.md`
- **Paste:** User pastes content, write to `/tmp/kb-input.md`
- **Book reference:** User provides text, write to `/tmp/kb-input.md`
- **File:** Copy file contents to `/tmp/kb-input.md` (or use directly if already a tmp file)

Then read from `/tmp/kb-input.md` for all subsequent processing steps. Delete the tmp
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
release-specific features, "modern" without context)

**Preserve:** Core explanations, illuminating examples, tables/comparisons,
code samples, LaTeX notation, depth and nuance

**Format:** Fix inconsistencies, remove trailing whitespace, no double spaces in
prose (table padding is fine), consistent heading hierarchy, ~80 char lines

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
# Note Title

Opening paragraph establishing the concept.

## Section

Substantive content. Prose when it serves clarity.

| Comparison | Option A    | Option B    |
|------------|-------------|-------------|
| Aspect     | Description | Description |

**Term:** Definition when introducing vocabulary.

## Related

- [Other note](other-note.md) - How it connects

---

Return to [Topic](_index.md)
```

**Cross-references:** Never link to other notes inline within prose or headings.
All cross-references go exclusively in the `## Related` section at the bottom.

Standards: Single blank lines between elements, sentence case headers, language
tags on code blocks.

### 8. Index File

```markdown
# Topic Name

Brief description.

## Subtopics

- [Subtopic](subtopic/_index.md) - Description

## Notes

- [Note name](note-name.md) - One-line description
```

Include Subtopics/Notes sections only when entries exist.

**Ordering:** List entries from general to specific, keeping related topics
together. Overviews and foundational concepts come first, specialized or
niche topics last. When adding a new entry, insert it at the position that
maintains this order rather than appending to the end.

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

### 11. Commits

When asked to commit, use conventional commit format with `docs(kb):` prefix.
One-line message, no co-author.

## Filename Convention

- "WTFs per Minute" -> `wtfs-per-minute.md`
- "Law of Demeter" -> `law-of-demeter.md`
- "Chapter 4: Ownership" -> `ownership.md`

## Examples

```
/kb practices/clean-code + paste -> Created:
  shutdown-surgery.md - Decommissioning legacy systems
  _index.md - Updated

/kb languages/java/concurrency + paste -> Created:
  topics/languages/java/concurrency/threads.md
  topics/languages/java/concurrency/executor-service.md
  Updated topics/languages/java/_index.md with subtopic link

/kb performance/async-io + paste (with match) -> Updated:
  asynchronous-io.md - Added event loop section
  Created blocking.md - When sync I/O fits

/kb databases/postgres + file ~/notes/postgres-indexes.md -> Created:
  btree-indexes.md - B-tree index structure and usage
  index-only-scans.md - Covering indexes for query optimization
```

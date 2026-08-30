---
name: kb-ingest
description: Record supplied material as atomic Zettelkasten notes under topics/, merging overlaps and maintaining each leaf index.
---

# Knowledge Acquisition Skill

Record knowledge into clean, atomic Zettelkasten notes. Each note must be
readable and recallable in under five minutes. Before processing content,
read [kb-style](../kb-style/SKILL.md) completely and apply every rule in it.

## Directory Structure

```
topics/<topic>/
  _index.md         # Plain link list (only for directories that contain notes)
  <note-slug>.md    # Individual notes
  <subtopic>/       # Optional nested subtopic
```

A directory that contains notes gets an `_index.md` (a "leaf index").
A directory that contains only further subtopic directories does not —
discovery there happens via directory listing.

## Workflow

### 1. Initialize

- Use `rg --files topics/<topic>` to check whether the topic exists
- Read `_index.md` if present to see what notes already exist

### 2. Gather Input

Ask: "How would you like to provide content? (1) URL (2) Paste (3) Book reference (4) File"

**Critical:** Create a uniquely named temporary file with `mktemp`, then save all input
there before processing. This prevents raw content from polluting conversation context:

- **URL:** Fetch content and write it to the temporary file
- **Paste:** Write the pasted content to the temporary file
- **Book reference:** Write the provided text to the temporary file
- **File:** Copy its contents to the temporary file, or use it directly if it is already temporary

Read from that file for all subsequent processing. Delete only the temporary file created
for this run after the notes are created.

### 3. Match Existing Notes

After receiving content, semantically match against existing notes:

- Read note titles from `_index.md`
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

**Remove:** Marketing language and sales pitches (competitive positioning,
"unlike X we do Y", "best-in-class", customer testimonials, pricing or
business arguments for adoption), self-references, and redundant
explanations. Also strip everything `$kb-style` rules out —
filler, hedges, convoluted phrasing, dated references, deprecation
language.

**Writing style:** Prose and wording follow `$kb-style` — apply
every rule there. Two ingest-specific checks on top: for each section,
identify in ≤12 words the one thing it says and develop only that; and
keep each note scannable and recallable in under 5 minutes.

**Preserve:** Core explanations, essential examples, tables/comparisons,
code samples, LaTeX notation, depth and nuance — but express them concisely

**Format:** Fix inconsistencies, remove trailing whitespace, no double spaces in
prose (table padding is fine), consistent heading hierarchy, prose lines ≤ 79
characters (tables exempt — they may exceed). Class/interface names in prose
are plain text (Channel, ByteBuf), not backtick-quoted — reserve backticks
for code literals like method calls, package paths, and inline snippets

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

Before writing notes, verify claims against trusted sources. Delegate the
fact-check to an independent subagent when delegation is available and
authorized; otherwise perform the same research directly. In either case:

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

**Link text must match titles:** A note's only links are its
`Return to [...](_index.md)` footer and an `_index.md`'s entries for
its notes; a note never links to another note. In both, the link text
must match the target's `# Title` exactly.

Standards: Single blank lines between elements, language tags on code blocks.

### 8. Index File

```markdown
# Topic name

- [Note name](note-name.md)
- [Another note](another-note.md)
```

The leaf `_index.md` is a plain list of links to the notes in the
directory — no topic blurb, no `## Notes` heading, no parent backlink,
no per-link descriptions. Intermediate directories (those that contain
only further subtopic directories, not notes) do not get an `_index.md`
at all.

**Ordering:** Arrange entries so the index reads like a book top-to-bottom:
general to specific, with related topics grouped together. Overviews and
foundational concepts come first, specialized or niche topics last. When
adding a new entry, insert it at the position that maintains this narrative
flow rather than appending to the end.

### 9. Save and Report

- Create `topics/<topic>/` if needed
- Write notes as `<slug>.md` (kebab-case)
- Update the leaf `_index.md` with new entries only
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
$kb-ingest practices/clean-code + paste -> Created:
  shutdown-surgery.md
  _index.md - Updated

$kb-ingest languages/java/concurrency + paste -> Created:
  topics/languages/java/concurrency/threads.md
  topics/languages/java/concurrency/executor-service.md
  topics/languages/java/concurrency/_index.md - Updated

$kb-ingest performance/async-io + paste (with match) -> Updated:
  asynchronous-io.md - Added event loop section
  Created blocking.md

$kb-ingest databases/postgres + file ~/notes/postgres-indexes.md -> Created:
  btree-indexes.md
  index-only-scans.md
```

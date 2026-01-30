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

Run in parallel:

```bash
python3 scripts/build-index.py          # Build term index
```

- Glob `topics/<topic>/**/*.md` to check if topic exists
- Read `_index.md` if present to see what's covered

### 2. Gather Input

Ask: "How would you like to provide content? (1) URL (2) Paste (3) Book reference"

### 3. Match Existing Notes

After receiving content, extract key terms and check for overlapping notes:

```bash
echo "term1 term2 term3 ..." | python3 scripts/match-notes.py [topic]
```

Returns JSON with matches ranked by score. Notes with score > 0.05 are
candidates for merging rather than creating new files.

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

**Remove:** Self-references, filler, redundant explanations, marketing language

**Preserve:** Core explanations, illuminating examples, tables/comparisons,
code samples, depth and nuance

**Format:** Fix inconsistencies, remove trailing whitespace, consistent heading
hierarchy, aligned tables, ~80 char lines

### 6. Note Format

```markdown
# Note Title

Opening paragraph establishing the concept.

## Section

Substantive content. Prose when it serves clarity.

| Comparison | Option A    | Option B    |
| ---------- | ----------- | ----------- |
| Aspect     | Description | Description |

**Term:** Definition when introducing vocabulary.

## Related

- [Other note](other-note.md) - How it connects
```

Standards: Single blank lines between elements, sentence case headers, language
tags on code blocks.

### 7. Index File

```markdown
# Topic Name

Brief description.

## Subtopics

- [Subtopic](subtopic/_index.md) - Description

## Notes

- [Note name](note-name.md) - One-line description
```

Include Subtopics/Notes sections only when entries exist.

### 8. Save and Report

- Create `topics/<topic>/` if needed
- Write notes as `<slug>.md` (kebab-case)
- Update `_index.md` with new entries only
- For nested subtopics, update parent `_index.md`
- Report what was created/updated with brief summaries

## Filename Convention

- "WTFs per Minute" -> `wtfs-per-minute.md`
- "Law of Demeter" -> `law-of-demeter.md`
- "Chapter 4: Ownership" -> `ownership.md`

## Examples

```
/kb clean-code + paste -> Created:
  wtfs-per-minute.md - Code quality metric
  abstraction.md - Managing complexity
  _index.md - Updated

/kb java/concurrency + paste -> Created:
  topics/java/concurrency/threads.md
  topics/java/concurrency/executor-service.md
  Updated topics/java/_index.md with subtopic link

/kb async-io + paste (with match) -> Updated:
  asynchronous-io.md - Added event loop section
  Created blocking.md - When sync I/O fits
```

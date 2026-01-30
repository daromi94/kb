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

Ask: "How would you like to provide content? (1) URL (2) Paste (3) Book reference"

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

**Remove:** Self-references, filler, redundant explanations, marketing language

**Preserve:** Core explanations, illuminating examples, tables/comparisons,
code samples, depth and nuance

**Format:** Fix inconsistencies, remove trailing whitespace, consistent heading
hierarchy, ~80 char lines

**Tables:** Pad all cells so columns align. Separator dashes must match header
width exactly (not longer):

```markdown
| Short | Longer header |
| ----- | ------------- |
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

### 9. Fixing Issues

When fixing formatting across multiple files, edit each file individually
rather than using batch scripts (which may break ASCII diagrams or other
structured content).

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

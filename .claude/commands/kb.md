---
description: Record and organize knowledge into atomic Zettelkasten notes
arguments: <topic>
---

# Knowledge Acquisition Skill

Record and organize knowledge into clean, atomic notes using Zettelkasten principles.

- `topic`: Topic path (e.g., "clean-code", "java/concurrency", "rust/ownership")

## Directory Structure

```
topics/
  <topic>/
    _index.md           # Topic overview
    <note-slug>.md      # Individual notes
    <subtopic>/         # Optional nested subtopic
      _index.md
      <note-slug>.md
```

## Workflow

### 1. Check Existing Notes

Before gathering input, check if the topic already exists:

- List existing notes in `topics/<topic>/`
- Read the `_index.md` to understand what's already covered
- Keep this context when identifying notes from new content

### 2. Gather Input

Ask how to provide content:

1. **URL** - Fetch from web
2. **Paste** - Content pasted directly
3. **Book** - Ask for book title, chapter, or section

### 3. Identify Notes

Analyze the content and identify distinct pieces of knowledge. Each becomes its own note file. A note can be:

- A concept explanation
- A principle or pattern
- A technique or method
- A comparison or analysis
- A one-pager summary
- Any cohesive chunk of knowledge

The key: each note should be **self-contained** and cover **one thing well**.

**When a matching note exists:** If a piece of knowledge maps to an existing
note (same concept, just more detail or a different angle), update the existing
note rather than creating a new one. Read the existing note first, then merge
the new content into it—adding sections, examples, or details that weren't
there before.

### 4. Process Each Note

**Remove:**
- Self-references ("In this article...", "As mentioned...")
- Filler and padding
- Redundant explanations
- Marketing language

**Preserve:**
- Core explanations and reasoning
- Examples that illuminate the concept
- Tables, comparisons, analogies
- Code samples that demonstrate ideas
- The depth and nuance of the original

**Clean up:**
- Fix formatting inconsistencies
- Remove double spaces and trailing whitespace
- Ensure consistent heading hierarchy
- Align tables properly

### 5. Note Format

```markdown
# Note Title

Opening paragraph establishing the concept or idea.

## Section

Substantive content. Prose is fine when it serves clarity.
Notes can include depth - this isn't about compression to
bullet points, but about removing noise while keeping signal.

### Subsection

More detailed exploration when needed.

| Comparison    | Option A     | Option B     |
| ------------- | ------------ | ------------ |
| Aspect        | Description  | Description  |

**Term:** Definition when introducing vocabulary.

```language
// Code that illustrates the point
```

## Another Section

Continue as needed. The note should feel complete.

## Related

- [Other note](other-note.md) - How it connects
```

**Formatting standards:**
- Single blank line between elements
- No trailing whitespace
- No consecutive blank lines
- Sentence case headers
- Aligned table pipes
- Language on code blocks
- ~80 char soft limit for terminal readability

### 6. Index File

`topics/<topic>/_index.md` for each topic:

```markdown
# Topic Name

Brief description.

## Subtopics

- [Subtopic name](subtopic/_index.md) - One-line description

## Notes

- [Note name](note-name.md) - One-line description
- [Another note](another-note.md) - One-line description
```

Include `## Subtopics` only when nested subtopics exist. Include `## Notes`
only when there are direct notes in the folder.

### 7. Save and Confirm

- Create `topics/<topic>/` folder if needed
- Write new note files to `topics/<topic>/<slug>.md` (kebab-case names)
- Update existing notes when merging new content
- Update `topics/<topic>/_index.md` (add new notes only)
- For nested subtopics, update parent `_index.md` with subtopic link
- Report what was created or updated with brief summaries

## Filename Convention

- "WTFs per Minute" → `wtfs-per-minute.md`
- "Law of Demeter" → `law-of-demeter.md`
- "Chapter 4: Ownership" → `ownership.md`

## Linking

Use standard markdown links for GitHub compatibility:

- `[Note title](note-name.md)` - Same folder
- `[Note title](../topic/note.md)` - Cross-topic

## Examples

```
User: /kb clean-code
[pastes content about code quality metrics and abstraction]

Created topics/clean-code/:
  wtfs-per-minute.md - Measuring code quality by confusion
  abstraction.md - Managing complexity through layered interfaces
  _index.md - Updated
```

Nested subtopic:

```
User: /kb java/concurrency
[pastes content about threads and executors]

Created topics/java/concurrency/:
  threads.md - Units of execution in Java
  executor-service.md - Thread pool abstraction
  _index.md - Updated
Updated topics/java/_index.md - Added subtopic link
```

Updating existing notes:

```
User: /kb async-io
[pastes content about event loops and blocking]

Updated topics/async-io/:
  asynchronous-io.md - Added event loop section
Created topics/async-io/:
  blocking.md - When sync I/O makes sense
  _index.md - Added blocking.md
```

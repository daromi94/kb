---
description: Record insights from reviewing open-source codebases
arguments: <project>
---

# Code Review Insight Skill

Capture insights from reading real codebases — patterns, design decisions,
and implementation techniques worth remembering. Each note focuses on one
transferable lesson grounded in a concrete implementation.

Refer to `/kb:ingest` for all formatting and structural standards (line
width, table style, title casing, prose style, cross-references, etc.).

## Directory Structure

```
topics/code-review/<project>/
  _index.md            # Project overview
  <insight-slug>.md    # Individual insight notes
```

## Workflow

### 1. Initialize

- Glob `topics/code-review/<project>/**/*.md` to check if project exists
- If the project directory does not exist, create it and its `_index.md`:

```markdown
# <Project name>

<One-line description of the project.>

## Notes

---

Return to [Code review](../_index.md)
```

- Add the project to `topics/code-review/_index.md` under `## Subtopics`
- Read existing `_index.md` if present to see what insights are already
  captured

### 2. Gather Input

Ask the user to paste or describe what they observed in the codebase.
Input is always direct observations — what they found interesting,
clever, or worth remembering.

Save all input to `/tmp/code-review-input.md` before processing. Read
from that file for all subsequent steps. Delete it after notes are
created.

### 3. Match Existing Notes

Semantically match against existing insight notes for this project:

- Read note titles and descriptions from `_index.md`
- For potential matches, read the actual note to assess overlap
- Merge into existing notes when the new content extends the same insight

### 4. Identify Notes

Analyze observations for distinct insights. Each note should cover
**one transferable lesson**:

- A design pattern or architectural choice
- A clever implementation technique
- A structural decision and its trade-offs
- An approach to a common problem

**High-scoring match?** Read that note and merge the new observation
into it rather than creating a duplicate.

### 5. Process Content

Apply all content rules from `/kb:ingest` (remove filler, fix format,
preserve depth). Additionally:

- Frame insights as transferable techniques, not project documentation
- Reference specific classes, methods, or source files from the codebase
- Explain *why* the approach works, not just *what* it does

### 6. Note Format

```markdown
# Technique/pattern name

Opening paragraph: what the codebase does, stated as a transferable
technique.

## How <Project> does it

Concrete implementation details. Reference specific classes, methods,
or source files from the reviewed codebase.

## Why it works

The reasoning behind the design. What problem does it solve? What
alternatives exist and why are they worse?

## Takeaway

1-2 paragraphs distilling the general principle. This is what makes
the note useful beyond "I read this source once."

## Related

- [Sibling insight](sibling.md) - How it connects

---

Return to [<Project>](_index.md)
```

**Title:** Names the technique or pattern, not the project. The project
context comes from the directory. Example: "Channel pipeline design"
not "How Netty implements pipelines."

**Cross-references:** Same-directory only, in `## Related`.

### 7. Save and Report

- Write notes as `<slug>.md` (kebab-case)
- Update `_index.md` with new entries in narrative order
- Report what was created/updated with brief summaries

### 8. Fixing Issues

Edit files sequentially (not in parallel) to avoid file-modified
conflicts.

## Examples

```
/kb:code-review redis + paste -> Created:
  topics/code-review/redis/_index.md
  topics/code-review/redis/event-loop-simplicity.md
  Updated topics/code-review/_index.md with subtopic link

/kb:code-review netty + paste (with match) -> Updated:
  topics/code-review/netty/channel-pipeline-design.md - Added section
  Created topics/code-review/netty/zero-copy-patterns.md
```

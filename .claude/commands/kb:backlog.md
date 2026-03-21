---
description: Track and manage topics to learn
---

# Learning Backlog Skill

Manage a learning backlog stored in `BACKLOG.md` at the project root.

## Workflow

### 1. Load

Read `BACKLOG.md` if it exists. If not, create it with an empty structure.
Also, glob `topics/` to know existing topic areas.

### 2. Prompt

Present the current backlog and ask the user what they'd like to do:

1. **Add** — Add a new item
2. **Remove** — Remove an item by number
3. **Prioritize** — Reorder items
4. **Clear done** — Remove all completed items

### 3. Add

Ask the user only **what** they want to learn. A single free-text answer.

Infer the topic from context: the item's subject, existing topics
in `topics/`, and existing sections in `BACKLOG.md`. If a reasonable
match exists, use it. If not, create a new section. Do not ask the user
to confirm the topic — just place it, and they can correct if needed.

Append to the appropriate section in `BACKLOG.md`.

### 4. Remove

Show numbered items. Ask which to remove. Confirm before deleting.

### 5. Prioritize

Show numbered items. Ask the user for the new order or which items to
move. Update the file.

### 6. Clear Done

Remove all items marked `[x]`. Confirm count before deleting.

### 7. Loop

After completing an action, show the updated backlog and prompt again.
Continue until the user says they're done.

## File Format

```markdown
# Backlog

## Topic Name

- [ ] Item title
- [ ] Item title

## Another Topic

- [ ] Item title
```

Items are grouped by topic. New topics go at the end. Items within a
topic are ordered by priority (highest first).

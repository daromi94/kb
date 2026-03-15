---
description: Review and improve existing knowledge base notes for readability, accuracy, and clarity
arguments: <topic>
---

# Knowledge Review Skill

Review existing Zettelkasten notes for readability, accuracy, and format
compliance. This is the counterpart to `/kb` — while `/kb` creates notes,
`/review` audits and improves them.

**Goal:** Every note must be readable and recallable in under 5 minutes.
Notes should be simple, direct, factual, and immediately understandable.

## Workflow

### 1. Load Topic

- Glob `topics/<topic>/**/*.md` to discover all notes
- Read every note and every `_index.md` in the topic
- Build a mental map of the topic's structure, coverage, and
  cross-references

### 2. Audit Notes

Review each note against the checklist below. Collect issues into a
structured report — do not fix anything yet.

#### Writing quality

| Issue               | What to look for                                          |
|---------------------|-----------------------------------------------------------|
| Filler words        | "basically", "essentially", "in order to", "the fact      |
|                     | that", "actually", "simply", "just", "very", "really"     |
| Hedging             | "it should be noted that", "it is worth mentioning",      |
|                     | "one might consider", "arguably", "perhaps"               |
| Passive voice       | "is performed by", "was designed to" — prefer active      |
| Roundabout openings | Sentences that delay the point with throat-clearing       |
| Long sentences      | Sentences over ~25 words that could be split or trimmed   |
| Explaining before   | Context before the fact — lead with what it *is*, then    |
| stating             | explain *why*                                             |
| Redundancy          | Same idea expressed twice in different words              |
| Marketing language  | "powerful", "best-in-class", "seamlessly", "elegant"      |
| Dated references    | Version numbers, "as of", "currently", "new in", "modern" |
| Deprecation notes   | "deprecated since", "removed in", migration advice        |

#### Format compliance

| Rule                  | Spec                                                  |
|-----------------------|-------------------------------------------------------|
| Title case            | Sentence case — only first word and proper            |
|                       | nouns/acronyms capitalized                            |
| Title prefix          | Must not repeat parent topic name                     |
| Opening paragraph     | Must exist, must establish the concept directly       |
| Heading hierarchy     | No skipped levels (`## ` under `# `, not `### `)      |
| Cross-references      | Only in `## Related` — never inline in prose/headings |
| Related link text     | Must match the target note's `# Title` exactly        |
| Return link           | `Return to [Topic](_index.md)` with correct title     |
| Horizontal rule       | `---` before the return link                          |
| Line length           | ~80 chars, no trailing whitespace                     |
| Blank lines           | Single blank line between elements, no double blanks  |
| Code blocks           | Must have language tags                               |
| Table formatting      | Single-line rows, aligned columns, padded cells,      |
|                       | no-space separator row                                |
| Class/interface names | Plain text in prose (Channel, ByteBuf), not backticks |
| Backticks             | Only for code literals: method calls, package paths,  |
|                       | inline snippets                                       |

#### Content quality

| Check             | What to assess                                     |
|-------------------|----------------------------------------------------|
| Atomicity         | One clear concept per note — not two ideas merged  |
| Self-contained    | Understandable without reading other notes first   |
| Scannability      | Can the key point be grasped in a quick scan?      |
| Opening paragraph | Does it immediately tell you what this thing *is*? |
| Accuracy          | Do claims match current official documentation?    |
| Completeness      | Is anything critical about the concept missing?    |
| Depth balance     | Enough depth to be useful, not so much it buries   |
|                   | the core idea                                      |

### 3. Audit Index

Review each `_index.md` in the topic:

| Check             | Spec                                                   |
|-------------------|--------------------------------------------------------|
| Descriptions      | 3-5 words, stable, describe topic area not contents    |
| Description style | Must not list sections, enumerate sub-concepts, or     |
|                   | reveal internal structure                              |
| Ordering          | General to specific, foundational before specialized,  |
|                   | reads like a book top-to-bottom                        |
| Link text         | Must match the target note's `# Title` exactly         |
| Completeness      | Every `.md` file in the directory has an index entry   |
| No dangling refs  | Every index entry points to an existing file           |
| Return link       | Points to correct parent; omitted for top-level topics |
| Subtopics/Notes   | Sections only present when entries exist               |

### 4. Cross-Reference Audit

Across the entire topic:

- Check for **dangling references** — links to files that don't exist
- Check for **missing connections** — notes that should cross-reference
  each other based on conceptual overlap but don't
- Check for **asymmetric references** — note A links to B but B doesn't
  link back to A (this is fine when intentional, flag only when the
  reverse connection would genuinely help the reader)
- Verify all link paths resolve correctly (relative paths, correct
  directory depth)

### 5. Fact-Check

Launch a general-purpose subagent (via the Agent tool) with instructions
to:

- Read all notes in the topic (pass the file paths)
- Identify key factual claims: API names, method signatures, default
  values, behavioral descriptions, definitions, formulas
- Search for **official documentation**, **academic sources**, or
  **authoritative references** for each claim
- Cross-reference each claim against what the source says
- Return a list of issues found, each with: the claim, what the source
  says, and a link to the source

**Skip this step** when the topic notes were originally sourced from
authoritative documentation (ask the user if unsure).

### 6. Present Report

Present findings grouped by category:

```
## Review: <topic>

### Writing issues
1. **<note>.md** — <description of issue> — "<quoted problematic text>"

### Format issues
1. **<note>.md** — <description of issue>

### Content issues
1. **<note>.md** — <description of issue>

### Index issues
1. **_index.md** — <description of issue>

### Cross-reference issues
1. **<note>.md** → **<note>.md** — <description>

### Fact-check issues
1. **<note>.md** — <claim> — Source says: <correction> — <link>

### Improvement opportunities
1. **<note>.md** — <suggestion>
```

Omit empty categories. Number all items globally so the user can
reference them by number.

End with: "Which issues should I fix? (all / none / comma-separated
numbers to accept, or numbers to reject)"

### 7. Fix Accepted Issues

- Edit files **sequentially** (not in parallel) to avoid conflicts
- Apply only the changes the user accepted
- For writing issues: rewrite the problematic text following the rules
  in `/kb` step 5 (Process Content)
- For format issues: fix to match the spec exactly
- For content issues: rewrite or restructure as needed, preserving the
  note's core knowledge
- For index issues: update descriptions, ordering, or links
- For cross-reference issues: add or fix links in `## Related` sections
- For fact-check issues: correct the claim to match the source
- After all fixes, re-read each modified file to verify no new issues
  were introduced

### 8. Commits

When asked to commit, use conventional commit format with `docs(kb):`
prefix. One-line message, no co-author.

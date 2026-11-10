# Note processing

Process supplied notes in the following order. Give brief progress updates between stages and complete the whole pipeline unless the user requests otherwise.

## 1. Ingest and clean up

- Read the source directly and keep it available for comparison. Default to one note unless splitting is requested.
- Use a short sentence-case title and a matching lowercase, hyphenated `.md` filename. Preserve proper names and acronyms.
- Choose the folder by subject.
- Preserve the supplied wording, section order, explanations, examples, and code, except for the cleanup below or requested edits. Make only minimal corrections for definite factual or arithmetic errors, and report them.
- Remove links, citation cards, reference-only lines, and HTML artifacts. Normalize escaped list markers and remove accidentally duplicated export titles. Preserve intentional repetition.
- Remove assistant narration, user references, conversation history, and commentary about source coverage or the research process. For example, remove remarks that a protocol is not described in introductory material or cannot be identified without more evidence.
- State technical facts directly: replace scaffolding such as "the documentation states that X" with X. Preserve substantive history, technical limitations, assumptions, uncertainty, and correctness conditions. Removing source commentary must not introduce guesses about missing mechanisms.
- Check for orphaned citation fragments such as `Documentation`, publisher names, and `+1` after removing links.

## 2. Fix diagrams and math

- Use ASCII diagrams in `text` fences. Move diagrams left and align boxes, arrows, columns, indices, and annotations. Repair disconnected paths and misleading pointers while preserving labels, values, and technical meaning.
- Restore a missing diagram only from information already present in the source. Identify illustrative examples as such and avoid inventing measurements or durations.
- Convert LaTeX to ASCII. Use backticks for inline expressions and `text` fences for displayed formulas. Keep each formula on one physical line, including long summations; diagrams and pseudocode can remain multiline.
- Label every fenced block: `text` for diagrams, state examples, formulas, and pseudocode; the appropriate language for executable code or configuration. Preserve code contents unless a change is requested.
- Keep Markdown tables readable and aligned after notation changes.

## 3. Bold strong messages

- Bold central insights, correctness and safety invariants, important distinctions, and engineering lessons.
- Bold definition labels, trade-off labels, and parallel paragraph labels such as "Cost versus availability." Include these labels even when another sentence in the paragraph is already bold.
- In numbered or bulleted engineering principles, bold the leading principle or first sentence. Keep supporting explanations in regular text.
- Preserve existing emphasis and keep bold markup out of fenced blocks.

## 4. Verify the saved note

- Read the saved file and compare it with the original input. Account for every wording change through requested edits, cleanup, or an explicitly reported correction.
- Check diagram connections and pointers, example values, code contents, and the mathematical meaning of formulas, including signs, bounds, indices, and conditions.
- Check the short title and matching filename, labeled and balanced fences, one-line formulas, selective bolding, table alignment, and remaining citation or meta-commentary fragments.
- Run `git diff --check` and check whitespace in new files too, since untracked files are not included in that command. Keep verification lightweight and appropriate to Markdown changes.
- Report the result, any intentional corrections, and whether changes remain uncommitted.

## Source files and commits

- Keep source files such as `tmp.md` unchanged during processing and out of commits unless explicitly requested.
- Commit only when asked, and include only the requested files. Follow the commit format in `AGENTS.md`.
- Delete a source file only when asked, after verifying that its latest contents have been ingested. Re-read before writing or deleting so edits made during processing are preserved.
- Honor requested ordering, such as committing the current version before making further changes. Leave subsequent edits uncommitted unless their commit is also requested.

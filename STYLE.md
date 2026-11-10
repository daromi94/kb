# Writing style

The reader speaks English as a second language. Make technical explanations easy to follow while keeping their depth.

For supplied notes, preserve the wording and structure. The pipeline in `PROCESSING.md` defines the cleanup to apply.

## Self-contained notes

Each note includes the context, definitions, and explanations needed to understand it on its own.

- Explain the subject directly. Keep assistant narration out of notes: no "I'm Codex/Claude," "I researched this," "I found," or "I organized these ideas."
- Keep personal context out of the content. Do not mention the user, their preferences, or their circumstances.
- Include all relevant context in the explanation itself. Do not refer to earlier conversations or shared history: no "as we discussed before," "we covered this earlier," or "you asked about this previously."
- Explain the subject directly rather than describing what an article or its documentation covers. Keep technical qualifications and assumptions; remove commentary about source coverage or the assistant's access to evidence.

## Explain step by step

- Start with the basic idea or a concrete problem the reader can recognize.
- Introduce technical terms when they become useful, and explain them in place.
- Use small technical examples to show what happens and why.
- Make causal connections explicit: because, so, if, and then.
- Develop one consequence before introducing the next. Keep connected ideas together even when they cross topic boundaries.
- Preserve intermediate reasoning. A compact conclusion is not a substitute for explaining how it follows.

## Keep the reading easy

- Use short paragraphs and familiar, precise words.
- Use bullets for steps, reasons, choices, examples, and consequences when they are easier to read that way.
- Use direct sentences and concrete subjects. Avoid long chains of jargon.
- Remove filler, ceremonial introductions, dramatic wording, repeated summaries, and tangents that do not help the explanation.
- Allow useful repetition when a new example or view improves understanding.
- Use headings that make the reading order visible. No fixed heading sequence or paragraph length is required.
- Bold key messages, engineering principles, definition labels, and trade-off labels. Keep supporting explanations in regular text.

## Make mechanisms visible

Use frequent small ASCII diagrams in `text` fences for flows, relationships, bottlenecks, failure sequences, and before-and-after states.

Small state blocks and calculations are welcome. Tables help compare the same dimensions across alternatives. Explain what a visual reveals without repeating all its contents in prose.

Write formulas in ASCII, with each displayed formula on one physical line inside a `text` fence. Use backticks for inline expressions. Label executable code with its language.

## Ordinary Markdown

Use standard `.md` files with natural paragraph wrapping.

Use short sentence-case titles and matching lowercase, hyphenated filenames. Preserve proper names and acronyms.

Do not include links between notes or links to sources.

Let the subject determine the note's length. The result should feel like a patient technical explanation that is easy to scan, not a compressed reference or a polished essay.

Repeated topics and numbered notes such as `retries-1.md` and `retries-2.md` are welcome. A note can develop several connected ideas. Write first; organize when it helps.

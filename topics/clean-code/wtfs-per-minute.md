# WTFs per minute

The most practical measurement of code quality is not found in static analysis
tools or cyclomatic complexity scores, but in the hallway outside a code review
room. The **WTFs per minute** metric evaluates how often a developer's brain
hits a cognitive "speed bump" while trying to parse the logic.

## The two states of code review

| Feature            | Low WTF/min (clean)                            | High WTF/min (messy)                               |
| ------------------ | ---------------------------------------------- | -------------------------------------------------- |
| Cognitive load     | Low; code reads like well-written prose        | High; requires mental map of 15 different files    |
| Discoverability    | Functions and variables exactly where expected | Logic buried in obscure utility classes            |
| Predictability     | No side effects; functions do what they claim  | A "Getter" might accidentally delete a user        |
| Reviewer reaction  | "Ah, that makes sense."                        | "What was the author thinking?"                    |

## Core drivers of high WTF rates

Several technical patterns consistently trigger high WTF rates:

- **Disinformation:** Naming a list of users `account_string` or using `data1`,
  `data2`
- **The "God" object:** A single class or function that handles everything from
  database connections to UI rendering
- **Hidden state:** Functions relying on global variables or environmental
  factors not passed as arguments
- **Deep nesting:** Arrow-shaped code from `if-else` blocks nested five levels
  deep, forcing the reader to track multiple boolean states
- **Cleverness over clarity:** Using obscure language features or "one-liners"
  that save three lines but take thirty minutes to decode

## Maintaining a low WTF count

Clean code is an act of empathy for the next person who will maintain the
system. It assumes the next developer is someone under a tight deadline who
needs to fix a bug at 3:00 AM.

The goal is **instant mental model synchronization**: the moment a developer
looks at a block of code, they should immediately understand its intent, its
inputs, and its expected output without needing to trace the entire execution
stack.

## Related

- [Triad of maintainability](triad-of-maintainability.md) - The three layers clean code optimizes for
- [Abstraction](abstraction.md) - Primary tool for keeping WTF count low

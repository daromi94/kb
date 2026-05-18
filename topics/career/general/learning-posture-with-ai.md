# Learning posture with AI

Using AI without active intent to learn degrades your engineering
skills. The bug gets fixed, the code ships, and your understanding does
not grow. Over time, your ability to build without AI assistance
weakens.

The fix is to change posture, not to stop using AI.

## The default loop optimizes for shipping, not learning

Paste in a spec or error, accept the diff, ship. The struggle between
problem and solution stops happening. Tools are tuned to close tasks:
product teams are rewarded for merged changes and shorter cycle times,
not for sharper engineers. Friction is where the learning happens, and
defaults have removed it.

Posture, not tool choice, determines the outcome. Engineers who use AI
to ask conceptual questions retain understanding; engineers who
copy-paste output do not. Same model, different result.

## When pure delegation breaks

- **Something breaks.** Generated code crashes the same way human code
  does. Someone on the team has to understand the architecture.
- **The model is confidently wrong.** The only defense against a
  plausible-looking incorrect answer is enough expertise to spot it.
- **The foundation changes.** Code is temporary; systems are permanent.
  Framework upgrades and structural reviews cannot be re-prompted away.
- **You leave the median.** AI is strong on problems solved many times
  before. The hard, undocumented problems still require deep
  understanding.

Delegation is fine for boilerplate, glue code, and throwaway scripts.
The cost is too high for everything else.

## Practices that preserve skill

- **Form a hypothesis first.** Write two or three sentences on what you
  think the problem is before prompting. Use the model's answer to test
  your theory, not replace it.
- **Ask for explanation before code.** In unfamiliar territory, the
  first prompt is "explain how this works, the alternatives, the
  tradeoffs". Request code only after grasping the concepts.
- **Treat AI output like a teammate's PR.** Read it, critique it, push
  back. Tests passing is not sufficient reason to merge.
- **Re-derive by hand occasionally.** Take code the model wrote and
  recreate it from scratch. It is the calibration check that tells you
  how much you have lost.
- **Ask the model to teach what it did.** After a clever function, ask
  what concepts it used and what to read to understand the design
  choice.

Some tools offer modes that use Socratic questioning and pause to make
you write code yourself. They feel slower. That is the point.

## Two metrics: ship and learn

End each session with a question: did I learn anything today, or did I
just close tickets?

"Just closed tickets" is fine occasionally. If it is the answer for
months, cognitive debt is accumulating — capability traded for
present-day speed.

Managers and customers only ask about ship. Learn is on you. Better to
ship 80% of what you could and learn 100% of what you needed, than the
reverse. Over years, those produce very different engineers.

---

Return to [General](_index.md)

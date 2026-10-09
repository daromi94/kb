# Managing up

A manager may be responsible for several projects while seeing only part of what happens in each one. Managing up means giving the manager the information, choices, and feedback needed to support the work.

Clear communication helps both sides coordinate. It makes progress, uncertainty, and needed decisions visible.

## Align on the expected result

First, agree on what the work should achieve:

- Which outcome has priority?
- Which deadline is fixed, and why?
- What tradeoffs are acceptable?
- Which decisions belong to the manager or another owner?

For example, a migration may be intended to reduce operating cost. If the team assumes its main purpose is better performance, it may spend time improving the wrong property.

## Send updates that support decisions

A useful update covers the current state and what happens next:

```text
Goal: migrate customer records

Done:           migration tested on a sample
Next:           test the full dataset
Risk:           a dependent team has not confirmed availability
Decision:       move the date or reduce the first rollout
Recommendation: reduce scope and preserve rollback time
```

The format can be much shorter for routine work. Include enough detail for the manager to understand the consequence of a decision.

## Raise bad news while options remain

If a deadline is at risk, waiting for certainty may leave less time to respond.

Describe:

- What changed.
- What is known and still uncertain.
- The likely impact.
- Possible responses.
- The recommended response and its tradeoff.

"We may miss Friday because the load test exposed a memory problem" is more actionable when paired with an estimate for investigation and a smaller rollout option.

```text
Early signal  -> choices still available -> coordinated response
Late surprise -> fewer choices           -> rushed response
```

Report uncertainty honestly. A risk does not need to be presented as a confirmed failure.

## Ask for feedback and apply it

Ask about a specific behavior:

> Which part of the project update was missing information you needed?

Use the feedback to improve the next update. For example, if the manager says the risks were unclear, explain each risk and its likely impact.

Repeated confusion can also reveal an improvement worth proposing: a shared status summary, clearer ownership, or a regular decision point.

Managing up works best as an exchange. The engineer supplies details from the work; the manager supplies priorities, organizational context, and help with decisions beyond the engineer's scope.

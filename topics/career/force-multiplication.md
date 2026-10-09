# Force multiplication

An engineer can solve a problem directly or make it easier for several people to solve similar problems. Force multiplication is the second kind of contribution.

Examples include a useful tool, a clear explanation, or coaching that lets a teammate handle work independently.

```text
One person's knowledge
          |
   +------+------+------+
   |             |      |
shared tool   teaching  worked example
   |             |      |
   +------+------+------+
          |
several people work more effectively
```

The benefit comes from reuse. It depends on whether others can apply the contribution, so it is not automatically exponential growth.

## Teach the reasoning

Suppose a teammate asks how to debug a slow request. Taking over may resolve this request quickly, but it leaves the method with the same person.

A teaching approach can include:

- Ask which part of the request is slow.
- Explain how to separate waiting time from processing time.
- Help choose a measurement.
- Discuss what the result rules out.

Urgent incidents may require direct action first. A later walkthrough can preserve the lesson.

## Make decisions visible

A design review or code walkthrough is more useful when it explains why a choice was made:

> This queue has a fixed capacity because producers can outpace consumers. When it fills, requests are rejected rather than allowing memory use to grow without a bound.

That reasoning is transferable. Someone can apply it to another queue even if the code is different.

Small examples, recorded decisions, and reusable tools let the explanation reach people who were not in the conversation.

## Give responsibility with support

A growth opportunity needs a real task and clear expectations:

- Define the desired result and important constraints.
- Agree on where help is available.
- Set checkpoints where mistakes can still be corrected.
- Leave room for the teammate to choose an approach.

For example, a teammate might lead a design discussion after reviewing the main tradeoffs with a more experienced engineer.

If every decision still requires approval from the same expert, delegation has moved execution but not much independence.

## Make contributions visible

Give accurate credit in reviews, status updates, and project discussions. Name what the person did and why it mattered.

Specific feedback also helps:

> The rollback steps were tested before release, so the team could recover without improvising during the incident.

For improvement, describe the behavior, its effect, and a possible next step. Discuss criticism privately when appropriate and invite missing context.

Useful multiplication leaves people more capable, with less dependence on the person who originally helped.

# Navigating ambiguity

A request such as "make the service more reliable" gives a direction without defining the problem.

Ambiguity means important details are unclear: the desired outcome, the constraints, the cause, or who can make a decision. Progress begins by identifying which missing detail matters next.

## Turn the request into questions

Start with the situation:

- Which users or operations are affected?
- What failure happens, and how often?
- What evidence is available?
- What result would count as an improvement?
- Which deadlines, costs, or compatibility requirements apply?

For "make the service more reliable," the problem might turn out to be request timeouts during peak traffic. That is more specific than a general desire for reliability.

```text
"Improve reliability"
          |
Which failure affects users?
          |
Timeouts during peak traffic
          |
Measure where requests wait
          |
Choose and test a response
```

The questions guide investigation without assuming the solution in advance.

## Sort the unknowns

Three groups help:

| Group                     | Example                                       | Next action                    |
| ------------------------- | --------------------------------------------- | ------------------------------ |
| Known                     | Timeouts occur during the evening peak        | Record the evidence            |
| Easy to find              | Current timeout and pool size                 | Check the configuration        |
| Decision-changing unknown | Requests wait for connections or slow queries | Collect a targeted measurement |

Focus on unknowns that could change the plan. Confirming that a project is no longer needed can save more work than refining its implementation.

## Ask the right person a precise question

Do initial investigation where possible, then explain the gap:

> The service times out mainly between 6 and 8 p.m. Is preserving the current latency target required during that peak, or is delayed processing acceptable for these operations?

A product owner can answer the acceptable user experience. An operations team may explain traffic patterns. A technical owner may clarify dependencies.

Bring enough context that the person can answer or identify the next owner.

## Write down a working boundary

A short problem statement can include:

- **Observed problem:** checkout requests time out during peak traffic.
- **Known evidence:** waiting time grows when the connection pool is full.
- **Constraint:** the database budget remains unchanged.
- **Success measure:** agree on a target using the current failure rate as a baseline.
- **Open question:** can the request hold a connection for less time?

This is a working model. New evidence can change it.

## Learn through a small step

Complete clarity may require an experiment. Measure one path, test one hypothesis, or prototype one alternative.

Afterward, update the problem statement and decide what comes next. If a new question expands the project, make that scope change explicit.

The aim is enough clarity for the next useful decision, followed by evidence that improves the following one.

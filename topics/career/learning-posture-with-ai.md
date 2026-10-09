# Learning posture with AI

An AI assistant can help complete a task and help explain a subject. Those goals overlap, but they are different.

A generated solution may finish the task while leaving the reader unable to explain it. For learning, the useful question is what understanding remains after the answer is used.

## Choose what needs to be learned

Some work mainly needs a correct result: a routine conversion, repetitive test setup, or a familiar piece of boilerplate.

Other work builds knowledge needed for future decisions:

- Why requests time out under load.
- How a transaction handles partial failure.
- Which assumptions make a concurrent algorithm safe.
- Why one architecture fits the constraints better than another.

Put learning effort where that understanding will be used. There is no need to turn every delegated task into a lesson.

## Start with a small hypothesis

Suppose a service becomes slow when traffic rises.

Before asking for a fix, form a tentative explanation:

> Requests may be waiting for database connections. If that is true, the wait should increase when the connection pool is full.

This connects an idea to observable evidence.

```text
Observed slowdown
        |
tentative explanation
        |
AI helps explore or test it
        |
compare with measurements
        |
revise the explanation
```

The assistant can suggest other causes, explain the pool, or help prepare a measurement. The measurements still need to decide which explanation fits.

## Use explanations actively

Useful prompts focus on a specific gap:

- Explain the request path one step at a time.
- Show a small example where this approach fails.
- Ask questions that reveal a misunderstanding.
- Compare two solutions under the stated constraints.
- Identify which claim in the explanation needs verification.

After reading, try to explain the mechanism without copying the answer. If the explanation gets stuck at a term such as "backpressure," examine that term before adding more complexity.

A small worked example often reveals more than another broad summary.

## Examine generated code as a teammate's proposal

For code that will be maintained, ask:

- Which behavior changed?
- Which assumptions does the implementation make?
- What happens when an operation fails halfway through?
- What do the tests establish, and what do they leave open?
- Can the important path be traced without asking for another summary?

An assistant's explanation can guide this examination. It cannot replace evidence that the implementation behaves as described.

## Practice the decisions that matter

Occasionally solve a small version of a relevant problem without generated code. For example, implement a bounded queue to explore what producers do when it fills.

Then compare approaches. The useful learning is in the differences: blocking, rejection, memory use, cancellation, and shutdown.

Practice need not duplicate an entire production project. A small example can expose the mechanism more clearly.

## Connect learning to future ownership

A useful session leaves something that can be applied again:

- A clearer model of how the system works.
- A tested explanation for a failure.
- An understanding of a tradeoff.
- A question precise enough to investigate.

The assistant supports learning when it helps build and challenge that understanding.

# Cognitive surrender

An AI assistant suggests a code change. The explanation sounds convincing, and the tests pass. The engineer accepts it without checking how it works.

This is **cognitive surrender**: letting the assistant's answer replace the engineer's own judgment.

Without that understanding, the engineer may not know where to look when the code fails or how to change it.

## Use the tool and check its work

**Cognitive offloading** means using a tool to do part of the work. A calculator handles arithmetic. An AI assistant might generate code or suggest tests.

The person using the tool still checks whether the result meets the goal.

```text
Offloading:
AI proposal -> understand it -> check it -> decide

Surrender:
AI proposal -> accept because it looks convincing
```

Both paths can produce code that appears to work. The difference is whether someone understands the important choices and checks them.

## A payment retry example

Suppose an assistant adds retries to a payment request. Retrying seems reasonable: if the request fails, try again.

But a timeout only means the caller did not receive a response in time. It does not establish whether the payment happened.

```text
Payment request
       |
Payment succeeds
       |
Response is lost
       |
Caller sees a timeout
       |
Caller retries
       |
Payment may happen again
```

If the payment service does not recognize the repeated request, the customer could be charged twice.

The engineer needs to ask:

- Can the payment succeed before the caller sees a timeout?
- How does the service recognize a repeated request?
- What prevents a second charge?

The existing tests might cover successful payments without covering a lost response. Passing those tests would leave this failure case unchecked.

The assistant's explanation is a starting point for investigation. The code and tests need to show what actually happens.

## Other ways judgment gets skipped

### Accepting a patch after a quick glance

The code looks reasonable, so it is approved. Nobody follows the changed path or checks what happens when an operation fails halfway through.

### Removing a symptom without understanding it

Increasing a timeout makes a test pass. That may be the right fix, but the reason for the delay remains unclear.

Was the timeout too short? Was the service overloaded? Was the operation stuck? Those explanations lead to different fixes.

### Starting with an assumed solution

The question is "Which cache should be added?" The assistant compares caches.

Before choosing a cache, ask why the operation repeats the same expensive query. Removing unnecessary work could solve the problem more simply.

## Think about the problem before reading the answer

For a difficult problem, write down a few things first:

- A possible cause.
- The behavior that must stay correct.
- Important facts that are still unknown.
- A check that could reveal a mistake.

For the payment example, one requirement is:

> Repeating the same payment request must not create a second charge.

That gives the proposed solution something concrete to satisfy.

If the assistant agrees with the initial explanation, check it anyway. Both may rely on the same mistaken assumption.

Asking for another explanation or a counterargument can reveal useful questions. Investigate those questions through the code, tests, or official documentation.

## Make the change easier to check

- Split a large patch into smaller changes.
- Trace the code paths that changed.
- Test important failure cases.
- Check claims about unfamiliar libraries against their documentation.
- Record why an important design choice was made.

The amount of checking should fit the change. A formatting edit may need a quick look at the diff. Payment retries need checks for duplicate requests and lost responses.

If time pressure or tiredness makes a change hard to follow, reduce its scope or return to the review when concentration improves.

## Be able to explain the result

After using an assistant's work, the person responsible should be able to answer:

- What changed?
- Why should it solve the problem?
- How was it checked?
- What could still go wrong?

If an answer is unclear, examine that part of the change. A small example or a targeted test can help close the gap.

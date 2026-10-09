# Asking questions

Two engineers can read the same requirement and understand it differently.

For "real-time updates," one may expect an update within one second. The other may expect it within five minutes.

```text
Same requirement: "real-time updates"

Engineer A -> within 1 second
Engineer B -> within 5 minutes
```

Both engineers may think the requirement is clear. Asking "How quickly must an update arrive?" reveals the difference before they build different solutions.

Experience helps identify useful questions. It does not remove the need to ask them.

## Give enough context

A useful question explains what the work is and which detail is unclear:

> The service sends an update after each payment. How quickly must it arrive: within one second, or within a few minutes?

The answer affects both the design and the tests. The team can then build the service and check whether updates arrive on time.

For an unfamiliar part of the system, start with a simple explanation of the current understanding:

> It looks like this service stores the payment before sending the update. Is that the correct order?

This gives someone a specific point to confirm or correct.

## Check assumptions

An assumption is something treated as true before it has been checked.

Common assumptions can be turned into questions:

| Assumption                               | Question                           |
| ---------------------------------------- | ---------------------------------- |
| Traffic will stay at its current level   | Is higher traffic expected?        |
| Another team will deliver an API on time | Has the delivery date been agreed? |
| Old data can be deleted                  | Does anyone still need it?         |

Start with assumptions that could change the design or schedule. For example, a late API delivery could delay integration. Checking the date early gives the team time to adjust the plan.

## Explain why the answer matters

A question is easier to prioritize when the consequence is clear:

> The change retries payments after a timeout. Could the first payment have succeeded already? If so, could the retry charge the customer twice?

The caller can see a timeout even after a payment succeeds. The team therefore needs to check how repeated requests are handled.

The question points to a concrete next step: inspect the retry behavior and test what happens when a payment succeeds but its response is lost.

For other questions, the next step may be to read documentation or ask the person responsible for the requirement. Agree on who will find the answer and which decision depends on it.

# Eisenhower matrix

A task can demand attention without contributing much to an important goal. Another task can matter greatly while having no immediate deadline.

The Eisenhower matrix separates two questions:

- **Urgency:** what happens if the task waits?
- **Importance:** how much does the task contribute to a meaningful goal or responsibility?

Urgency depends on timing. Importance depends on the outcome.

## The four combinations

```text
                            Urgency
                  Low                High
             +-----------------+-----------------+
Importance   | Schedule        | Address soon    |
High         | Prevention,     | Incident,       |
             | skill building  | critical date   |
             +-----------------+-----------------+
Importance   | Reduce or drop  | Route, delegate,|
Low          | Low-value work  | or limit effort |
             +-----------------+-----------------+
```

| Combination                 | Typical response                             | Example                                                       |
| --------------------------- | -------------------------------------------- | ------------------------------------------------------------- |
| Important and urgent        | Address it promptly                          | Restore a service that customers cannot use                   |
| Important, less urgent      | Reserve time                                 | Remove the cause of repeated outages                          |
| Less important, urgent      | Check ownership and use proportionate effort | Route a time-sensitive request to the team that can answer it |
| Less important, less urgent | Reduce or remove it                          | Stop preparing a report nobody uses                           |

These categories depend on context. An email about a production risk can be important; an email is not low-value simply because it is an email.

## Protect work that prevents future emergencies

Suppose a service repeatedly runs out of disk space. Deleting old files restores it each time, but the same incident returns.

```text
Repeated emergency
        |
delete files each time
        |
same risk remains
        |
reserve time for retention and alerts
        |
fewer avoidable emergencies
```

Preventive work is easy to postpone because the service currently runs. Scheduling it makes the important task compete with fewer urgent requests.

## Use the matrix as a question

Before choosing a response, ask:

- What happens if the deadline is missed?
- What outcome does this support?
- Is this the right person or team to handle it?
- Can the effort be reduced without losing the needed result?

Delegation requires a suitable owner and enough context. Rest, relationship building, and recovery can also serve important goals; they should not be discarded just because they produce no immediate artifact.

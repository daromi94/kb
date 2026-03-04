# Span anatomy

A span represents one operation within a trace. Every span in a trace
shares the same 16-byte Trace ID. Each span has its own 8-byte
Span ID.

## Fields

| Field      | Description                                       |
|------------|---------------------------------------------------|
| Span ID    | 8-byte identifier for this operation              |
| Trace ID   | Shared across all spans in the trace              |
| Parent     | Set via Context at creation; absent on root spans |
| Attributes | Key-value dimensional metadata                    |
| Events     | Timestamped records with a name and attributes    |
| Links      | References to spans in other traces               |
| Status     | Outcome: UNSET, OK, or ERROR                      |
| Kind       | Role in the trace (CLIENT, SERVER, etc.)          |

**Attributes** attach dimensional metadata to a span — things like
`http.method`, `http.status_code`, or `db.statement`.

**Events** are structured, span-scoped log entries. Each event has a
name, a timestamp, and its own set of attributes. Use them for
discrete occurrences within a span, such as a cache miss or a retry
attempt.

**Status** defaults to UNSET. Set it to ERROR to flag a failed
operation; OK is rarely needed since UNSET already implies success.

## Tree structure and links

Parent-child edges form a tree. Each span has at most one parent. A
span with no parent is the root span.

Links add cross-trace edges on top of this tree. They reference spans
in other traces without establishing a parent-child relationship.
A common use case is connecting a Kafka producer span to its
downstream consumer span. Together, parents and links make the full
structure a directed acyclic graph.

## Java API

Spans are created via the Tracer
(`io.opentelemetry.api.trace.Tracer`). The active span is held in
thread-local storage through the Context API.

## Related

- [Signals](signals.md) - Overview of the three signal types
- [Context and propagation](context-propagation.md) - How trace
  context flows between threads and services

---

Return to [OpenTelemetry](_index.md)

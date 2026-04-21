# Admission controllers

Admission controllers intercept write requests after authentication
and authorization but before persistence. They can modify the
object, reject it, or both — and they are where cluster operators
enforce policy the built-in schema does not capture.

Reads (`get`, `list`, `watch`) bypass admission entirely; policing
reads is the job of authorization.

## Two phases

Admission runs in two ordered phases:

1. **Mutating admission** — controllers may modify the incoming
   object (injecting defaults, sidecar containers, labels).
2. **Validating admission** — controllers may only approve or
   reject (quotas, required labels, privilege checks).

Rejection in either phase aborts the whole request. Between the two
phases the object passes through **schema validation** against the
OpenAPI spec.

## Extension points

Three controllers are extension points for operators:

| Controller                 | Type       | Mechanism                 |
|----------------------------|------------|---------------------------|
| MutatingAdmissionWebhook   | Mutating   | HTTP callout to a webhook |
| ValidatingAdmissionWebhook | Validating | HTTP callout to a webhook |
| ValidatingAdmissionPolicy  | Validating | CEL expression, inline    |

Webhooks run arbitrary logic at the cost of HTTP round-trip latency
on every affected request and an availability dependency — if the
webhook is down, requests queue or fail based on `failurePolicy`.

ValidatingAdmissionPolicy evaluates CEL inline: no callout, no extra
pod, no external dependency. Use it for rules expressible in CEL
(required fields, allowed values, cross-field consistency); reach
for a webhook only when the rule needs state outside the object.

## Related

- [API server](api-server.md) - Where admission sits in the pipeline

---

Return to [Control plane](_index.md)

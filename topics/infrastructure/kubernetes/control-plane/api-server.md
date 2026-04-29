# API server

The API server is the single entry point for a Kubernetes cluster.
Every `kubectl` command, every controller reconciliation, every
kubelet status update arrives here as an HTTP call.

It is not a thin CRUD shim over etcd. Every write walks an ordered
pipeline before being persisted, and every persisted change fans
out as watch events to the rest of the cluster.

## HTTP and the openAPI schema

The API is a plain HTTP server. Any kubectl request can be replayed
with curl and a bearer token. Resources live at REST paths like
`/api/v1/namespaces/default/pods/my-pod`, encoded as JSON by
default. Clients can negotiate protobuf via the `Accept` header for
higher throughput.

The server publishes an **OpenAPI schema** describing every built-in
type and every registered custom type. kubectl fetches this schema
and uses it for:

- Client-side validation — catch `kubectl apply` errors before the
  request leaves the client.
- Autocompletion in `kubectl explain`.
- Structure-aware diffing in `kubectl apply --dry-run`.

Because the schema lives on the server, kubectl works with any
resource type without recompiling — new CRDs and API versions are
picked up automatically.

## Request pipeline

A write request walks an ordered sequence of stages. Any stage
before persistence can reject the request; once persisted, the
change is committed and downstream stages only observe it.

```text
+------------------------------+
| 1. TLS + authentication      |
+------------------------------+
| 2. Authorization (RBAC, etc) |
+------------------------------+
| 3. Mutating admission        |
+------------------------------+
| 4. Schema validation         |
+------------------------------+
| 5. Validating admission      |
+------------------------------+
| 6. Persist to etcd           |
+------------------------------+
| 7. Notify watchers           |
+------------------------------+
| 8. Audit log                 |
+------------------------------+
```

- **Authentication** identifies the caller via client certs, bearer
  tokens, OIDC, or service account tokens.
- **Authorization** decides whether that caller may perform this
  verb on this resource. RBAC is the common implementation.
- **Mutating admission** can modify the object — injecting defaults,
  adding sidecar containers, stamping labels.
- **Schema validation** rejects the mutated object if it no longer
  matches the OpenAPI schema.
- **Validating admission** enforces policy without mutating —
  namespace quotas, naming rules, image provenance.
- **Persist** serializes the object and writes it to etcd.
- **Notify watchers** fans the change out to every active watch on
  this resource kind.
- **Audit** records the request at the configured verbosity.

Read requests (`get`, `list`, `watch`) take a shorter path — they
skip admission entirely, since there is nothing to mutate or
validate.

## Storage and internal versioning

Only the API server reads or writes etcd. Every controller, kubelet,
or external tool goes through the API server instead.

Centralizing access has two payoffs. First, authorization,
validation, and encoding choices live in one place. Second, etcd's
schema or storage format can evolve without any client needing to
change.

On write, objects are:

1. Decoded from whatever API version the client sent.
2. Converted to an **internal, version-neutral representation**.
3. Encoded to the configured storage format — typically protobuf.
4. Persisted under the object's REST path.

Reads run the pipeline in reverse: bytes from etcd are decoded into
the internal representation, then converted to whatever API version
the client asked for. This is why an older API version can be
deprecated in the schema without rewriting any data in etcd —
conversion happens at request time.

## Related

- [Admission controllers](admission-controllers.md) - Stages 3 and 5 in detail
- [Watch API](watch-api.md) - Stage 7 fan-out mechanism
- [API extension](api-extension.md) - Teaching the server new types

---

Return to [Control plane](_index.md)

# API extension

The API server can accept new resource types at runtime — operators
don't need to rebuild or upgrade it to add functionality. Two
mechanisms exist, and both are transparent to clients: once a new
type is installed, kubectl and every other client treat it exactly
like a built-in resource.

## CustomResourceDefinition

A CRD teaches the API server a new type declaratively. The operator
submits a CRD object that names the new type (group, version, kind)
and defines its OpenAPI schema. The API server then serves the type
under `/apis/<group>/<version>/<kind>`, storing its objects in the
same etcd the built-in types use, running them through the same
admission pipeline, and exposing the same watch API.

No separate service to operate.

## APIService (aggregation)

An APIService hands a slice of the API surface to an external
process. The operator registers an APIService pointing at a Service,
and the kube-apiserver forwards every request under that group to
the external server, which implements every CRUD handler itself.

Metrics Server is the canonical example. It serves the Resource
Metrics API from a separate process because CPU and memory samples
do not fit etcd's storage model.

## When to use which

| Aspect         | CRD                             | APIService (aggregation)         |
|----------------|---------------------------------|----------------------------------|
| Storage        | Uses the cluster's etcd         | Extension server chooses its own |
| Implementation | Declarative schema only         | Full custom HTTP handlers        |
| Typical use    | Declarative configuration types | Computed data, non-etcd backends |
| Operational    | No separate service to run      | Separate deployment to operate   |

Default to a CRD. Reach for aggregation when the data does not
belong in etcd — live metrics, computed views, external
integrations.

---

Return to [Control plane](_index.md)

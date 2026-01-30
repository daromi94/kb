# ReplicaSets

A ReplicaSet ensures that a specific number of identical Pods are running at all
times. While you rarely create ReplicaSets directly—Deployments manage them for
you—understanding them is essential for troubleshooting scaling behavior.

## The Reconciliation Loop

A ReplicaSet operates on a continuous reconciliation loop:

1. **Desired state:** How many pods did the user request? (e.g., `replicas: 3`)
2. **Current state:** How many pods with matching labels exist?
3. **Action:** Start more if count is low, terminate extras if count is high

## Components

A ReplicaSet manifest has three main parts:

- **Selector:** Labels used to identify which Pods the ReplicaSet owns
- **Replicas:** The target number of running Pods
- **Pod Template:** The specification used to create new Pods when needed

**Label matching caveat:** A ReplicaSet doesn't care how a Pod was created. If
you manually create a Pod with labels matching a ReplicaSet's selector, the
ReplicaSet will adopt it—and may delete it if already at capacity.

## Version History via ReplicaSets

When a Deployment updates (e.g., image `v1` to `v2`), it doesn't modify the
existing ReplicaSet. Instead:

1. Creates a new ReplicaSet for `v2`
2. Scales `v2` ReplicaSet up incrementally
3. Scales `v1` ReplicaSet down incrementally
4. Continues until `v2` is at full capacity and `v1` is at 0

Running `kubectl get rs` often shows old ReplicaSets with `0` replicas. These
are retained as history, enabling instant rollbacks by scaling an old ReplicaSet
back up.

## ReplicaSet vs Deployment

| Feature         | ReplicaSet                  | Deployment                          |
|-----------------|-----------------------------|-------------------------------------|
| Primary goal    | Maintain specific pod count | Manage lifecycle and versioning     |
| Update strategy | Manual                      | Automated (RollingUpdate, Recreate) |
| Self-healing    | Yes                         | Yes (via ReplicaSet)                |
| Rollback        | No                          | Yes (tracks multiple ReplicaSets)   |

## Related

- [Deployments](deployments.md) - Higher-level abstraction using ReplicaSets

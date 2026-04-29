# Expanders

When more than one node group could satisfy a pending pod, the
Cluster Autoscaler uses an **expander** to pick one. Templates decide
which groups are candidates; the expander decides which of those
candidates gets scaled.

## Strategies

| Strategy      | How it picks                                   |
|---------------|------------------------------------------------|
| `least-waste` | Least idle CPU/memory after scale-up (default) |
| `most-pods`   | Schedules the most pending pods                |
| `least-nodes` | Adds the fewest nodes                          |
| `random`      | Random candidate                               |
| `price`       | Cheapest group (GCE, GKE, Equinix Metal only)  |
| `priority`    | Highest user-assigned priority                 |

`least-waste` is the default. It prefers groups that will leave the
least idle CPU and memory after the new node joins, keeping packing
tight.

`priority` reads integer priorities from a ConfigMap keyed by
node-group name patterns. The common pattern is ranking spot pools
above on-demand pools, so that on-demand is used only when spot
capacity is unavailable.

`price` estimates VM cost against likely utilization. A cheap node
that ends up mostly idle can score worse than a more expensive one
that fills up.

## Chaining

Pass multiple expanders as a comma-separated list. Each acts as a
tie-breaker for the previous:

```bash
--expander=priority,least-waste
```

If the first expander returns a single winner, it's chosen. If it
returns several groups tied at the top, the next expander runs over
those, and so on. A name cannot appear twice in the list.

`priority,least-waste` is a common chain: route scale-ups to the
highest-priority group, and fall back to the least-waste choice only
when several groups share the same priority.

## External decisions

The `grpc` expander delegates the choice to an external gRPC service.
CA sends the pending pods and the candidate node groups; the service
returns the group to scale. This is the escape hatch for decision
logic that doesn't fit the built-in strategies — workload-aware
placement, business rules, or multi-cluster coordination.

## Related

- [Cluster autoscaler](cluster-autoscaler.md) - Scale-up trigger and templates

---

Return to [Autoscaling](_index.md)

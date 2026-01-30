# Scheduling

Kubernetes provides several mechanisms to influence where the scheduler places
Pods, from simple label matching to complex distribution rules.

## Node selection

### nodeSelector (basic)

Simple key-value matching. Pod only schedules on nodes with exact labels:

```yaml
nodeSelector:
  disktype: ssd
```

### Node affinity (advanced)

More expressive than nodeSelector with operators (`In`, `NotIn`, `Exists`,
`DoesNotExist`):

| Constraint type                                   | Behavior                                 |
|---------------------------------------------------|------------------------------------------|
| `requiredDuringSchedulingIgnoredDuringExecution`  | Hard rule; Pod stays Pending if no match |
| `preferredDuringSchedulingIgnoredDuringExecution` | Soft rule; schedules anyway if no match  |

## Inter-Pod affinity

Placement based on where other Pods are running, not node labels.

**Pod affinity:** Keep Pods together. Place a web app in the same zone as its
Redis cache to reduce latency.

**Pod anti-affinity:** Keep Pods apart for high availability. Ensure replicas
never run on the same node so a single failure doesn't take down the service.

**topologyKey:** Scope of the rule. `kubernetes.io/hostname` applies to nodes;
`topology.kubernetes.io/zone` applies to availability zones.

## Taints and tolerations

While affinity attracts, taints repel.

**Taint:** Applied to a node. "I am reserved for special workloads" or
"I am under maintenance."

**Toleration:** Applied to a Pod. "I am allowed to schedule on nodes with this
taint."

**Use cases:** Dedicated nodes for specific teams, GPU-only nodes, marking
nodes under maintenance.

## Topology spread constraints

The most flexible way to ensure high availability. Unlike anti-affinity
(all-or-nothing), topology spread defines how evenly Pods distribute.

- **maxSkew:** Maximum difference in Pod count between any two zones
- **whenUnsatisfiable:** `DoNotSchedule` (hard) or `ScheduleAnyway` (soft)

## Scheduling gates

Put a Pod in a waiting state after creation. The scheduler ignores it until an
external controller (quota manager, security scanner) removes the gate.

Useful when the Pod should exist in the API but isn't ready to be placed.

## Comparison

| Mechanism          | Focus        | Constraint | Primary use case                      |
|--------------------|--------------|------------|---------------------------------------|
| nodeSelector       | Node labels  | Hard       | Specific hardware (SSD, GPU)          |
| Node affinity      | Node labels  | Hard/Soft  | Cloud zones, instance types           |
| Pod affinity       | Other Pods   | Hard/Soft  | Co-locate app and cache for latency   |
| Pod anti-affinity  | Other Pods   | Hard/Soft  | HA (don't put all eggs in one basket) |
| Taints/Tolerations | Nodes        | Repulsion  | Dedicated hardware, node maintenance  |
| Topology spread    | Distribution | Balanced   | Evenly spread across zones/racks      |

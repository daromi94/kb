# Cluster topologies

Running Kubernetes at any size forces a decision: one large cluster
for everything, or many small ones? A typical workload set is a
matrix of applications by environments (dev, test, prod), and the
topology question is how to project that matrix onto clusters. The
choice shapes isolation, cost, operational overhead, and team
access. Most organizations end up with a hybrid.

## Four common patterns

### One large shared cluster

Every workload shares a single cluster. Kubernetes treated as
general infrastructure.

**Pros**

- One control plane, one auth system, one upgrade path
- Lowest operational cost per workload

**Cons**

- A cluster outage takes down everything
- Weak isolation between unrelated apps
- Broad RBAC surface — many teams need access
- Hits the 5,000-node control-plane ceiling, with API-server latency
  and etcd pressure biting well before that

### Many small single-use clusters

One cluster per deployment unit (one application in one
environment). Kubernetes treated as a per-app runtime.

**Pros**

- Small blast radius — one outage affects one unit
- Strong isolation between applications
- Narrow access list per cluster

**Cons**

- Control-plane overhead multiplies with every cluster
- Upgrades, policy, and observability must be solved fleet-wide

### Cluster per application

One cluster holds every environment of a single application.

**Pros**

- The cluster can be tailored to the app (GPU node pools, specific
  CNI, service mesh)

**Cons**

- Dev and prod of the same app coexist, weakening production
  isolation

### Cluster per environment

One cluster per tier (dev, test, prod). All apps coexist within
their tier.

**Pros**

- Production is isolated from dev and test
- Production can be locked down to automated deploys only

**Cons**

- Applications inside the same tier do not isolate from each other
- Poor fit when apps have very different infrastructure needs

## Decision axes

| Axis                     | Favors few large clusters   | Favors many small clusters |
|--------------------------|-----------------------------|----------------------------|
| Isolation / blast radius | Low isolation is acceptable | Strong isolation required  |
| Operational cost         | Minimize overhead           | Willing to pay more        |
| Per-app customization    | Uniform stack fits all apps | Divergent infra needs      |
| Team access              | Shared wide access is fine  | Each team owns its cluster |
| Scale                    | Under 5,000 nodes           | Over 5,000 nodes           |

A common hybrid: two clusters per team (one dev, one prod), or
cluster-per-environment overall with extra dedicated clusters for
workloads that need specialized infrastructure.

---

Return to [Best practices](_index.md)

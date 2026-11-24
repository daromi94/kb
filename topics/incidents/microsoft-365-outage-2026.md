# Microsoft 365 outage (2026)

On November 12, 2026, Microsoft 365 experienced a global outage lasting almost 24 hours, primarily affecting Exchange Online but also disrupting Teams, SharePoint, OneDrive, Copilot and other services.

The incident originated in the networking gateway responsible for handling client connections to these services.

A latent concurrency defect, reduced available capacity, an automatic failover and peak traffic combined to trigger a global cascading failure. At the worst point, more than 80% of the affected gateway servers in North America became unresponsive.

The most interesting aspect of this incident is that **the mechanisms designed to provide high availability became mechanisms for propagating failure.**

## 1. Understanding the architecture

Microsoft 365 operates networking gateways that sit between clients and backend services.

Conceptually, the architecture looks like this:

```text
                 Clients
                    |
                    v
         +---------------------+
         | Traffic Management  |
         +---------------------+
                    |
        +-----------+-----------+
        |                       |
        v                       v
   +---------+             +---------+
   | Gateway |             | Gateway |
   |    A    |             |    B    |
   +---------+             +---------+
        |                       |
        v                       v
    Exchange                  Teams
        |
        v
Backend services
```

The gateway infrastructure is distributed geographically and organized into thousands of capacity units.

```text
              Global traffic management
                          |
      +-------------------+-------------------+
      |                   |                   |
      v                   v                   v
North America          Europe           Asia Pacific
      |                   |                   |
 +----+----+         +----+----+         +----+----+
 |    |    |         |    |    |         |    |    |
CU1  CU2  CU3       CU4  CU5  CU6       CU7  CU8  CU9
```

Each capacity unit contains gateway servers that process incoming connections.

The architecture provides multiple levels of redundancy:

- Server-level redundancy.
- Capacity-unit redundancy.
- Regional redundancy.
- Independent gateway infrastructures.

Under normal circumstances, when a component becomes unavailable, its traffic can be redirected to healthy infrastructure.

However, redundancy relies on two fundamental assumptions:

- **The destination has enough spare capacity to absorb the displaced workload.**
- **The destination is not vulnerable to the same failure mechanism.**

Both assumptions broke down during the incident.

## 2. The latent concurrency defect

In July 2026, an operating system update introduced a performance regression in the connection-processing mechanism of the gateway servers.

The defect involved lock contention inside a Windows process.

Under sufficiently high concurrency, the process consumed excessive CPU and memory resources until the entire server became unresponsive.

The following illustrates a possible contention mechanism, rather than the exact implementation of the defective process.

```text
    Connection requests
             |
             v
 +-----------------------+
 | Concurrent processing |
 +-----------------------+
             |
   +---------+---------+
   |         |         |
   v         v         v
Thread    Thread    Thread
   A         B         C
   |         |         |
   +---------+---------+
             |
             v
         +------+
         | Lock | <-- Contention
         +------+
             |
             v
       Shared state
```

A contended lock effectively introduces a serialization point into an otherwise concurrent system.

As concurrency increases:

- More threads compete for the same shared resource.
- Requests spend more time waiting.
- In-flight operations retain memory for longer.
- Synchronization and scheduling overhead can increase.
- Useful throughput can stagnate or decrease.

The system can eventually spend more resources managing concurrent work than completing it.

### Why newer hardware made the problem worse

Interestingly, newer servers were susceptible to the defect, while older servers were not observed to experience it.

Newer servers had more CPU cores, enabling greater concurrency and consequently greater lock contention. Laboratory testing predominantly used older hardware and different traffic characteristics.

```text
Older hardware

 8 concurrent workers
           |
           v
      Shared lock

 Manageable contention

Newer hardware

 64 concurrent workers
           |
           v
      Shared lock

 Excessive contention
```

_Core counts are illustrative._

This is an example of **negative scalability**: increasing computational resources can expose synchronization bottlenecks and reduce useful throughput.

```text
Throughput
    ^
    |        /  Ideal scalability
    |       /
    |      /
    |     /
    |    /------.
    |   /        \
    |  /          \___  Contention collapse
    | /
    +----^----------------------------> Concurrency
         |
 Saturation point
```

**Adding CPU cores does not necessarily improve the performance of a system whose primary bottleneck is serialized access to shared state.**

## 3. The triggering conditions

The defect remained dormant for more than three months. Its presence alone was insufficient to cause an outage.

Three operational conditions combined to expose it.

| Condition           | Effect                                                        |
| ------------------- | ------------------------------------------------------------- |
| Routine maintenance | Nearly 14% of gateway capacity was unavailable.               |
| Teams failover      | Additional traffic arrived at the Exchange gateway.           |
| Daily traffic peak  | Normal demand increased during North American business hours. |

```text
Maintenance ------------>  Available capacity
                                    | Decreases
                                    v
                             Gateway servers
                                    ^
                                    |
Teams failover ------+       Increases load
                     |              ^
Daily traffic peak --+--------------+
```

The system experienced simultaneous pressure on both sides of the capacity equation.

- Demand increased.
- Available capacity decreased.
- The defect reduced effective processing capacity under concurrency.

These operational conditions would ordinarily have been tolerable. The latent defect made their combination dangerous.

### The capacity problem

Consider a simplified hypothetical fleet:

| Metric                   | Normal operation | Maintenance and failover |
| ------------------------ | ---------------- | ------------------------ |
| Available servers        | 100              | 86                       |
| Incoming requests/sec    | 60,000           | 80,000                   |
| Requests/sec per server  | 600              | 930                      |
| Safe capacity per server | 1,000            | 1,000                    |
| Utilization              | 60%              | 93%                      |

Even though the system remains theoretically within its nominal capacity, it is operating much closer to saturation.

If contention subsequently reduces effective service capacity to 800 requests per second per server, the system becomes overloaded.

The important distinction is between **provisioned capacity and effective capacity**.

A machine may be operational, have available CPU cores and accept connections, yet be incapable of completing work at its expected rate.

## 4. Backlog accumulation and server collapse

Once the concurrency defect was triggered, servers became unable to process requests fast enough.

From a queueing perspective:

```text
lambda > mu
```

Where:

- **`lambda`** is the arrival rate.
- **`mu`** is the effective service rate.

The backlog growth rate becomes:

```text
dQ/dt = lambda - mu
```

**As long as arrivals exceed completions, outstanding work accumulates.**

```text
         Arrival rate
          1,000 req/s
               |
               v
 +---------------------------+
 | R R R R R R R R R R R R R |  Growing backlog
 +---------------------------+
               |
               v
        +-------------+
        | Connection  |
        | processing  |
        +-------------+
               |
               v
           600 req/s
         Service rate

Backlog growth: 400 req/s
```

This is particularly dangerous when queued and in-flight requests consume resources needed to complete existing work.

```text
    Lock contention
           |
           v
Reduced processing rate <---+
           |                | Repeat
           v                |
 Backlog accumulation       |
           |                |
           v                |
  Resource exhaustion       |
           |                |
           v                |
Reduced processing rate ----+
```

This creates a **positive feedback loop**.

Unlike ordinary saturation, where throughput reaches a ceiling, overload collapse can cause throughput to decrease as demand increases.

Eventually, the affected machines became unresponsive.

## 5. The regional cascading failure

The traffic management system detected unhealthy capacity units and redistributed their traffic.

This is normally desirable behavior. However, the remaining servers were susceptible to the same defect.

Consider four capacity units, each capable of safely processing 1,000 requests per second.

### Initially healthy

```text
             3,200 req/s
                  |
  +----------+----+-----+----------+
  |          |          |          |
  v          v          v          v
CU-A       CU-B       CU-C       CU-D
800        800        800        800

          Utilization: 80%
```

### One capacity unit fails

```text
             3,200 req/s
                  |
             +----+-----+----------+
             |          |          |
             v          v          v
CU-A       CU-B       CU-C       CU-D
DOWN       ~1067      ~1067      ~1067

         Utilization: ~107%
```

Traffic redistribution now overloads the surviving units.

### A second capacity unit fails

```text
             3,200 req/s
                  |
                  +-----+----------+
                        |          |
                        v          v
CU-A       CU-B       CU-C       CU-D
DOWN       DOWN       1600       1600

          Utilization: 160%
```

Each failure makes subsequent failures more likely.

The relationship can be expressed as:

```text
rho = lambda / (N * mu)
```

Where `N` represents the number of healthy servers and `mu` represents each server's effective service rate.

During this incident, both `N` and `mu` deteriorated.

```text
   Servers become unresponsive <-----+
                |                    | Repeat
                v                    |
    Available capacity falls         |
                |                    |
                v                    |
    Traffic is redistributed         |
                |                    |
                v                    |
    Load per server increases        |
                |                    |
                v                    |
    Lock contention increases        |
                |                    |
                v                    |
More servers become unresponsive ----+
```

This is a classic **cascading failure driven by load redistribution**.

The traffic management system was making locally reasonable decisions that produced a globally destructive outcome.

## 6. The global cascading failure

Once North America began exhausting its capacity, traffic management redirected requests to other regions.

Those regions contained the same underlying software defect.

```text
Stage 1: Local failure

North America         Europe          Asia Pacific
 [DEGRADED]          [HEALTHY]          [HEALTHY]

Stage 2: Regional failover

North America ------> Europe
      |
      +-----------------------------> Asia Pacific

Stage 3: Failure propagation

North America         Europe          Asia Pacific
  [FAILED]          [DEGRADED]         [DEGRADED]

Stage 4: Global degradation

North America         Europe          Asia Pacific
  [FAILED]           [FAILED]           [FAILED]
```

Within approximately two hours of widespread North American failures, every region had affected servers.

This exposes a fundamental distinction in distributed systems:

**Geographical isolation is not necessarily failure isolation.**

Regions may have independent physical infrastructure while still sharing failure modes through:

- Identical software implementations.
- Identical operating system configurations.
- Shared deployment mechanisms.
- Global traffic management policies.
- Shared workload dependencies.

This is known as a **common-mode failure**.

Geographic redundancy is highly effective against independent failures, such as power outages and hardware failures. It is considerably less effective against a software defect that can be activated by redirected traffic.

The failover mechanism effectively transported the triggering condition from one region to another.

## 7. Why recovery was so difficult

Restoring servers did not immediately restore service.

During the outage, clients continued attempting to establish connections. This created substantial pent-up demand.

When an individual server returned, traffic management exposed it to that demand, causing it to become unresponsive again.

```text
     Waiting clients

C C C C C C C C C C C C C
C C C C C C C C C C C C C
C C C C C C C C C C C C C
            |
            v
     Traffic manager
            |
            v
      +-----------+
      | Recovered |
      | server    |
      +-----------+
            |
            v
        Overload
            |
            v
         Failure
```

This created a **recovery-induced overload loop**.

```text
    Restart server <--------+
           |                | Restart server
           v                |
  Pass health checks        |
           |                |
           v                |
Receive pending traffic     |
           |                |
           v                |
       Overload             |
           |                |
           v                |
   Become unhealthy --------+
```

The recovery automation was effectively fighting the consequences of the traffic management automation.

### Health is not readiness for unrestricted traffic

A health check typically answers whether a server can perform some basic operation.

It does not necessarily establish whether the server can withstand thousands of simultaneous connection attempts.

There are several distinct server states:

```text
+-----------------+
| Offline         |
+-----------------+
         |
         v
+-----------------+
| Running         |
+-----------------+
         |
         v
+-----------------+
| Healthy         |
+-----------------+
         |
         v
+-----------------+
| Warming up      |
+-----------------+
         |
         v
+-----------------+
| Fully available |
+-----------------+
```

Treating these states as equivalent makes recovery fragile.

### Recovery capacity requirements

Recovery also introduces a different capacity requirement from steady-state operation.

Suppose:

```text
Normal arrival rate:     8,000 req/s
Recovered capacity:     10,000 req/s
Accumulated backlog: 6,000,000 requests
```

Only 2,000 requests per second of capacity remain available for clearing the backlog while serving new arrivals.

```text
T_drain = Q / (mu - lambda)
```

In this hypothetical example, draining the backlog takes 50 minutes, assuming constant rates.

A system provisioned merely to handle normal traffic may remain degraded for a considerable period after its infrastructure has recovered.

## 8. How the incident was resolved

The response involved removing competing workloads, correcting the operating system regression and repairing the affected fleet in batches. Microsoft began deploying the corrective update on November 13 at 07:20 UTC.

The server recovery process required two restarts:

```text
   Remove from routing
            |
            v
     Restart server
            |
            v
Install corrective patch
            |
            v
     Restart server
            |
            v
    Return to routing
```

Rather than continuing to restore individual servers while they were exposed to overwhelming connection demand, the recovery was organized around groups of capacity units.

```text
        Traffic management
                 |
      +----------+-----------+
      |                      |
      v                      v
Active group          Recovery group
                        [ISOLATED]
                             |
                             v
                      Repair servers
                       concurrently
                             |
                             v
                       Restore group
```

This approach allowed substantially more capacity to become available together, rather than exposing isolated recovering servers to concentrated demand.

Customer-facing disruption ended at 16:10 UTC on November 13. Monitoring and email backlog processing continued afterward.

## 9. Architectural improvements

The corrective actions address several broader distributed systems design problems.

### Workload isolation through bulkheading

Sharing infrastructure improves resource utilization but creates interference between otherwise unrelated workloads.

```text
Before:

Exchange   -----+
                |
Teams      -----+----> Shared capacity pool
                |
SharePoint -----+

After:

Exchange   ---------> Exchange capacity pool
Teams      ---------> Teams capacity pool
SharePoint ---------> SharePoint capacity pool
```

With workload isolation, one service consuming excessive resources does not automatically exhaust the resources available to another.

The trade-off is lower statistical multiplexing efficiency. Dedicated pools may contain unused capacity while another pool is overloaded.

A compromise is reserved capacity with controlled borrowing.

### Capacity-aware failover

Failover should consider the destination's ability to absorb additional traffic, rather than merely whether it is healthy.

```text
  Incoming failover traffic
              |
              v
+---------------------------+
| Destination has capacity? |
+---------------------------+
              |
     +--------+---------+
     |                  |
    Yes                 No
     |                  |
     v                  v
  Accept           Shed / defer
  traffic            traffic
```

Capacity-aware routing can incorporate:

- Queue depth.
- Connection establishment rate.
- In-flight requests.
- Effective throughput.
- Resource saturation.
- Remaining capacity headroom.

Under extreme conditions, rejecting some traffic is preferable to accepting everything and destroying the remaining healthy capacity.

### Smaller failure domains

Capacity units should provide meaningful boundaries for containing failures.

```text
Large failure domain:

+---------------------------------------+
|   CU1  CU2  CU3  CU4  CU5  CU6  CU7   |
|                                       |
|      Unrestricted redistribution      |
+---------------------------------------+

Smaller failure domains:

+---------+    +---------+    +---------+
| CU1 CU2 |    | CU3 CU4 |    | CU5 CU6 |
| Cell A  |    | Cell B  |    | Cell C  |
+---------+    +---------+    +---------+
     |              |              |
     +--------------+--------------+
                    |
        Controlled redistribution
```

Cell-based architectures deliberately restrict the blast radius of failures.

The objective is not to prevent every failure, but to prevent a local failure from becoming a systemic one.

### Gradual traffic ramp-up

Recovering servers should receive traffic progressively.

```text
Traffic allocation
100% |                          +-------
     |                          |
 75% |                  +-------+
     |                  |
 50% |          +-------+
     |          |
 25% |    +-----+
     |    |
  0% +----+------------------------------> Time
```

**Traffic increases only when the server demonstrates sustained stability.**

This allows recovery automation to behave as a stabilizing feedback mechanism rather than an amplifying one.

### Production-representative testing

Testing should explore combinations of operational conditions, not merely individual failure scenarios.

```text
Test dimensions

  Hardware generations
            +
      Peak traffic
            +
    Reduced capacity
            +
 Cross-workload failover
            +
    Connection storms
            +
 Concurrent maintenance
```

A deployment that survives normal traffic for months is not necessarily safe under rare combinations of conditions.

Progressive deployment reduces immediate deployment risk, but it cannot guarantee that latent defects have been exercised.

## 10. Fundamental engineering lessons

| Principle         | Lesson                                                                       |
| ----------------- | ---------------------------------------------------------------------------- |
| Redundancy        | Additional replicas do not guarantee independent failure modes.              |
| Failover          | Redirecting traffic transfers load, not just responsibility.                 |
| Capacity planning | Effective capacity matters more than nominal capacity.                       |
| Concurrency       | More parallelism can produce lower throughput.                               |
| Queue management  | Unbounded outstanding work can contribute to resource exhaustion.            |
| Admission control | Rejecting excess work can preserve useful throughput.                        |
| Fault isolation   | Sacrificing local availability can protect global availability.              |
| Recovery          | Recovery workloads differ from steady-state workloads.                       |
| Automation        | Independent control loops can interact destructively.                        |
| Testing           | Compound failure scenarios expose defects that isolated tests miss.          |
| Rollback          | Old changes must remain diagnosable and reversible.                          |
| Headroom          | Spare capacity is a reliability mechanism, not merely unused infrastructure. |

## 11. The incident as a systems problem

The complete causal chain can be summarized as:

```text
Latent software defect
           +
   Reduced capacity
           +
Cross-workload failover
           +
      Peak demand
           |
           v
    Lock contention
           |
           v
Throughput degradation
           |
           v
 Backlog accumulation
           |
           v
  Resource exhaustion
           |
           v
    Server failure
           |
           v
Regional redistribution
           |
           v
 Regional degradation
           |
           v
 Global redistribution
           |
           v
     Global outage
           |
           v
 Reconnection pressure
           |
           v
   Recovery collapse
```

The underlying software defect explains why servers failed.

The architecture explains why the failure became global.

The recovery mechanisms explain why the outage lasted so long.

**A resilient distributed system must be designed not only to survive component failures, but also to remain stable while capacity disappears, traffic moves, queues accumulate and infrastructure recovers.**

# Topology

Topology is the "map" of a network, describing how nodes (computers, routers,
switches) connect and how data moves between them. The chosen layout affects
traffic flow, cost, and what happens when a link fails.

## Physical vs logical

| Aspect    | Physical Topology              | Logical Topology                     |
|-----------|--------------------------------|--------------------------------------|
| Describes | Actual cables, wires, hardware | How data travels through the network |
| Focus     | Physical layout                | Data flow paths                      |

The two can differ. A network might be physically wired as a star (all devices
connect to a central switch) but logically behave as a bus (data broadcast to
all nodes).

## Point-to-Point

A dedicated link between exactly two endpoints.

No addressing is needed because there is only one possible recipient. Think of
two servers connected by a crossover cable, or a dedicated fiber link between
data centers.

When you call `net.Dial("tcp", "1.2.3.4:80")`, you create a logical
point-to-point connection over a more complex physical network.

- **Pros:** Maximum bandwidth, zero contention
- **Cons:** Not scalable—connecting $N$ computers requires $\frac{N(N-1)}{2}$ cables

## Daisy chain

Nodes connected in series, one after the other. If Node A wants to talk to
Node C, data must pass through Node B. A linear chain has a beginning and end;
connect them, and it becomes a ring.

- **Pros:** Easy to add nodes, low cabling cost
- **Cons:** High latency (each hop adds delay), middle node failure severs chain

## Bus

Every node attaches to a single shared communication line called the backbone.
When a node sends a message, it travels down the cable in both directions.
Every node hears it, but only the one with the matching address processes it.

Terminators are required at both ends to prevent signal bounce.

- **Pros:** Cheapest, requires the least cable
- **Cons:** Collision domain (simultaneous transmissions crash), backbone break
  kills entire network—old Ethernet (10Base2) worked this way

## Ring

Each node has exactly two neighbors, forming a continuous loop. Data usually
travels in one direction. To prevent collisions, many rings use token
passing—you can only transmit if holding the virtual token.

- **Pros:** No collisions, better than bus under heavy load
- **Cons:** Single node or cable failure kills the ring—dual rings (like FDDI)
  fix this with a backup loop in the opposite direction

## Star

The dominant modern topology. All nodes connect to a central hub or switch.

Modern switches are intelligent—they learn which MAC address is on which port
and send data only to the intended recipient rather than broadcasting.

- **Pros:** Fault isolation—one node's cable failure doesn't affect others
- **Cons:** Single point of failure (switch), requires more cabling than bus or
  ring

## Mesh

Every node can connect to any other node. Two flavors exist:

**Full Mesh:** Every node has a direct connection to every other node. Connecting
$N$ nodes requires $\frac{N(N-1)}{2}$ connections (10 servers = 45 connections,
1000 servers = 499,500). Ultimate fault tolerance and lowest latency, but
physically impossible to scale with hardware.

**Partial Mesh:** Most nodes connect to several others, but not all. This is how
the Internet works. Data hops through the most efficient path; if one path is
congested or broken, the network routes around it. Requires complex routing
logic (BGP, OSPF) to determine paths.

## Comparison

| Topology       | Best For                | Fault Tolerance        | Scalability |
|----------------|-------------------------|------------------------|-------------|
| Point-to-Point | Direct server links     | High (for that link)   | None        |
| Daisy Chain    | Simple peripheral setup | Very Low               | Moderate    |
| Bus            | Legacy/cheap setups     | None                   | Low         |
| Ring           | High-load coordination  | Low (unless dual-ring) | Moderate    |
| Star           | Modern LANs / Wi-Fi     | High (per node)        | Very High   |
| Full Mesh      | Critical infrastructure | Highest                | Very Low    |
| Partial Mesh   | Internet / WAN          | High                   | High        |

---

Return to [Fundamentals](_index.md)

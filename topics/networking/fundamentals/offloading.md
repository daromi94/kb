# Offloading

Handling expensive tasks is a primary reason for using the client-server model.
Modern mobile apps and web services depend on **offloading** heavy workloads to
powerful servers.

## Computation Offloading

Expensive tasks like 3D rendering, complex simulations, or AI model inference
require significant CPU/GPU power and RAM.

**The Problem:** Running a high-end video game or LLM on a low-end smartphone
would overheat the device, drain the battery, and likely crash the app.

**The Solution:** The "thin" client sends task parameters to a "fat" server in a
data center. The server does the heavy lifting and returns only the final
result.

## Resource Pooling

Servers use enterprise-grade hardware far more powerful than consumer devices.

- **Shared Cost:** Instead of every user buying a $5,000 workstation for
  occasional tasks, a company buys one powerful server that 1,000 users share
- **Specialized Hardware:** Servers can house TPUs for AI or massive NVMe arrays
  that standard laptops cannot accommodate

## Data Locality

Sometimes a task is expensive because of data volume (searching petabytes of
logs).

**The Efficiency:** Sending a small search query to where data already lives is
much faster than downloading 100GB to your phone just to find one line of text.

## Scaling Strategies

When tasks overwhelm a single server, the architecture allows two scaling types:

| Strategy   | Description                                                  |
|------------|--------------------------------------------------------------|
| Vertical   | Upgrade existing server (more RAM, faster CPU, better NICs)  |
| Horizontal | Add more servers with a load balancer to distribute requests |

## Example: Cloud Gaming

Cloud gaming (Xbox Cloud, GeForce Now) demonstrates offloading in action:

```
+------------------+                    +---------------------+
|  Client (Tablet) |                    |  Server (Data Ctr)  |
|                  |   controller       |                     |
|  Display video <-+--- inputs -------->|  Render 4K @ 60fps  |
|  stream only     |<-- video stream ---|  Full game engine   |
+------------------+                    +---------------------+
```

The client handles only input capture and video display. The server runs the
entire game engine and renders graphics that the client hardware could never
produce locally.

## Related

- [Client-Server](client-server.md) - The architecture that enables offloading

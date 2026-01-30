# Client-Server Architecture

In client-server architecture, tasks are partitioned between two components: the
**client** (service requester) and the **server** (service provider). Unlike
peer-to-peer networks where every machine is equal, this model is inherently
asymmetric. The server sits in a passive state listening for requests, while the
client actively initiates communication.

## Core Components

**The Client:** A user-facing device or application (web browser, mobile app,
terminal). Handles the presentation layer, rendering the UI and capturing user
input.

**The Server:** A machine or process (Apache, MySQL) that hosts, delivers, and
manages resources. Waits for requests, processes them, and sends responses.

**The Network and Protocol:** The connection between them. Both must agree on
rules like HTTP/HTTPS for web traffic or FTP for files.

## Request-Response Cycle

The interaction follows a strict pattern:

1. **Request:** Client sends a message to a specific server address (IP/Port)
2. **Processing:** Server validates the message, executes business logic or
   queries a database
3. **Response:** Server sends the result (data, status code, or error) back

## Architecture Tiers

As systems grow complex, architecture is split into tiers to separate concerns:

| Tier    | Description                                               | Use Case              |
| ------- | --------------------------------------------------------- | --------------------- |
| 1-Tier  | Client, logic, and data on one machine                    | Local apps (MS Access)|
| 2-Tier  | Direct client-to-server (database) communication          | Simple enterprise     |
| 3-Tier  | Adds middle tier (app server) between UI and data         | Modern web apps       |
| N-Tier  | Multiple layers (load balancers, caching, microservices)  | High-scale systems    |

## Benefits

- **Centralized Management:** Security, backups, and updates handled in one
  place
- **Scalability:** Upgrade server hardware or add servers (horizontal scaling)
  without changing clients
- **Resource Sharing:** Many clients access the same data or expensive hardware
  simultaneously

## Drawbacks

The main risk is a **single point of failure**. If the central server goes down,
the entire system is paralyzed for all clients.

## Related

- [Offloading](offloading.md) - Why servers handle expensive tasks
- [RPC](rpc.md) - Making remote calls feel local

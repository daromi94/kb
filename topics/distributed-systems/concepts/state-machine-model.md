# State machine model

A distributed system is a collection of collaborating, concurrent
components that communicate with one another by sending and receiving
messages over a network.

It can be modeled as a state machine: a sequence of states, with each
step transitioning the system from one state to the next.

## Components and network

The system has two kinds of state holders:

- **Components.** Each has exclusive access to its own local state.
  Other components cannot read or modify it directly.
- **The network.** Holds its own local state, including in-flight
  messages.

Components communicate only by sending and receiving messages over
the network.

## Steps

The system proceeds in discrete steps. Each step is taken by either a
component or the network, and falls into one of two categories:

- **External steps.** Sending or receiving a message.
- **Internal steps.** Local computation or local state access.

At any moment, exactly one component or the network completes exactly
one step; the system's behavior is the resulting sequence of states.

## Related

- [Overview](overview.md) - Definition and motivation
- [Emergence](emergence.md) - Global behavior from local rules

---

Return to [Concepts](_index.md)

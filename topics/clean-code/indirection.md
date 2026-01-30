# Indirection

Source: Codely

Indirection is the ability to reference something using a name, identifier, or
container instead of the value itself. In software engineering, it is the act
of adding a layer between a requester and a provider to decouple them.

The "fundamental theorem of software engineering," often attributed to David
Wheeler, states:

> "We can solve any problem by introducing an extra level of indirection."
>
> (To which many add: "...except for the problem of too many levels of
> indirection.")

## The mechanism

At its core, indirection replaces a direct link with an intermediate step.
Instead of **A -> B**, the structure becomes **A -> Map -> B**.

| Component     | Direct access                                    | Indirect access                                  |
| ------------- | ------------------------------------------------ | ------------------------------------------------ |
| The pointer   | Actual value stored at memory address            | Memory address stores the address of the value   |
| The name      | Hardcoding an IP address (`192.168.1.1`)         | Using a hostname (`database.local`) via DNS      |
| The reference | Function calls a specific class implementation   | Function calls an interface/abstract class       |

## Common examples

### Pointers and references

In low-level programming (like C), a pointer is the purest form of indirection.
Instead of passing a massive data structure, a small memory address is passed.
This allows multiple parts of a program to share and modify the same data
without duplicating it.

### Domain Name System (DNS)

The internet relies on indirection. If a web server's IP address changes, the
entire world doesn't need to update their bookmarks. DNS allows a human-readable
name to point to a changing numerical address.

### Virtualization and containers

A VM or container provides indirection between software and hardware. The
application "thinks" it's talking to a physical CPU and RAM, but it's actually
talking to a hypervisor that manages those resources.

### File descriptors (Unix/Linux)

When a process writes to a file, it doesn't talk to the disk directly. It uses
a file descriptor (an integer). The kernel uses this integer as an index into
a table to find the actual file or socket. This allows the same "write" command
to work for a local file, a network pipe, or a terminal.

## Indirection vs abstraction

While often used together, they serve different logical purposes:

- **Abstraction** hides complexity (the "how"). It focuses on the interface.
- **Indirection** provides flexibility (the "where" or "which"). It focuses on
  the mapping.

If a function uses an interface `Shape` to call `draw()`, it uses abstraction
to not care if it's a circle or square. It uses indirection because the actual
implementation is determined at runtime (dynamic dispatch).

## Why use indirection

Indirection facilitates clean code through:

- **Decoupling:** The caller doesn't need to know the specific identity of the
  callee, only the intermediary
- **Late binding:** Decisions about which resource to use can be delayed until
  the program is running
- **Extensibility:** New implementations can be swapped in by updating the
  mapping layer without changing core logic
- **Security:** By providing a proxy or handle instead of direct access, a
  system can intercept, validate, or log requests

## The cost: abstraction penalty

Every level of indirection comes with trade-offs:

1. **Performance overhead:** Following a pointer or looking up a value takes
   CPU cycles. In high-performance systems (game engines, HFT), "pointer
   chasing" is often avoided to stay within CPU cache
2. **Increased complexity:** Too much indirection makes code hard to follow.
   A developer might click through five interfaces and three proxies before
   finding the code that actually performs work
3. **Memory usage:** Each layer requires storage for references, handles, or
   mapping tables

## Related

- [Abstraction](abstraction.md) - Hides complexity; indirection provides flexibility
- [Polymorphism](polymorphism.md) - Dynamic dispatch is a form of indirection

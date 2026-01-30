# Shutdown surgery

Shutdown surgery is a specialized engineering pattern for decommissioning or
drastically refactoring high-stakes legacy systems. It describes the process
of systematically removing a service, module, or database while it is still
"live" or critical to other operations, without causing systemic failure.

If a system is tightly coupled, shutdown surgery is impossible; if it is
well-architected, the surgery is routine.

## The surgical protocol

A successful shutdown surgery follows a strict sequence:

| Phase              | Action                                                            | Goal                                                      |
| ------------------ | ----------------------------------------------------------------- | --------------------------------------------------------- |
| 1. Isolation       | Wrap the legacy system in an indirection layer (interface/proxy)  | Stop the rest of the app from talking directly to legacy  |
| 2. Shadowing       | Route traffic to both old and new systems simultaneously          | Compare results to ensure new logic is accurate           |
| 3. Traffic shifting | Incrementally move read/write requests to the new system          | Validate performance under real-world load                |
| 4. Amputation      | Physically remove dead code, dependencies, and configuration      | Reclaim resources and reduce cognitive load               |

## Core principles

### Decoupling the "patient"

Before surgery begins, any direct dependencies must be broken. This often
involves creating a **shim** or **adapter**. By coding to an interface rather
than the specific legacy implementation, the "surgeon" can swap underlying
logic without calling systems ever knowing a change occurred.

### Feature flags and kill switches

Modern shutdown surgery relies on feature flags. This allows "dark launching"
the replacement logic. If the new system fails during surgery, the flag can
be flipped back instantly, acting as a digital tourniquet to stop the "bleeding"
(outages).

### Handling hidden side effects

The most dangerous part of shutdown surgery is discovering hidden dependencies:

- **Database triggers:** Logic living in the DB rather than the code
- **Cron jobs:** External scripts expecting a specific file or table to exist
- **Shared state:** Global variables or caches the legacy system was silently
  maintaining for others

## Failed surgery symptoms

A "high-WTF" shutdown happens when code is simply deleted without proper
isolation:

- **Fragile systems:** Deleting a "useless" function causes a crash in a
  completely unrelated module
- **Zombie code:** Code technically still in the repo but "disconnected" from
  the main flow, confusing future maintainers
- **The Chesterton's fence dilemma:** Developers afraid to remove code because
  they don't understand why it was put there in the first place

## The bridge replacement analogy

Replacing a major highway bridge while traffic is still flowing is the physical
version of shutdown surgery. You don't just blow up the old bridge. You build a
temporary bypass (indirection), move the cars over (traffic shifting), tear down
the old structure (amputation), and finally move traffic onto the permanent new
bridge.

## Related

- [Indirection](indirection.md) - The isolation layer that makes surgery possible
- [Abstraction](abstraction.md) - Clean interfaces enable safe decommissioning

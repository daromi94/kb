# Shared memory

Shared memory is an IPC technique where the OS intentionally breaks process
isolation to allow multiple processes to access the same region of physical
RAM.

## Process isolation (the default)

Every process believes it's the only program in existence:

**Virtual memory:** OS gives Process A a fake map of memory. When it puts data
at "Address 100", it goes to a specific spot in physical RAM.

**Isolation:** If Process B also writes to "Address 100", the OS redirects that
to a completely different spot in physical RAM.

Process A and Process B cannot see each other's data. This prevents crashes and
security issues.

## Breaking isolation

The OS takes a specific block of physical RAM and maps it into the virtual
address space of both processes:

1. Process A has pointer `0x5000` that leads to physical RAM frame #99
2. Process B has pointer `0x8000` that also leads to physical RAM frame #99
3. If Process A writes to `0x5000`, the change appears instantly at Process B's
   `0x8000`

## Why it matters

Fastest form of Inter-Process Communication (IPC) possible:

**Zero copy:** Data isn't moved from one buffer to another. It stays in place;
just the "viewers" change.

**Large data:** Transferring a 4GB video between programs by copying takes
seconds. With shared memory, you pass the pointer. Takes microseconds.

## The catch: race conditions

If two processes write to the same memory location simultaneously, data becomes
corrupted.

**The fix:** Locks or semaphores coordinate who touches the memory when.

## Comparison

| Method        | Analogy                       | Speed   | Safety                      |
|---------------|-------------------------------|---------|-----------------------------|
| Pipes/Sockets | Emailing an attachment (copy) | Slow    | Safe (OS manages)           |
| Shared Memory | Editing a live Google Doc     | Instant | Risky (manual coordination) |

## Application to io_uring

The Submission Queue and Completion Queue are regions of RAM that both the
application and Linux kernel have mapped as shared memory:

- App writes a request
- Kernel reads that same memory location
- No expensive syscalls needed to pass data back and forth

## Related

- [io_uring](io-uring.md) - Uses shared memory for ring buffers
- [Zero copy](zero-copy.md) - Related optimization technique

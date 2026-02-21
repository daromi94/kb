# Virtual memory

Each process gets a virtual address space — a contiguous range of
addresses that looks like private, dedicated memory. The process
doesn't know where its data physically resides, or whether it's in
RAM at all (it could be swapped to disk). The kernel and the CPU's
Memory Management Unit (MMU) maintain the illusion.

## Why the kernel lies

**Isolation.** Virtual addresses in Process A map to different
physical locations than those in Process B. Neither can see or
modify the other's memory.

**Security.** The kernel doesn't map its own physical pages into a
process's page tables, so user-space code cannot overwrite kernel
memory.

**Efficiency.** The kernel can grant virtual address space without
immediately backing it with physical RAM. Physical pages are
assigned on first access (demand paging), not at allocation time.

## From malloc to physical memory

`malloc()` is a userspace library function (glibc), not a system
call. It manages an internal pool of previously allocated and freed
memory. Most calls are satisfied entirely in userspace from this
pool. Only when the pool is exhausted does the allocator request
more virtual address space from the kernel via `brk(2)` or
`mmap(2)`.

When the kernel handles a `brk(2)` or `mmap(2)` call, it updates
the process's Virtual Memory Areas (VMAs) — kernel data structures
(`vm_area_struct`) that record which virtual address ranges are
valid and their permissions. No physical pages are allocated yet.

When the process first accesses an address in the new range, the
MMU finds no page table entry and raises a **page fault**. The
kernel's page fault handler then allocates a physical page and
installs the mapping in the hardware page tables.

## Resource limits

The kernel enforces `RLIMIT_AS` (total address space) and
`RLIMIT_DATA` (data segment size) at `brk(2)`/`mmap(2)` time, set
via `ulimit`. Cgroup memory limits are enforced at page fault time
when physical memory is actually committed.

## Related

- [Processes](processes.md) - Process creation and the virtual
  address space each process receives
- [Segmentation faults](segmentation-faults.md) - What happens
  when a process violates memory rules
- [User and kernel space](user-and-kernel-space.md) - The
  privilege boundary that system calls cross

---

Return to [Linux](_index.md)

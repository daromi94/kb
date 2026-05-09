# Address space layout

A process's virtual address space is divided into segments that
separate code, static data, and dynamic data from each other.

```text
High addresses
+------------------------+
|          Stack         | grows downward
|            |           |
|            v           |
|                        |
|            ^           |
|            |           |
|          Heap          | grows upward
+------------------------+
|          BSS           | uninitialized globals/statics
+------------------------+
|          Data          | initialized globals/statics
+------------------------+
|          Text          | executable instructions
+------------------------+
Low addresses
```

## Text

Contains the executable machine instructions. Mapped read-only so
a bug cannot overwrite the program's own code. When multiple
instances of the same program run, the kernel can map them to the
same physical pages for the text segment — saving RAM without
sacrificing isolation.

## Data and BSS

The **data** segment holds global and static variables with
explicit initial values (`int count = 10;`). The **BSS** segment
holds global and static variables that are zero-initialized or
have no initializer (`static int buffer[1024];`). The kernel
zeroes BSS pages on first access so the binary only needs to
store the segment's size, not a block of zeroes.

## Heap

Used for dynamic memory allocation at runtime (`malloc`,
`new`). Starts at the end of BSS and grows upward toward higher
addresses. The allocator requests more address space from the
kernel via `brk(2)` or `mmap(2)` when its internal pool runs out.

## Stack

Stores local variables, function arguments, and return addresses.
Starts near the top of user space and grows downward toward lower
addresses. Each function call pushes a stack frame; returning pops
it (LIFO). The kernel enforces a maximum stack size
(`RLIMIT_STACK`, typically 8 MB).

## Threads and sharing

Threads within a process share the text, data, BSS, and heap
segments. Each thread gets its own private stack and register set,
so function call chains remain independent.

---

Return to [Linux](_index.md)

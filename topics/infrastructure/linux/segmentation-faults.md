# Segmentation faults

A segmentation fault (SIGSEGV) is the kernel's response when a
process attempts an illegal memory access. The MMU detects the
violation during address translation and traps into the kernel,
which delivers SIGSEGV to the offending process.

## Violation types

The kernel distinguishes two primary categories, reported via
`si_code` in the signal info:

| si_code     | Meaning                                          |
|-------------|--------------------------------------------------|
| SEGV_MAPERR | Address not mapped — no VMA covers it            |
| SEGV_ACCERR | Permission violation — VMA exists but forbids it |

SEGV_MAPERR covers dereferencing a NULL pointer, accessing
addresses beyond the stack or heap, and any access to an unmapped
region. SEGV_ACCERR covers attempts to write to read-only memory
(like the text segment) or execute a non-executable page.

## Core dumps

When the kernel kills a process with SIGSEGV, it can write a core
dump — an ELF file containing the process's memory segments and
register state at the moment of the crash. A debugger like `gdb`
can load this file to inspect exactly what went wrong:

```text
gdb ./program core
```

Core dump production requires `ulimit -c` to be non-zero.

---

Return to [Linux](_index.md)

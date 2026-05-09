# Kernel modules

Linux is a monolithic kernel — all core subsystems (scheduler,
filesystem, networking) share a single address space in Ring 0.
Loadable Kernel Modules (LKMs) extend this kernel at runtime
without recompiling or rebooting.

## How modules work

A module is compiled into a `.ko` (Kernel Object) file and loaded
into the kernel's address space with `insmod` or `modprobe`. Once
loaded, the module runs in Ring 0 with full hardware access — it
is not sandboxed. A buggy module can corrupt memory or cause a
kernel panic just like any other kernel code.

Removing a module with `rmmod` unlinks it from the running kernel,
freeing its resources.

## Why modules exist

Without modules, every driver for every device ever supported
would need to be compiled into the kernel binary. Instead, the
kernel ships lean and loads drivers on demand. When a device is
plugged in, `udev` detects the hardware and tells the kernel
which module to load.

Modules also serve as a prototyping tool — engineers can test new
filesystems or network protocols by loading and unloading modules
without rebooting.

## Module commands

| Command            | Purpose                                           |
|--------------------|---------------------------------------------------|
| `lsmod`            | List loaded modules                               |
| `modinfo <name>`   | Show module metadata (author, params, etc.)       |
| `modprobe <name>`  | Load a module and its dependencies                |
| `insmod <file.ko>` | Load a single `.ko` file (no dependency handling) |
| `rmmod <name>`     | Unload a module                                   |

---

Return to [Linux](_index.md)

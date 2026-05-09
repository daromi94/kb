# Kernel ring buffer

The kernel writes diagnostic messages to a fixed-size ring buffer
in memory. Early in the boot process, before filesystems are
mounted or logging daemons are running, this buffer is the only
place log output can go. Once full, new messages overwrite the
oldest entries.

`dmesg` reads this buffer directly from memory.

## What the kernel logs

- **Hardware detection** — device vendor/product IDs, assigned
  device names (`/dev/sdb`)
- **Module loading** — confirmation that drivers initialized
  successfully
- **System failures** — segfault details (with instruction
  pointer), kernel panics, OOM killer actions
- **Networking** — firewall logs (iptables/nftables), interface
  state changes

## Useful flags

| Flag                     | Purpose                                                 |
|--------------------------|---------------------------------------------------------|
| `dmesg -T`               | Human-readable timestamps instead of seconds since boot |
| `dmesg -w`               | Follow mode — stream new messages as they arrive        |
| `dmesg --level=err,warn` | Filter to errors and warnings only                      |
| `dmesg -n <level>`       | Set which severity levels print to the physical console |

---

Return to [Linux](_index.md)

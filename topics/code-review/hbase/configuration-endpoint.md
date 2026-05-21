# Configuration endpoint

A configuration endpoint is a read-only HTTP route that serves the
settings a process is running with. Those settings are assembled at
startup from several sources — defaults, config files, environment
variables, code overrides. Each source is just one input; the process
runs the merged result of all of them.

## Implementation

Every HBase daemon exposes this endpoint on its HTTP info server.

- **Served from memory.** It returns the configuration the daemon
  already holds, never re-reading files from disk.
- **Locked down.** Access is restricted and secret values are masked,
  so it is safe to leave enabled in production.

---

Return to [Apache HBase](_index.md)

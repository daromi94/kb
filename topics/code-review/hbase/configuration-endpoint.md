# Configuration endpoint

A configuration endpoint is a read-only HTTP route where a running
process reports the settings it is using. Those settings are assembled
at startup by layering several sources — built-in defaults, config
files, environment variables, and code overrides. Each source is just
one input; what the process runs is the merged result of all of them.

## Implementation

Each HBase daemon exposes this endpoint on its built-in HTTP info
server. It serves the configuration the daemon already holds in memory
instead of re-reading config files from disk. The endpoint restricts
access and masks secret values, so it is safe to leave enabled in
production.

---

Return to [Apache HBase](_index.md)

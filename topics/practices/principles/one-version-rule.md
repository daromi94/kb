# One Version Rule

For any dependency, exactly one version exists in the repository. No
multiple versions of a package, no forks under different names, no
versioned directories.

## Why one version

**Maintenance burden.** Multiple copies require duplicate update effort.
Forks demand continuous manual work to integrate upstream changes.

**Security.** Upstream maintainers focus security efforts on the latest
version. Older copies may harbor vulnerabilities that were discovered
and patched upstream but never backported to the stale copy sitting in
your tree.

**Diamond dependencies.** When A depends on B and C, and both B and C
depend on different versions of D, the build system resolves the
conflict — often silently picking a version the consumer didn't
intend. These conflicts produce unpredictable runtime failures
that can take days or weeks to diagnose because the symptoms appear far
from the root cause.

```text
     A
    / \
   B   C
    \ /
  D v1? v2? <- diamond: which version wins?
```

## Practical implications

**Upgrade atomically.** When you bump a dependency, every consumer in
the repository moves to the new version in the same commit. This is
expensive up front but eliminates version skew entirely.

**No vendoring forks.** If you need local patches, contribute them
upstream or maintain a single patched copy — never a parallel fork
under a different name.

**Monorepo enabler.** The rule works naturally in a monorepo where you
have visibility into all consumers. In a multi-repo world the same
principle applies but enforcement shifts to lockfiles, BOMs, or
platform dependency constraints.

---

Return to [Principles](_index.md)

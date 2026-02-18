# Tests as specifications

In a refactor, your test suite is your primary deployment gate. Tests are living
documentation of behavioral requirements.

## Preserve the specification

If a test fails after a structural change, it usually indicates you've violated
a business requirement—not that the test is wrong.

## Separate test changes from implementation changes

Avoid modifying tests and implementation simultaneously. If you must update a
test to match a new API, do it as a separate, isolated commit.

```
commit 1: Update test API expectations
commit 2: Refactor implementation to new API
```

This ensures you aren't accidentally "fixing" the test to pass against broken
logic.

## Warning signs

| Situation                      | Risk                             |
|--------------------------------|----------------------------------|
| Test fails after refactor      | Likely violated a requirement    |
| Changing test to make it pass  | May be hiding a regression       |
| Test and impl changed together | Can't tell which introduced bugs |

---

Return to [Refactoring](_index.md)

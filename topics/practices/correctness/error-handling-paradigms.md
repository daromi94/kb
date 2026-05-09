# Error handling paradigms

Five major approaches to communicating and managing failure in
software, each with a distinct philosophy and tradeoffs.

The choice of error handling strategy shapes the entire architecture:
how functions communicate failure, how callers respond, how errors
propagate, and what happens when nobody anticipated a failure mode.
The fundamental tension is between making errors visible so they get
handled and keeping normal-case code clean so logic stays readable.

## Return codes

A function returns a special value to indicate failure — a negative
number, zero, null, or a sentinel outside the valid range. Errors
are just data flowing through the same channel as normal return
values. No hidden control flow, no stack unwinding.

```text
result = openFile("/path/to/file")

if result == ERROR_NOT_FOUND
    // handle missing file
else if result == ERROR_PERMISSION_DENIED
    // handle permission problem
else
    // proceed with result
```

The C tradition. Dominant in systems programming, embedded
development, and Go. If the caller forgets to check the return
code, the error is silently ignored — the worst possible outcome.

## Exceptions

A function throws an object that automatically propagates up the
call stack until something catches it. The normal return path and
the error path are separate channels.

```text
try
    file = openFile("/path/to/file")
    data = file.read()
    result = parse(data)
catch FileNotFound
    // handle missing file
catch PermissionDenied
    // handle permission problem
```

The Java, C#, Python tradition. The normal path reads as a straight
sequence. Errors that nobody handles propagate automatically rather
than being silently ignored. The cost: hidden control flow jumps,
expensive stack unwinding, and resource cleanup complications.

**Checked vs unchecked.** Checked exceptions (Java) force callers
to handle or declare every exception at compile time. Widely
considered a failed experiment — the verbosity they impose leads
developers to swallow exceptions rather than handle them properly.
Unchecked exceptions provide no compile-time enforcement at all.

## Result types

A function returns a wrapper containing either a success value or
an error value, never both. The caller must unwrap the result
before using it, forcing acknowledgment of the error case at
compile time.

```text
result = openFile("/path/to/file")

match result with
    Success(file) ->
        // proceed with file
    Failure(FileNotFound) ->
        // handle missing file
    Failure(PermissionDenied) ->
        // handle permission problem
```

The Rust and Haskell tradition. The compiler refuses to let code
proceed without handling both cases. Nothing is invisible, nothing
is implicit, nothing can be accidentally ignored.

Monadic composition (Rust's `?` operator, `.then()` in promises)
extends this by automatically short-circuiting a chain of
operations at the first failure. Each step only runs if the
previous succeeded, giving the syntactic cleanliness of exceptions
with the explicitness of Result types.

## Callbacks

A function accepts a callback whose first argument is an error
value (null if no error occurred). Arose from event-driven systems
where exceptions cannot propagate across event loop boundaries.

```text
openFile("/path/to/file", function(error, file)
    if error is not null
        // handle error
    else
        // proceed with file
)
```

The early Node.js tradition. Largely superseded by promises and
async/await, which are Result types adapted for asynchronous
control flow.

## Let it crash

A process that encounters an error is allowed to die. A supervisor
detects the death and takes corrective action: restart, log,
escalate, or shut down a subsystem.

```text
// Worker — no error handling
function processMessage(message):
    data = decode(message)
    result = compute(data)
    store(result)

// Supervisor — watches workers
supervisor = Supervisor(
    strategy      = ONE_FOR_ONE,
    maxRestarts   = 5,
    withinSeconds = 60,
    children      = [Worker, Worker, Worker]
)
```

The Erlang/OTP tradition. The insight: error handling code is often
the buggiest part of the system because it is the least exercised.
Minimizing it and relying on structural recovery through redundancy
and supervision can produce more reliable systems overall.

## Comparison

| Axis             | Return codes | Exceptions     | Result types  | Crash      |
|------------------|--------------|----------------|---------------|------------|
| Error visibility | Every call   | Separate block | Every call    | Supervisor |
| Compile-time     | None         | Checked only   | Full          | N/A        |
| Composability    | Poor         | Poor           | Strong        | N/A        |
| Separation       | Interleaved  | Clean          | Interleaved   | By process |
| When ignored     | Silent       | Propagates     | Won't compile | Crashes    |

**When ignored** is the most important axis. Return codes let the
program continue with garbage. Exceptions propagate and crash
eventually, potentially far from the source. Result types refuse to
compile. The crash philosophy sidesteps the question entirely.

## Operational errors vs programming errors

Two fundamentally different kinds of failure that demand different
responses.

**Operational errors** are expected runtime conditions. A file does
not exist. A network request times out. A user submits invalid
input. The system is correct; the environment is messy. Response:
handle, retry, fall back, degrade gracefully.

**Programming errors** are bugs. A null dereference. An index out
of bounds. A violated invariant. The program is wrong. No recovery
logic fixes a bug. Response: fail immediately (assertion, panic,
crash) so the bug is found and fixed.

Mixing the two categories is where most strategies break down.
Catching NullPointerException and "recovering" masks a bug.
Returning -1 for "file not found" conflates absence with failure.
Wrapping invariant violations in Result types adds overhead to
conditions that should never occur.

The principled approach: one mechanism for operational errors
(exceptions, Result types, or return codes) and a separate
mechanism for programming errors (assertions or panics that
cannot be caught by normal error handling).

---

Return to [Correctness](_index.md)

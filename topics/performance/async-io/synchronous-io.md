# Synchronous I/O

Synchronous I/O is a programming model where tasks execute sequentially, one
after another.

## Characteristics

**Blocking behavior:** When a thread initiates a synchronous I/O operation
(such as reading from disk or making a network request), it becomes blocked.
The thread sits idle and does nothing while waiting for the operation to
complete.

**Linear execution:** Code following an I/O request cannot run until the
request finishes and returns a result.

**Ease of use:** The simplest model to write and understand because program
flow matches the order of code on the page.

## Related

- [Asynchronous I/O](asynchronous-io.md) - The non-blocking alternative

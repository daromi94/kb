# Navigational models

Early database systems from the 1960s–70s—**IMS** (Hierarchical) and **CODASYL**
(Network)—operated on a principle known as "programmer as navigator."

## How they worked

The database was a graph or hierarchy of records linked by physical pointers
(next, prior, parent).

- **Procedural querying** — Code explicitly described *how* to traverse pointers
  to find data, navigating the structure step-by-step
- **Manual traversal** — Finding an artist's albums meant nested loops: go to
  artist record, follow pointer to first album, follow "next" pointer to
  subsequent albums
- **Coupled to physical storage** — Code had to know the underlying data
  structure; hash map vs tree required completely different access commands

## Why they failed

These systems are obsolete for general-purpose use due to critical flaws:

| Problem               | Description                                               |
|-----------------------|-----------------------------------------------------------|
| No data independence  | Changing physical storage broke all application code      |
| Complexity            | Programmers needed to understand internal structure       |
| Fixed execution plans | Hard-coded traversal paths couldn't adapt to data changes |

If data volume changed significantly, the hard-coded execution strategy became
slow with no way to adapt without rewriting code.

## The relational solution

The relational model introduced **physical data independence**—allowing storage
to change without breaking application logic. Instead of navigating, you
declare *what* data you want and the DBMS determines *how* to retrieve it.

## Related

- [Data models](data-models.md) — Overview of all data models

---

Return to [Databases](_index.md)

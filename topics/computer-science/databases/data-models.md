# Data models

A **data model** is a collection of concepts used to describe the data stored
in a database. It functions as a high-level abstraction—a set of rules—defining
what types of data can exist and how they relate.

**Data model vs schema:** The data model is the abstract set of rules (e.g.,
"data is organized into tables with rows and columns"). The schema is a specific
blueprint using that model (e.g., "an Artist table with name and year columns").

## Relational model

The dominant model for general-purpose DBMS, proposed by Ted Codd around
1970 to solve the rigidity of earlier systems.

| Concept              | Description                                        |
|----------------------|----------------------------------------------------|
| Structure            | Relations (tables) containing tuples (rows)        |
| Integrity            | Primary keys, foreign keys, constraints            |
| Data independence    | Logical structure separated from physical storage  |
| Declarative querying | Specify *what* you want, not *how* to get it (SQL) |

**Data independence** allows the DBMS to optimize physical storage without
breaking application code. **Declarative querying** lets the DBMS determine
the most efficient retrieval strategy.

## Navigational models (legacy)

Before relational: **IMS** (Hierarchical) and **CODASYL** (Network). Now
obsolete for new applications.

- **Programmer as navigator** — Procedural code explicitly traversed database
  structures, tightly coupling query logic to physical storage layout
- **Brittleness** — Structure changes required rewriting all navigation code

## Alternative models

| Model        | Use case                                                 |
|--------------|----------------------------------------------------------|
| Document     | Hierarchical JSON/XML; avoids object-relational mismatch |
| Vector       | ML/AI nearest-neighbor searches on embeddings            |
| Key/Value    | Simple lookups by key                                    |
| Graph        | Relationship-heavy data with complex traversals          |
| Wide-Column  | Sparse data with many columns                            |
| Array/Matrix | Scientific and analytical workloads                      |

---

Return to [Databases](_index.md)

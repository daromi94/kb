# Overview

A database is an organized collection of inter-related data that models some
aspect of the real world. It serves as a digital representation of real-world
entities—such as students in a class or artists and albums in a music store—
capturing their attributes and the relationships between them.

## Database vs DBMS

A **database** is the data itself. A **Database Management System (DBMS)** is
the software (PostgreSQL, MySQL, SQLite) used to store, manage, and query that
data. The terms are often used interchangeably but are technically distinct.

## Data models

Databases are structured according to a **data model**—a collection of concepts
describing what types of data can exist and how they relate. Common models
include:

| Model      | Description                                 |
|------------|---------------------------------------------|
| Relational | Tables with rows and columns (dominant)     |
| Key/Value  | Simple key-to-value mappings                |
| Document   | Semi-structured JSON/BSON documents         |
| Graph      | Nodes and edges for relationship-heavy data |

The relational model remains the dominant standard for general-purpose systems.

## Why not flat files

Storing data in text files (CSVs) lacks essential guarantees:

- **Data integrity** — Ensuring correctness
- **Durability** — Protecting against crashes
- **Concurrency control** — Allowing simultaneous access by multiple users

A DBMS provides these guarantees; flat files do not.

---

Return to [Databases](_index.md)

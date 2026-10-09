# Vector embeddings

An embedding represents an item as a list of numbers called a **vector**. A model learns these numbers so they help with tasks such as predicting text or finding related content.

The item can be a token, sentence, document, or image. Different embedding models represent different kinds of items.

## Why token IDs are not enough

A tokenizer might assign these IDs:

```text
apple  --> 40
banana --> 41
car    --> 8000
```

The numbers identify vocabulary entries. Their numerical distance says nothing about meaning.

A language model uses each ID to look up a learned vector:

```text
token ID
    |
    v
embedding table
    |
    v
[0.12, -0.37, 0.08, ...]
    |
    v
model calculations
```

This **embedding table** has one vector per vocabulary entry. Training adjusts the values so they become useful to the model.

A vector may contain hundreds or thousands of values. These values are dimensions of the representation, not a list of named properties such as "animal" or "vehicle."

## What similarity can reveal

In a representation trained to capture semantic relationships, related items can have similar vectors.

A two-dimensional sketch can show the idea:

```text
dimension 2
    ^
    |
    |     dog  puppy
    |       *  *
    |
    |                         car *
    +--------------------------------> dimension 1
```

Real embeddings have many more dimensions. The sketch illustrates proximity.

A similarity measure compares vectors. **Cosine similarity**, for example, compares their directions.

The useful measure depends on how the embeddings were trained. Numerical proximity is evidence of a learned relationship, not a guarantee that two items mean the same thing.

## Input embeddings and contextual representations

A token's input embedding comes from a lookup table. The same token ID selects the same input vector.

Inside a Transformer, attention combines information from allowed context positions. The resulting representation can differ across sentences.

For example:

```text
"the river bank"        "deposit at the bank"
        |                         |
        v                         v
representation using     representation using
river context            financial context
```

These are **contextual representations**. The surrounding tokens help distinguish the use of `bank`.

The input embedding starts the calculation. The contextual representation reflects processing inside the model.

## Embeddings for search

A text-embedding model can produce one vector for a passage. It can also produce a vector for a search query.

A search system then compares the query vector with stored passage vectors:

```text
documents --> embedding model --> stored vectors
                                      ^
                                      | compare similarity
                                      |
query ----> embedding model --> query vector
```

This supports **semantic search**: finding related content even when the query and passage use different words.

The query and documents need compatible embeddings from the same representation space. Vectors from unrelated models are not directly comparable.

## Vector arithmetic

Some word embeddings capture relationships as directions. A familiar example is:

```text
king - man + woman ~= queen
```

The arithmetic operates on vectors, not on the words themselves.

Such relationships can appear in a learned space, but they are approximate and depend on the model. Embeddings provide useful numerical structure; they do not encode every relationship as a reliable equation.

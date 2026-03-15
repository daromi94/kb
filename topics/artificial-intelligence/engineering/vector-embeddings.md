# Vector embeddings

An embedding converts a discrete token ID into a dense vector — a list
of hundreds to thousands of floating-point numbers. This replaces an
arbitrary integer with a coordinate in a high-dimensional space where
geometric proximity encodes semantic similarity.

## Why not raw integers

Token IDs are arbitrary integers — "apple" might be 40, "banana" 41,
"car" 8000. Proximity between IDs says nothing about meaning, and
arithmetic on them is nonsensical. Embeddings replace each ID with a
learned position in a space where distance reflects semantic
relatedness.

## Properties

**Dimensionality.** Embedding vectors typically range from 768 to over
4,000 dimensions, depending on model size.

**Semantic proximity.** During pre-training, tokens that appear in
similar contexts are pulled closer together. "Dog" and "puppy" end up
near each other; "carburetor" ends up far away.

**Contextual embeddings.** Transformer-based models produce different
vectors for the same token depending on context. "Bank" gets one
embedding in "river bank" and a different one in "deposit at the bank."

## Vector arithmetic

Because relationships are encoded as directions in the space, semantic
analogies reduce to vector algebra:

$\text{King} - \text{Man} + \text{Woman} \approx \text{Queen}$

The direction from Man to Woman captures a relationship that, when
applied to King, lands near Queen. The same principle holds for verb
tense, geography, and other systematic relationships.

## Related

- [Tokenization](tokenization.md) - The pipeline that produces the
  integer IDs embeddings replace

---

Return to [AI engineering](_index.md)

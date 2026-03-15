# Tokenization

A token is the atomic unit of input for a language model. It is not
necessarily a word — depending on the algorithm, a token may represent a
whole word ("apple"), a subword fragment ("un-", "-break-", "-able"), or
a single character. In English, one token is roughly four characters or
three-quarters of a word.

## Why subword tokenization

Word-level tokenization creates three problems that subword algorithms
solve:

**Vocabulary size.** A unique entry for every inflected form ("run",
"runs", "running", "ran") produces an unmanageably large vocabulary.
Subword tokenizers keep the vocabulary between 30,000 and 100,000 units
while still being able to construct any word.

**Out-of-vocabulary words.** A word-level tokenizer fails on unseen
strings — novel slang, technical jargon, chemical names. A subword
tokenizer decomposes unknown strings into recognized fragments or
individual characters.

**Morphologically rich languages.** Languages with compound words
(German) or complex morphology (Turkish) are handled far more
efficiently as subword fragments than as whole-word units.

## Processing pipeline

```
"unbreakable"
   |
   | segmentation
   v
["un", "break", "able"]
   |
   | vocabulary lookup
   v
[441, 8704, 481]
   |
   | embedding
   v
[vec_441, vec_8704, vec_481]
```

1. **Segmentation.** Raw text is split into tokens according to the
   algorithm's learned rules
2. **Vocabulary lookup.** Each token maps to an integer ID in the
   model's fixed vocabulary
3. **Embedding.** Integer IDs are converted to dense, high-dimensional
   vectors that encode semantic relationships between tokens

## Related

- [Vector embeddings](vector-embeddings.md) - The next step: converting
  token IDs into semantic vectors
- [Language models](language-models.md) - The models that operate on
  tokenized input

---

Return to [AI engineering](_index.md)

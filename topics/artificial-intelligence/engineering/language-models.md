# Language models

A language model computes probability distributions over sequences of
tokens. Given a context, it assigns a probability to every token in its
vocabulary and predicts the most likely next one.

## Autoregressive generation

Text generation is an iterative loop:

1. The model receives an input sequence
2. It produces a probability distribution over its full vocabulary for
   the next position
3. A token is selected and appended to the sequence
4. The extended sequence feeds back into the model

This repeats until a stop token is produced or a length limit is hit.

## Architectural evolution

**N-gram models.** Early approaches used frequency counts over fixed
windows of preceding words (bigrams, trigrams). Cheap to compute but
blind to long-range dependencies.

**Transformer-based models.** Tokens are mapped to dense vectors in a
high-dimensional embedding space. Self-attention lets the model weigh
every token against every other token in the sequence, capturing
grammar, semantics, and long-range context in a single pass.

## Related

- [Foundation models](foundation-models.md) - Pretrained base models
  built on language model architectures

---

Return to [AI engineering](_index.md)

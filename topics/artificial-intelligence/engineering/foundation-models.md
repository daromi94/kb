# Foundation models

A foundation model is a general-purpose model trained on vast quantities
of unlabeled data via self-supervised learning. Researchers at Stanford's
Center for Research on Foundation Models (CRFM) coined the term in 2021
to describe a single pretrained base that can be adapted to many
downstream tasks — rather than building a separate model for each one.

## Characteristics

**Self-supervised learning.** The model learns by finding patterns in
raw data — predicting the next token in a sequence, reconstructing
masked portions of an image, or similar pretext tasks — rather than
relying on human-annotated labels.

**Scale.** Billions to trillions of parameters trained on terabytes of
data. Pre-training is computationally immense, but the resulting base
can be cheaply adapted to many tasks.

**Adaptability.** A single pretrained base supports diverse use cases
through full fine-tuning, parameter-efficient fine-tuning (LoRA,
adapters), prompt engineering, or Retrieval-Augmented Generation (RAG).

**Multimodality.** Models increasingly handle multiple data types —
text, code, images, audio, video — within the same architecture,
enabling cross-modal reasoning.

**Emergent abilities.** Some capabilities only appear after a model
reaches a certain scale. Performance on a task stays near-random
across smaller sizes, then jumps to competent at a threshold — a
discontinuity not driven by any task-specific training signal.

## Comparison with traditional ML

| Feature       | Traditional ML                      | Foundation Models                    |
|---------------|-------------------------------------|--------------------------------------|
| Task scope    | Single-purpose                      | General-purpose, multi-task          |
| Training data | Curated, human-labeled (supervised) | Massive, unlabeled (self-supervised) |
| Adaptability  | New task requires a new model       | Fine-tune or prompt the same base    |
| Cost profile  | Low train cost, high per-task cost  | High pre-train cost, low adapt cost  |

Traditional ML is purpose-built: a spam classifier, a fraud detector,
and a sentiment analyzer are each trained from scratch on labeled data
specific to that task. Foundation models invert this by front-loading
compute into one pre-training run, then amortizing that cost across
many lightweight adaptations.

## Related

- [Self-supervised learning](self-supervised-learning.md) - The training
  paradigm that makes foundation models possible
- [Language models](language-models.md) - The dominant architecture for
  text-based foundation models

---

Return to [AI engineering](_index.md)

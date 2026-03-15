# Self-supervised learning

Self-supervised learning extracts training signals directly from raw
data, eliminating the need for human-annotated labels. The data itself
provides both the input and the target.

## The supervision bottleneck

Supervised learning requires labeled datasets — every image tagged,
every sentence annotated. This scales poorly:

- **Cost.** Human annotation for millions of examples is expensive and
  slow. Expert domains (medical imaging, legal analysis) are worse.
- **Volume.** Labeled data is a tiny fraction of all available data.
  Raw, unstructured text and images are orders of magnitude larger.

Self-supervision sidesteps this by deriving labels from the structure
of the data itself, unlocking training at internet scale.

## Next-token prediction as self-supervision

In language modeling, every sentence is its own labeled dataset. The
model sees a prefix and predicts the next token — the true next token
already exists in the text.

For the sentence "I love street food":

| Context               | Target |
|-----------------------|--------|
| `<BOS>`               | I      |
| `<BOS>` I             | love   |
| `<BOS>` I love        | street |
| `<BOS>` I love street | food   |

If the model predicts "car" instead of "food", the loss function
computes the error against the known correct token and adjusts
parameters via backpropagation. Billions of these self-correcting
iterations run without any human in the loop.

## Special tokens

**`<BOS>` (beginning of sequence).** Marks the start of a new
document. Resets the context window so the model does not carry over
meaning from an unrelated preceding text.

**`<EOS>` (end of sequence).** Marks the end of a document or
response. During generation, predicting `<EOS>` is the signal that
tells the model to stop producing output.

## Related

- [Foundation models](foundation-models.md) - Self-supervised learning
  as a defining characteristic
- [Language models](language-models.md) - The autoregressive prediction
  loop this training produces

---

Return to [AI engineering](_index.md)

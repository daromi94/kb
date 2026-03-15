# Completion paradigm

Every language model behavior — translation, classification,
summarization, code generation — is next-token prediction. The model
does not retrieve stored answers or run task-specific modules. It
continues the input pattern by sampling from a probability distribution
over its vocabulary.

## Stochastic output

Traditional software is deterministic: the same input always produces
the same output. Language models are stochastic — they sample from a
probability distribution, so outputs vary across runs. The result is a
statistically weighted prediction, not a guaranteed correct answer.

**Hallucinations** are a direct consequence. The model optimizes for
statistical coherence (sounding correct), not factual accuracy (being
correct). It will confidently complete a pattern with fabricated content
if that completion is the most probable continuation.

## Tasks as completion

Any task can be framed as pattern completion by structuring the prompt
so the desired output is the natural continuation:

**Translation.** A prompt like `"English: Hello. French: "` activates
cross-lingual weights — the model completes the pattern with the
target language.

**Classification.** A prompt like `"Text: [email body]. Spam status: "`
narrows the next-token distribution to a label, turning the generator
into a classifier.

No separate translation or classification algorithm runs. The prompt
structure steers the same completion mechanism toward different tasks.

## Related

- [Language models](language-models.md) - The underlying prediction
  mechanics

---

Return to [AI engineering](_index.md)

# Completion paradigm

A generative language model can perform different tasks by continuing different input patterns. The prompt supplies the task, and the model generates the continuation.

For an autoregressive model, the output is built one token at a time. A token is a piece of text, such as a word fragment or punctuation.

## A task can be expressed as a pattern

Consider a translation prompt:

```text
English: Hello
French:
```

A suitable continuation is:

```text
Bonjour
```

The prompt provides both the source text and the expected output form. The model's learned capabilities determine whether it can produce a good translation.

A classification task can use a different pattern:

```text
Text: "Win a prize by sending your bank details."
Choose one label: spam, not spam
Label:
```

The desired continuation is a label.

```text
translation prompt ------+
                         |
classification prompt ---+--> same generative model
                         |             |
summary prompt ----------+             v
                              task-shaped continuation
```

A model can use the same generation mechanism for many tasks. Changing the prompt changes the context used to predict the output.

## The prompt guides a learned capability

Instructions and examples make the intended task clearer.

For classification, examples can establish the label meanings:

```text
Text: "Your package arrives tomorrow."
Label: not spam

Text: "Send money to claim your prize."
Label: spam

Text: "Lunch has moved to 12:30."
Label:
```

The earlier examples become part of the context for the final prediction.

This is **in-context learning**: examples guide behavior within the input. It normally does not update the model's parameters.

Prompt structure helps the model use capabilities it has learned. A clear format alone does not guarantee that the model can solve the task.

## Prediction and selection are separate

At each step, the model produces probabilities over possible next tokens. A decoding method selects a token.

- **Greedy decoding** selects the most likely token at that step.
- **Sampling** makes a random selection based on the probabilities.

Sampling can produce different outputs from the same prompt. A fixed selection rule can make outputs more repeatable, although execution details can still affect repeatability.

Either method can produce an incorrect answer. Repeatability and correctness are separate properties.

## A plausible continuation can be false

A **hallucination** is generated content that is unsupported or false while appearing credible.

Suppose a prompt asks for a paper supporting a claim. The model may produce a title, author list, and publication name that match the style of a citation.

Those details can form fluent text even when the paper does not exist.

The next-token calculation does not independently verify every generated claim. Training and additional checks can improve factual reliability, but fluency alone is not evidence.

## External information can become part of the context

A surrounding application can retrieve documents or run tools before asking the model to generate an answer.

```text
question
   |
   v
retrieve relevant passages
   |
   v
question + passages
   |
   v
language model
   |
   v
generated answer
```

The model still generates a continuation, but the context now contains information from another system.

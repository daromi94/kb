# Language models

A language model learns patterns in text and uses them to estimate which tokens fit a context. A **token** is a piece of text, such as a word, part of a word, or punctuation.

A model that generates text can use these estimates to build a response one token at a time.

## From context to probabilities

Consider this unfinished sentence:

```text
The cat sat on the
```

The words already available form the **context**. The model uses that context to assign probabilities to possible next tokens.

An illustrative result might look like this:

| Next token | Probability |
| ---------- | ----------- |
| mat        | 40%         |
| floor      | 30%         |
| chair      | 20%         |
| Other      | 10%         |

The actual distribution covers the model's vocabulary, not just these examples.

A separate selection step chooses a token:

- **Greedy selection** chooses the token with the highest probability.
- **Sampling** chooses randomly according to the probabilities, possibly after adjusting or filtering them.

The model therefore does not always select its most likely token.

## Building a sequence

After selecting `mat`, the generation process adds it to the context and asks for another prediction.

```text
"The cat sat on the"
          |
          v
 predict next-token probabilities
          |
          v
      select "mat"
          |
          v
"The cat sat on the mat"
          |
          v
 predict again, now using the longer context
```

This is **autoregressive generation**: each new token depends on the tokens that come before it.

Generation continues until a stopping condition is reached, such as an end-of-sequence token or an output-length limit.

The model's learned parameters normally stay fixed during generation. Producing a response uses the model; training changes it.

## How the model uses context

A simple **n-gram model** estimates probabilities by counting short sequences in a dataset. A model using only the previous two words has little information about the rest of a paragraph.

A **Transformer** builds numerical representations of tokens and updates them through **attention**. Attention combines information from allowed context positions, with different weights for their relevance to the calculation.

For a model trained to predict the next token, those positions include the current token and earlier tokens. Future tokens are hidden during training so they cannot reveal the answer.

```text
["The", "cat", "sat", "on", "the"]
                 |
                 | attention over available positions
                 v
      contextual representation
                 |
                 v
      next-token probabilities
```

Longer context can help the model connect a pronoun to a name, continue a topic, or follow a code structure. The amount of context available still has a limit.

## Language modeling includes other objectives

Next-token prediction is one language-modeling objective.

A **masked language model** learns to predict missing tokens inside text:

```text
The [MASK] sat on the mat.
       |
       v
      cat
```

Such a model can use text on both sides of the missing position. It does not use the same left-to-right generation loop by default.

# Self-supervised learning

Self-supervised learning creates training targets from the data itself. The model learns by predicting information that is already present, so each example does not need a person to supply a separate label.

For text, a sentence can provide both the input and the expected answer.

## Where the targets come from

Suppose a training dataset contains:

```text
I love street food
```

For a simplified example, treat each word as one token. Several prediction tasks can come from the same sentence:

| Input context | Expected next token |
| ------------- | ------------------- |
| I             | love                |
| I love        | street              |
| I love street | food                |

The training system already has the complete sentence. It hides the next token from the model, then uses that token as the target.

```text
"I love street" --> model --> predicted probabilities
                                      |
                                      v
"food" ------------------------> loss function
                                      |
                                      v
                               parameter updates
```

One document can therefore produce many training examples.

## How an error changes the model

The model predicts a probability distribution over possible next tokens.

Suppose it assigns:

```text
food: 10%
car:  60%
other tokens: 30%
```

The observed next token is `food`. A **loss function** measures the prediction error. For the usual next-token objective, assigning a low probability to the observed token produces a larger loss.

**Backpropagation** computes how the model's parameters contributed to that loss. An optimizer then adjusts the parameters to reduce the error across training examples.

```text
predict --> measure loss --> compute gradients --> update parameters
   ^                                                     |
   +------------------ next training batch --------------+
```

These updates gradually teach patterns in grammar, meaning, and document structure.

The example shows the prediction positions separately. A **causal Transformer** lets each position use only its current and earlier tokens. During training, it can process many positions in parallel while hiding future tokens at each position.

## Self-supervision can hide other information

Next-token prediction is one way to create targets.

Other examples include:

- Hide a word and predict it from the surrounding sentence.
- Hide part of an image and reconstruct the missing region.
- Train representations from different views of the same input.

The common idea is to derive a learning task from the available data.

Human work still matters for collecting, filtering, and evaluating that data. Self-supervision removes the need to manually label every prediction target.

## Sequence markers

Training data may include special tokens:

- **Beginning of sequence**, often written `<BOS>`, marks a starting position.
- **End of sequence**, often written `<EOS>`, marks an ending position.

During generation, the decoding system can stop when it encounters an end token.

A beginning marker does not reset context by itself. The input sequence, attention rules, and handling of stored context determine which earlier tokens remain available.

## Training and generation are different

During training, the observed data supplies the expected answer, and the model's parameters change.

During generation, the next answer is unknown. The system selects a token from the model's predictions and uses it to continue the sequence.

Self-supervision makes large training datasets practical because the targets come from the data's own structure.

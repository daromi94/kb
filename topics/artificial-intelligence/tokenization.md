# Tokenization

Tokenization converts text into units a language model can process. Each unit is a **token**, and each token has an integer identifier in the tokenizer's vocabulary.

A token can be a whole word, part of a word, punctuation, whitespace, or a representation of bytes. The exact split depends on the tokenizer.

## Why a word is not always one token

A vocabulary containing every possible word has several problems:

- A word can have many forms, such as `run`, `runs`, and `running`.
- New names, technical terms, and spelling variations keep appearing.
- Some languages build long words from many smaller parts.

A **subword tokenizer** uses reusable pieces. Common text can stay together, while less common text is split into smaller units.

An illustrative split is:

```text
unbreakable
     |
     v
["un", "break", "able"]
```

These pieces do not have to match grammatical roots. Tokenization follows the tokenizer's learned vocabulary and rules.

## From text to model input

Each token maps to an integer ID. That ID selects a numerical vector called an **embedding**, which the model uses in its calculations.

```text
"unbreakable"
      |
      | split text
      v
["un", "break", "able"]
      |
      | look up token IDs
      v
[441, 8704, 481]
      |
      | look up embedding vectors
      v
[vector_441, vector_8704, vector_481]
      |
      v
   language model
```

The tokenizer defines the pieces and IDs. The model learns how to use their vectors.

A model therefore needs the tokenizer associated with its vocabulary. An ID from another tokenizer can refer to a different piece of text.

## How subword vocabularies are built

**Byte pair encoding**, or **BPE**, starts with small units and repeatedly merges frequent adjacent pairs. Common sequences become larger vocabulary entries.

**WordPiece** and **Unigram** use different rules to build or select subword pieces.

The shared tradeoff is:

- Larger pieces produce shorter token sequences but need more vocabulary entries.
- Smaller pieces can represent more combinations but produce longer sequences.

A tokenizer based on all possible byte values can encode unfamiliar text without requiring a vocabulary entry for every word. Other tokenizers may use an unknown-token marker when they cannot represent an input.

## Token counts change the available context

A model's context limit is measured in tokens. The prompt, supporting text, and generated output may all need to fit within that limit.

Two passages with the same character count can produce different token counts.

The count depends on:

- The tokenizer's vocabulary.
- The language and writing system.
- Names, numbers, punctuation, and code.
- Repeated or uncommon character sequences.

An estimate such as four English characters per token is only a rough shortcut. Exact counts come from the model's tokenizer.

## Turning output back into text

The model produces token IDs. **Decoding** converts those IDs back into text.

```text
input text --> token IDs --> model --> output token IDs --> output text
```

Visible text and model input are different representations. Tokenization is the step that connects them.

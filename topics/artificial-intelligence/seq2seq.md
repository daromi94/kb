# Seq2Seq

Sequence-to-sequence (Seq2Seq) is a neural network architecture for transforming an input sequence into an output sequence, where the two sequences can have different lengths.

The fundamental idea is to separate the model into two components:

- Encoder: Processes the input sequence and produces a representation of it.
- Decoder: Uses that representation to generate an output sequence.

Seq2Seq models became particularly important in machine translation, text summarization, speech recognition, and other problems involving sequences.

## 1. The problem Seq2Seq solves

Consider translating an English sentence into Spanish.

```text
Input: "I am tired"

Output: "Estoy cansado"
```

The input contains three words, while the output contains two.

A model cannot simply translate each word independently because languages differ in grammatical structure, word order, and how meaning is expressed.

Furthermore, the model does not necessarily know the output length in advance.

Seq2Seq addresses this by learning a transformation from an entire input sequence to an output sequence.

```text
INPUT SEQUENCE
"I am tired"
    |
    v
+---------------+
|    Encoder    |
+---------------+
    |
    v
Encoded Information
    |
    v
+---------------+
|    Decoder    |
+---------------+
    |
    v
OUTPUT SEQUENCE
"Estoy cansado"
```

The encoder learns how to represent the input, while the decoder learns how to generate the desired output.

The key innovation is that input and output lengths do not need to match.

## 2. The original Seq2Seq architecture

Early neural Seq2Seq models used two recurrent neural networks, commonly LSTMs.

The architecture contained an encoder RNN and a decoder RNN.

### Step 1: Encoding the input

Suppose the input sequence is:

```text
["I", "am", "tired"]
```

The encoder processes the tokens sequentially, updating its hidden state at every time step.

```text
ENCODER

        "I"    "am"   "tired"
        |      |      |
        v      v      v
        +----+ +----+ +----+
h0 ---->| E1 |>| E2 |>| E3 |
        +----+ +----+ +----+
        |      |       |
        v      v       v
        h1     h2      h3
                       |
                       v
                       Final state
                       h3
```

Mathematically:

```text
h_t = f_enc(x_t, h_(t-1))
```

Where `x_t` is the embedding of the current input token and `h_t` is the resulting hidden state.

In the simplest architecture, the final encoder state becomes a context vector:

```text
c = h_T
```

The context vector is intended to summarize the relevant information in the input sequence.

For an LSTM, the final hidden state and cell state can both be passed to the decoder.

### Step 2: Decoding the output

Once the encoder finishes, the decoder begins producing output tokens.

The decoder is initialized using information from the encoder.

```text
                 ENCODER
            +---------------+
            | I  am  tired  |
            +-------+-------+
                    |
                    v
              Context Vector
                    |
                    v
                 DECODER

               +--------+
     <SOS> --->|   D1   |----> "Estoy"
               +--------+
                    |
                    v
               +--------+
    "Estoy" -->|   D2   |----> "cansado"
               +--------+
                    |
                    v
               +--------+
   "cansado" ->|   D3   |----> <EOS>
               +--------+
```

Two special tokens appear in the diagram:

`<SOS>` means start of sequence. It signals that generation should begin.

`<EOS>` means end of sequence. It signals that generation is complete.

The decoder generates one token at a time, conditioned on its preceding tokens and the information supplied by the encoder.

This design was demonstrated successfully using deep LSTMs for machine translation in 2014.

## 3. How the decoder actually predicts tokens

A decoder does not directly produce words. It computes numerical scores for possible tokens, which are transformed into probabilities.

For example, the first decoder step might produce:

| Token | Probability |
| ----- | ----------- |
| Estoy | 0.82        |
| Soy   | 0.10        |
| Tengo | 0.05        |
| Other | 0.03        |

A greedy decoding strategy selects the most probable token: `Estoy`.

That token becomes an input to the next decoder step, which predicts the next token.

The process continues until the model generates `<EOS>` or reaches another stopping condition, such as a maximum output length.

Mathematically, the decoder models:

```text
P(y_t | y_1, ..., y_(t-1), x)
```

Where `x` represents the input sequence and `y_t` represents the next output token.

For the complete output sequence:

```text
P(y | x) = product(t = 1..M, P(y_t | y_<t, x))
```

This factorization is one of the most important ideas in conditional text generation.

The model learns the probability of an output sequence, conditioned on an input sequence.

## 4. The fundamental problem: the context vector bottleneck

The original architecture had a serious limitation.

The entire input sequence had to be represented through a fixed-size context vector.

Consider two inputs:

```text
Input A:
    "Hello"

Input B:
    "The distributed database experienced a network
     partition while several replicas were performing
     concurrent writes and recovering from a previous
     leader failure."
```

Both inputs might be compressed into a context vector of the same dimensionality.

```text
Short Sequence            Long Sequence
    |                         |
    v                         v
+---------+               +---------+
| Encoder |               | Encoder |
+---------+               +---------+
    |                         |
    v                         v
+----------+              +----------+
| Context  |              | Context  |
| Vector   |              | Vector   |
| 512 dims |              | 512 dims |
+----------+              +----------+
```

The dimensionality remains fixed, but the amount of information that must be captured grows with the sequence length.

This creates an information bottleneck.

The decoder may struggle to recover details from early parts of longer sequences, especially when they contain complex dependencies.

It is not mathematically impossible for a fixed-size vector to encode information about a long sequence. The practical problem is learning a representation that preserves everything necessary for accurate decoding.

This limitation motivated one of the most influential developments in neural networks: attention.

## 5. How Seq2Seq models are trained

Seq2Seq models are typically trained using paired examples.

For a translation application, each training example contains a source sequence and its target translation.

```text
TRAINING DATA

+----------------+----------------+
| Source         | Target         |
+----------------+----------------+
| I am tired     | Estoy cansado  |
| Good morning   | Buenos dias    |
| Thank you      | Gracias        |
+----------------+----------------+
```

During training, the objective is to maximize the probability of the correct target tokens.

Equivalently, the model commonly minimizes negative log-likelihood:

```text
L = -sum(t = 1..M, log(P_theta(y_t^* | y_<t^*, x)))
```

The asterisk indicates the ground-truth target sequence.

### Teacher forcing

A common training technique is called teacher forcing.

During training, the decoder receives the correct previous token rather than its own previous prediction.

```text
TRAINING

Decoder input     Expected output
-------------     ---------------
<SOS>        ---> Estoy
Estoy        ---> cansado
cansado      ---> <EOS>
```

This enables efficient supervised training because incorrect early predictions do not automatically corrupt the inputs used for subsequent training steps.

However, a discrepancy emerges between training and inference.

During inference, the true target sequence is unavailable. The decoder must use its own generated tokens.

```text
INFERENCE

<SOS>      ---> "Estoy"
"Estoy"    ---> "cansado"
"cansado"  ---> <EOS>
```

If the model generates an incorrect token, future predictions are conditioned on that error.

This training-inference mismatch is related to exposure bias, a well-known issue in autoregressive sequence generation.

## 6. Seq2Seq is not necessarily an RNN

An important distinction:

Seq2Seq describes a sequence-transformation architecture or modeling approach, not a particular neural-network layer.

Historically, many Seq2Seq models used RNNs and LSTMs. However, encoder-decoder architectures can also use Transformers.

The Transformer architecture replaced recurrent operations with attention-based computations, improving parallelism during training.

```text
CLASSIC SEQ2SEQ

Input Sequence
    |
    v
RNN Encoder
    |
    v
Encoded Information
    |
    v
RNN Decoder
    |
    v
Output Sequence


TRANSFORMER SEQ2SEQ

Input Sequence
    |
    v
Transformer Encoder
    |
    v
Encoder Representations
    |
    v
Transformer Decoder
    |
    v
Output Sequence
```

The roles remain similar, but the internal computations differ.

In a Transformer encoder-decoder architecture, the decoder typically combines masked self-attention over previously generated tokens with cross-attention over encoder representations.

The architecture can therefore model complex relationships without relying on recurrent hidden-state transitions.

## 7. Seq2Seq versus modern decoder-only LLMs

Many modern generative language models use decoder-only Transformer architectures.

This introduces an important distinction between generating an output sequence conditioned on an input and using a separate encoder-decoder architecture.

| Property         | Encoder-decoder Seq2Seq               | Decoder-only LLM                         |
| ---------------- | ------------------------------------- | ---------------------------------------- |
| Architecture     | Separate encoder and decoder          | Decoder-only Transformer                 |
| Input processing | Encoder builds source representations | Prompt becomes part of the token context |
| Conditioning     | Often via decoder cross-attention     | Via causal self-attention                |
| Generation       | Autoregressive                        | Autoregressive                           |
| Example          | T5, BART                              | GPT-style models                         |

Both approaches can perform translation, summarization, and many other sequence-transformation tasks.

For example, a decoder-only model might receive:

```text
Translate to Spanish: I am tired

Answer:
```

It then generates the answer as a continuation of the prompt.

In contrast, an encoder-decoder model processes the source through its encoder, and the decoder generates the target while conditioned on the encoded representations.

Thus, Seq2Seq can describe the task, while encoder-decoder describes a particular architectural solution to that task.

## 8. Where Seq2Seq is useful

Seq2Seq modeling applies whenever an input sequence needs to be transformed into another sequence.

| Application            | Input                | Output               |
| ---------------------- | -------------------- | -------------------- |
| Machine translation    | English sentence     | Spanish sentence     |
| Summarization          | Long document        | Short summary        |
| Speech recognition     | Audio sequence       | Transcription        |
| Grammatical correction | Incorrect sentence   | Corrected sentence   |
| Question answering     | Question and context | Answer               |
| Code translation       | Source-language code | Target-language code |

Not every implementation uses the same neural architecture. For example, modern speech systems may combine specialized audio encoders with other decoding strategies.

The common property is learning a conditional relationship between sequences.

## 9. Key engineering takeaways

1. Seq2Seq separates input understanding from output generation through the encoder-decoder architecture.
2. Input and output lengths can differ, making it suitable for translation and other sequence transformations.
3. Early RNN-based models used a fixed-size context vector, which created challenges for longer sequences.
4. Teacher forcing simplifies supervised training, but creates a mismatch between training and autoregressive inference.
5. Seq2Seq is not synonymous with RNNs. Transformer encoder-decoder models implement the same broad architectural idea without recurrence.

The central idea can be summarized as:

```text
Input Sequence --Encoder--> Representation --Decoder--> Output Sequence
```

Seq2Seq was a major step toward modern generative AI because it established a powerful general pattern: learn a representation of an input, then generate an output conditioned on that representation.

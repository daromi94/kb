# Attention

Attention is a neural network mechanism that allows a model to dynamically determine which pieces of information are most relevant when computing a representation or generating an output.

Instead of treating all available information equally, attention computes relevance scores, converts those scores into weights, and combines information according to those weights.

Attention is one of the fundamental mechanisms behind modern large language models (LLMs) and Transformer architectures.

## 1. The problem attention solves

Consider the following sentence:

> The animal didn't cross the street because it was tired.

What does "it" refer to?

To interpret "it", the model needs to establish a relationship with the earlier word "animal".

Not every word contributes equally to this interpretation.

Conceptually, a model might assign the following weights:

```text
Interpreting the word "it"

Previous word    Relevance
-------------    ---------
The                   0.02
animal                0.75
didn't                0.03
cross                 0.02
the                   0.01
street                0.12
because               0.05
                      ----
Total                 1.00
```

These numbers are illustrative, not actual model outputs.

The key idea is that information associated with "animal" could contribute more strongly to the representation of "it" than information associated with less relevant words.

This is fundamentally different from requiring every preceding word to contribute equally.

Attention is a mechanism for selecting and combining information based on learned relevance.

## 2. Why attention was introduced

Early Seq2Seq architectures commonly relied on recurrent neural networks.

An encoder processed the input sequence and compressed information into a fixed-size representation, which the decoder used to generate an output.

```text
ORIGINAL SEQ2SEQ

Input: "I am very tired"
    |
    v
+---------+
| Encoder |
+---------+
    |
    v
Context Vector
    |
    v
+---------+
| Decoder |
+---------+
    |
    v
Output: "Estoy muy cansado"
```

The problem was the fixed-size context vector.

For long input sequences, retaining every important detail in that single representation became difficult.

Attention introduced another possibility: allow the decoder to access multiple encoder representations, assigning different weights to them at each decoding step.

```text
ATTENTION-BASED SEQ2SEQ

ENCODER

I      am     very   tired
|      |      |      |
v      v      v      v
[h1]   [h2]   [h3]   [h4]
|      |      |      |
+------+------+------+
       |
       v
+---------------+
|   Attention   |
+---------------+
       |
       v
    DECODER
       |
       v
Next output token
```

The decoder no longer has to depend exclusively on one compressed summary.

It can dynamically retrieve relevant information from the encoder states.

This approach was established in neural machine translation by Bahdanau, Cho, and Bengio in 2014.

## 3. The three fundamental components: Query, Key, and Value

Modern attention is commonly implemented using three types of vectors:

- Query (Q): Represents the information being sought.
- Key (K): Represents information used to determine whether an item is relevant to a query.
- Value (V): Represents the information contributed by an item.

An analogy is a search operation.

```text
QUERY
"What is relevant?"
    |
    v
+----------------+
| Match against  |
| available keys |
+----------------+
    |
    v
Relevance Scores
    |
    v
Attention Weights
    |
    v
Weighted combination of matching values
    |
    v
OUTPUT
```

The distinction between keys and values matters.

A key determines relevance, while a value supplies information.

### How Q, K, and V are created

Suppose an input token is represented by a vector `x_i`.

A Transformer computes query, key, and value vectors using learned linear projections:

```text
q_i = x_i * W_Q
```

```text
k_i = x_i * W_K
```

```text
v_i = x_i * W_V
```

Where `W_Q`, `W_K`, and `W_V` are trainable weight matrices.

These matrices are learned through training. The programmer does not manually specify which linguistic concepts the keys or queries should encode.

```text
         Token Vector
              x
              |
    +---------+---------+
    |         |         |
    v         v         v
   W_Q       W_K       W_V
    |         |         |
    v         v         v
  Query      Key      Value
    Q         K         V
```

A token therefore has different learned representations for requesting information, matching requests, and contributing information.

## 4. How attention is calculated

The most widely used formulation is scaled dot-product attention.

The process has four main steps.

### Step 1: Calculate relevance scores

For a query `q`, attention compares it against the available keys.

A dot product measures compatibility between two vectors:

```text
s_i = dot(q, k_i)
```

A larger score generally means that the key is more compatible with the query.

In the standard scaled formulation, the score is:

```text
s_i = dot(q, k_i) / sqrt(d_k)
```

Where `d_k` is the dimensionality of the key vectors.

Why divide by `sqrt(d_k)`?

With certain assumptions about the vector components, dot-product magnitudes tend to increase with dimensionality. Large scores can drive softmax into saturated regions, producing very small gradients.

Scaling helps stabilize this behavior.

### Step 2: Convert scores into weights

The raw scores are passed through softmax:

```text
alpha_i = exp(s_i) / sum(j, exp(s_j))
```

Softmax produces nonnegative weights that sum to one.

For example:

```text
Key       Raw score      Attention weight
---       ---------      ----------------
K1              1.0                  0.20
K2              2.2                  0.66
K3              0.5                  0.14
                                     ----
                                     1.00
```

The model assigns the highest weight to `K2`.

### Step 3: Retrieve and combine values

Once the weights are available, the mechanism calculates a weighted sum of the value vectors:

```text
z = sum(i, alpha_i * v_i)
```

For a simple example:

```text
v_1 = [1, 0], v_2 = [0, 2], v_3 = [3, 1]
```

Suppose the attention weights are:

```text
alpha = [0.1, 0.7, 0.2]
```

Then:

```text
z = 0.1 * [1, 0] + 0.7 * [0, 2] + 0.2 * [3, 1]
```

```text
z = [0.7, 1.6]
```

The output is a new vector formed by combining information from the available values.

### Step 4: Use the resulting representation

The attention output can then be passed into subsequent neural network computations.

```text
Query
|
v
+-------------------+
| Compare with Keys |
+-------------------+
|
v
Raw Scores
|
v
Scaling
|
v
Softmax
|
v
Attention Weights
|
v
+-----------------+
| Weighted Sum of |
| Value Vectors   |
+-----------------+
|
v
Output Vector
```

The complete operation is expressed compactly as:

```text
Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V
```

This is the fundamental scaled dot-product attention equation used in Transformers.

## 5. Self-attention

Self-attention is attention in which the queries, keys, and values are derived from the same sequence of representations.

Consider:

```text
        "The"   "cat"   "sleeps"
          |       |        |
          v       v        v
         [x1]    [x2]     [x3]
          |       |        |
          +-------+--------+
                  |
                  v
            Self-Attention
                  |
                  v
         [z1]    [z2]    [z3]
```

Each output representation is computed using a query for that position and the permitted keys and values from the sequence.

For example, when calculating the new representation of "sleeps", the model can use information from "The", "cat", and "sleeps".

This creates contextualized token representations.

The vector representing "sleeps" is no longer based only on that token. It incorporates information about the surrounding context.

### The attention matrix

For a sequence containing four tokens, full self-attention computes an attention score for every pair of positions:

```text
              Keys

                T1    T2    T3    T4
              +-----------------------+
Query T1      | a11   a12   a13   a14 |
Query T2      | a21   a22   a23   a24 |
Query T3      | a31   a32   a33   a34 |
Query T4      | a41   a42   a43   a44 |
              +-----------------------+
```

Every row represents the weights used to construct one output representation.

Each row sums to one after softmax, assuming no dropout is applied to the attention weights.

An important detail: attention does not inherently know token order. Positional information must be incorporated through mechanisms such as positional embeddings or relative position encodings.

## 6. Self-attention versus cross-attention

These are two closely related mechanisms.

### Self-attention

Queries, keys, and values come from the same sequence.

```text
   SEQUENCE A
       |
+------+------+
|      |      |
v      v      v
Q      K      V
|      |      |
+------+------+
       |
       v
   Attention
       |
       v
     Output
```

This allows representations within one sequence to interact.

### Cross-attention

Queries come from one sequence, while keys and values come from another sequence.

For an encoder-decoder model:

```text
        DECODER              ENCODER
           |                    |
           v                    v
        Queries              Encoded
          (Q)             Representations
           |                    |
           |               +----+----+
           |               |         |
           |               v         v
           |              Keys     Values
           |               K         V
           |               |         |
           +---------------+---------+
                           |
                           v
                     Cross-Attention
                           |
                           v
                     Decoder Output
```

This allows the decoder to retrieve relevant information from the encoded input.

For example, during translation, the decoder can attend to source-language representations while generating target-language tokens.

## 7. Multi-head attention

A single attention operation produces one set of attention weights and a corresponding output representation.

However, a sequence can contain several relationships simultaneously: grammatical dependencies, semantic relationships, references, and other contextual patterns.

Multi-head attention allows several learned attention operations to run in parallel, each with its own projection matrices.

```text
               Input Representations
                         |
            +------------+------------+
            |            |            |
            v            v            v
         Head 1       Head 2       Head 3
            |            |            |
            v            v            v
        Attention    Attention    Attention
            |            |            |
            v            v            v
           Z1           Z2           Z3
            |            |            |
            +------------+------------+
                         |
                         v
                    Concatenate
                         |
                         v
                 Output Projection
                         |
                         v
                   Final Output
```

Each head independently projects the input into query, key, and value representations and calculates attention.

The head outputs are concatenated and passed through another learned projection.

Mathematically:

```text
head_i = Attention(Q * W_i^Q, K * W_i^K, V * W_i^V)
```

```text
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) * W^O
```

The heads can learn different relationships, although particular heads are not guaranteed to correspond to neatly interpretable linguistic functions.

The original Transformer architecture established this multi-head formulation.

## 8. Causal attention: how autoregressive LLMs avoid seeing the future

Standard full self-attention allows every token to attend to every other token.

That is suitable for many encoder architectures.

However, an autoregressive language model predicts future tokens from preceding tokens.

When predicting a token, access to later tokens would leak information that should not be available.

This is why decoder-only LLMs commonly use causal attention, implemented with an attention mask.

```text
             Keys

                T1   T2   T3   T4
             +--------------------+
Query T1     |  Y    X    X    X  |
Query T2     |  Y    Y    X    X  |
Query T3     |  Y    Y    Y    X  |
Query T4     |  Y    Y    Y    Y  |
             +--------------------+

Y = Attention permitted
X = Attention blocked
```

The model can use the current token and preceding tokens, but not future tokens.

Before applying softmax, disallowed positions are assigned a very large negative score (conceptually negative infinity), making their attention weights zero.

This masking mechanism is a core part of causal Transformer architectures.

## 9. Why attention changed neural network architectures

RNNs and attention-based Transformers organize computation differently.

### RNN

```text
x1 ---> [RNN] ---> [RNN] ---> [RNN] ---> [RNN]
                     ^          ^          ^
                     |          |          |
                     x2         x3         x4
```

Each recurrent state depends on the preceding state.

Consequently, the states within a sequence generally require sequential computation.

### Transformer self-attention

```text
    x1    x2    x3    x4
    |     |     |     |
    v     v     v     v
+-------------------------+
|      Self-Attention     |
+-------------------------+
    |     |     |     |
    v     v     v     v
    z1    z2    z3    z4
```

At a given layer, attention can calculate representations for multiple token positions in parallel when the entire input sequence is available.

This allows efficient use of matrix multiplication accelerators such as GPUs.

It also provides more direct computational paths between distant token positions than traditional recurrence.

However, attention has costs.

## 10. Engineering trade-offs

### Quadratic attention complexity

With standard dense self-attention, every query position computes compatibility scores with every key position.

For a sequence of `n` tokens, that creates `n^2` scores per attention head.

| Sequence length | Attention score count per head |
| --------------- | ------------------------------ |
| 1,000           | 1 million                      |
| 10,000          | 100 million                    |
| 100,000         | 10 billion                     |

For fixed query/key dimensions, the score calculation scales quadratically with sequence length.

Naively storing the attention matrix also requires `O(n^2)` memory.

This makes long-context processing expensive.

Optimizations such as FlashAttention reduce memory traffic and avoid materializing the full attention matrix in high-bandwidth GPU memory, while preserving exact attention results under the algorithm's numerical implementation. They do not eliminate the underlying quadratic arithmetic of dense attention.

### KV caching

In autoregressive inference, previously processed tokens do not need to have their keys and values recomputed at every generation step.

A KV cache stores those representations for reuse.

```text
            GENERATION STEP t

         New Token Representation
                    |
                    v
              New Q, K, V
                    |
                    +------------+
                    |            |
                    v            v
                Query       Append K, V
                    |            |
                    |            v
                    |        KV Cache
                    |            |
                    +------------+
                           |
                           v
                        Attention
                           |
                           v
                       Next Token
```

KV caching improves generation efficiency but introduces memory overhead that grows with the number of stored positions.

This creates important trade-offs involving context length, GPU memory, throughput, and batch size.

## 11. Common misconceptions

Attention is not the same as memory. It retrieves and aggregates information from available representations. Whether that information persists depends on the surrounding architecture and its state-management mechanisms.

Attention weights are not necessarily explanations. A high weight indicates how strongly a value contributes to a particular weighted aggregation, but it does not automatically provide a reliable causal explanation of the model's final decision.

Attention is not the entire Transformer. Transformers also use feed-forward networks, normalization, residual connections, positional information, and other components.

Attention does not guarantee unlimited context. Models remain constrained by computational resources, architectural context limits, and their ability to use distant information effectively.

## 12. Key engineering takeaways

1. Attention performs content-dependent information aggregation. Queries identify what information is relevant; keys provide matching signals; values provide information to combine.
2. Relevance is learned. The query, key, and value projections are trainable parameters.
3. Self-attention contextualizes representations by allowing positions within a sequence to exchange information.
4. Cross-attention connects different representations, such as a decoder's state and an encoder's output.
5. Multi-head attention supports multiple learned interaction patterns in parallel.
6. Causal masking enforces autoregressive dependencies, preventing future-token information leakage.
7. Attention enables substantial training parallelism, but standard dense self-attention introduces quadratic sequence-length costs.

The fundamental equation remains:

```text
Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V
```

The deepest architectural insight is that a token representation does not need to be computed independently or solely from a compressed recurrent history. It can be constructed dynamically from the relevant information available throughout a sequence.

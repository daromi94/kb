# Attention, step by step

## Step 1: The fundamental idea

Consider this sentence:

> The cat sleeps.

Suppose a neural network is processing the word "sleeps".

The word "sleeps" has meaning by itself, but its meaning in this sentence is connected to "cat".

Attention allows the network to incorporate information from other tokens when computing a new representation for "sleeps".

Imagine that the model assigns these attention weights:

```text
Sentence: "The cat sleeps"

Token being processed: "sleeps"

                    Attention
                       weight

    "The"    ---------- 0.10
    "cat"    ---------- 0.70
    "sleeps" ---------- 0.20
                        ----
                        1.00
```

These are illustrative weights, not actual values from a trained model.

The weights determine how much information each token contributes to the new representation of "sleeps".

```text
     "The"          "cat"        "sleeps"
       |              |             |
       v              v             v
      0.10           0.70          0.20
       |              |             |
       +--------------+-------------+
                      |
                      v
             Weighted combination
                      |
                      v
       New representation of "sleeps"
```

Three important observations:

- Attention does not simply select one word. It combines information from multiple tokens.
- Attention weights determine the relative contribution of the tokens' value vectors.
- The result is a new vector, not a word or sentence.

The actual vectors and weights are learned through training.

The weight of `0.70` means that the value vector associated with "cat" is multiplied by `0.70` when constructing the new representation of "sleeps".

Now comes the interesting part: how does the model calculate that weight?

## Step 2: How attention determines relevance

Attention begins by calculating a relevance score between tokens.

For this, it uses two vectors:

- Query (Q): Represents what the current token is looking for.
- Key (K): Represents information that another token offers for matching.

Consider the same sentence:

> The cat sleeps.

Suppose attention is calculating a new representation for "sleeps".

```text
                      "sleeps"
                         |
                         v
                     Query (Q)
                         |
                  Compare against
                         |
            +------------+------------+
            |            |            |
            v            v            v
         Key(The)     Key(cat)    Key(sleeps)
            |            |            |
            v            v            v
          Score        Score        Score
```

### 2.1 How are scores calculated?

Attention can calculate relevance using the dot product of a query and a key.

For simplicity, imagine that the vectors contain just two numbers.

The query for "sleeps" is:

```text
Q_sleeps = [1, 0]
```

And the keys are:

```text
K_The = [0, 1]
```

```text
K_cat = [2, 0]
```

```text
K_sleeps = [1, 0]
```

These are invented vectors for teaching purposes, not real learned embeddings.

The dot product multiplies corresponding elements and adds the results:

```text
dot([a, b], [c, d]) = a * c + b * d
```

Now calculate the scores.

"sleeps" compared with "The":

```text
dot([1, 0], [0, 1]) = 0
```

"sleeps" compared with "cat":

```text
dot([1, 0], [2, 0]) = 2
```

"sleeps" compared with "sleeps":

```text
dot([1, 0], [1, 0]) = 1
```

The results:

```text
Query: "sleeps" = [1, 0]

Token       Key       Dot Product    Score
------------------------------------------
The         [0, 1]          0 + 0        0
cat         [2, 0]          2 + 0        2
sleeps      [1, 0]          1 + 0        1
```

The highest score belongs to "cat".

In this artificial example, its key is the most compatible with the query for "sleeps".

Notice something important: these scores are not probabilities. They are raw compatibility scores.

The numbers `0`, `2`, and `1` must still be converted into attention weights. That will be Step 3.

### 2.2 Where do queries and keys come from?

They are generated from token representations using learned weight matrices.

```text
       Token Vector
            |
    +-------+-------+
    |               |
    v               v
Matrix Wq       Matrix Wk
    |               |
    v               v
  Query            Key
```

These matrices are learned during training, enabling the model to develop useful ways of comparing tokens.

For now, the important relationship is:

```text
Relevance Score = dot(Q, K)
```

Standard Transformer attention also scales this score by the square root of the key dimension, but that detail can come later.

## Step 3: Turning relevance scores into attention weights

Recall the sentence:

> The cat sleeps.

In Step 2, the query for `"sleeps"` was compared against the keys of all three tokens.

The resulting scores were:

```text
Query: "sleeps"

Token        Relevance score
----------------------------
The                        0
cat                        2
sleeps                     1
```

But there is a problem.

These scores are not yet suitable for computing a normalized weighted combination because they do not sum to 1.

We need a function that converts raw scores into normalized weights.

That function is called softmax.

### 3.1 What does softmax do?

Softmax converts a collection of numerical scores into nonnegative weights that sum to 1.

It also preserves their ranking: a larger input score produces a larger output weight.

For our example:

```text
Relevance Scores
[0, 2, 1]
    |
    v
Softmax
    |
    v
Attention Weights
[0.09, 0.67, 0.24]
    |
    v
Sum = 1
```

The model now assigns approximately:

| Token  | Score | Attention weight |
| ------ | ----- | ---------------- |
| The    | 0     | 0.09             |
| cat    | 2     | 0.67             |
| sleeps | 1     | 0.24             |
| Total  |       | 1.00             |

Notice that `"cat"` receives the highest weight because it has the highest relevance score.

### 3.2 How does softmax calculate these values?

The mathematical formula is:

```text
softmax(s_i) = exp(s_i) / sum(j, exp(s_j))
```

It performs two operations.

First: Exponentiate each score.

```text
e^0 = 1
```

```text
e^2 ~= 7.39
```

```text
e^1 ~= 2.72
```

Second: Divide each result by their sum.

The sum is:

```text
1 + 7.39 + 2.72 = 11.11
```

Therefore:

```text
alpha_The = (1 / 11.11) ~= 0.09
```

```text
alpha_cat = (7.39 / 11.11) ~= 0.67
```

```text
alpha_sleeps = (2.72 / 11.11) ~= 0.24
```

These are the attention weights.

For simplicity, this example applies softmax directly to the raw dot products. Standard Transformer attention first scales them by `sqrt(d_k)`, which changes the numerical weights but not the underlying process.

### 3.3 Why is this useful?

The model now has a numerical mechanism for determining the relative contributions of different tokens.

```text
        "The"       "cat"      "sleeps"
          |           |           |
          v           v           v
         0.09        0.67        0.24
          |           |           |
          +-----------+-----------+
                      |
                      v
              Weighted combination
                      |
                      v
            New representation of
                  "sleeps"
```

One important detail: these weights are not probabilities that a word is correct. They control how strongly the corresponding value vectors contribute to the attention output.

The actual vectors to be combined are called Values (V), which will be the subject of Step 4.

Now comes the final piece of the basic attention mechanism.

## Step 4: What are Values (V), and how does attention produce its output?

So far, three things have happened:

1. A Query (Q) was created for `"sleeps"`.
2. The query was compared against Keys (K) to calculate relevance scores.
3. Softmax converted those scores into attention weights.

Recall the result:

```text
Query: "sleeps"

Token        Attention weight
-----------------------------
The                      0.09
cat                      0.67
sleeps                   0.24
                         ----
                         1.00
```

But what happens with these weights?

### 4.1 Introducing Values (V)

Every token also has a third vector, called its Value.

The distinction is important:

- Query: What information is relevant?
- Key: How relevant is this token to the query?
- Value: What information does this token contribute?

Consider a simple example with two-dimensional value vectors:

```text
Token       Value vector
------------------------
The              [1, 0]
cat              [0, 2]
sleeps           [2, 1]
```

These are invented vectors for illustration. In a real model, they are produced through learned projections of the token representations.

### 4.2 Multiplying each Value by its attention weight

Attention multiplies each value vector by its corresponding weight.

For `"The"`:

```text
0.09 * [1, 0] = [0.09, 0]
```

For `"cat"`:

```text
0.67 * [0, 2] = [0, 1.34]
```

For `"sleeps"`:

```text
0.24 * [2, 1] = [0.48, 0.24]
```

The complete operation:

```text
Token         Value      Weight     Weighted Value
--------------------------------------------------
The          [1, 0]        0.09       [0.09, 0.00]
cat          [0, 2]        0.67       [0.00, 1.34]
sleeps       [2, 1]        0.24       [0.48, 0.24]
```

Notice that `"cat"` receives the highest weight, so its value is multiplied by the largest factor.

However, all three value vectors contribute to the result.

### 4.3 Adding the weighted Values

The final operation is to add the weighted vectors together.

```text
z = 0.09 * V_The + 0.67 * V_cat + 0.24 * V_sleeps
```

Substituting the calculated vectors:

```text
z = [0.09, 0] + [0, 1.34] + [0.48, 0.24]
```

Therefore:

```text
z = [0.57, 1.58]
```

This is the attention output for `"sleeps"` in our example.

```text
                Query: "sleeps"
                       |
                       v
               Attention Weights
                       |
          +------------+------------+
          |            |            |
          v            v            v
         0.09         0.67         0.24
          |            |            |
          v            v            v
        [1,0]        [0,2]        [2,1]
          |            |            |
          v            v            v
      [0.09,0]     [0,1.34]    [0.48,0.24]
          |            |            |
          +------------+------------+
                       |
                       v
                  Vector Sum
                       |
                       v
                 [0.57, 1.58]
                       |
                       v
               Attention Output
                 for "sleeps"
```

### 4.4 What does this output actually represent?

The output `[0.57, 1.58]` is not a word or a prediction.

It is a new vector representation for `"sleeps"`, constructed by combining information from the three tokens.

In a real Transformer, this vector is subsequently processed by other operations, such as output projections, residual connections, normalization, and feed-forward layers.

The attention operation itself simply produces a weighted combination of value vectors.

### 4.5 Putting everything together

Here is the complete process developed across the four steps:

```text
                  "The cat sleeps"
                         |
                         v
               Token Representations
                         |
                         v
                 Learned Projections
                         |
              +----------+----------+
              |          |          |
              v          v          v
           Queries      Keys      Values
              |          |          |
              +----+-----+          |
                   |                |
                   v                |
             Dot Products           |
                   |                |
                   v                |
             Relevance Scores       |
                   |                |
                   v                |
                 Softmax            |
                   |                |
                   v                |
             Attention Weights      |
                   |                |
                   +--------+-------+
                            |
                            v
                       Weighted Sum
                            |
                            v
                      Output Vector
```

The mathematical expression summarizing the operation for a single query is:

```text
z = sum(i, alpha_i * v_i)
```

## Step 5: How Queries, Keys, and Values are created and learned

So far, the examples have assumed that every token already has a Query, Key, and Value.

But where did those vectors come from?

### 5.1 Everything starts with a token representation

Consider the sentence:

> The cat sleeps.

Before attention, the model converts each token into a numerical representation.

For simplicity, imagine:

```text
Token       Input vector
------------------------
The            [1, 0, 0]
cat            [0, 1, 0]
sleeps         [0, 0, 1]
```

These are simplified one-hot vectors. Real Transformers use dense token embeddings and incorporate positional information. In deeper layers, the input vectors are representations produced by preceding layers.

The important point is that attention receives vectors, not words directly.

### 5.2 A token produces three different vectors

Each input representation is multiplied by three learned matrices:

- `W_Q`: Query projection matrix.
- `W_K`: Key projection matrix.
- `W_V`: Value projection matrix.

```text
                   Input vector
                    x_sleeps
                        |
            +-----------+-----------+
            |           |           |
            v           v           v
           W_Q         W_K         W_V
            |           |           |
            v           v           v
          Query        Key        Value
```

Mathematically:

```text
Q = x * W_Q
```

```text
K = x * W_K
```

```text
V = x * W_V
```

The same projection matrices are reused across token positions within a particular attention head.

Let's calculate one of these projections.

### 5.3 A concrete example

Take the input vector for `"sleeps"`:

```text
x_sleeps = [0, 0, 1]
```

Suppose the learned Query matrix is:

```text
W_Q = [[0, 1], [1, 1], [1, 0]]
```

Multiply the input vector by the matrix:

```text
Q_sleeps = [0, 0, 1] * [[0, 1], [1, 1], [1, 0]]
```

The result is:

```text
Q_sleeps = [1, 0]
```

Notice that this is exactly the Query vector used in Step 2!

With these simplified one-hot inputs, multiplying by the matrix selects its third row.

Similarly, suppose the Key and Value matrices are:

```text
W_K = [[0, 1], [2, 0], [1, 0]]

W_V = [[1, 0], [0, 2], [2, 1]]
```

Applying these projections to all three tokens reproduces the earlier example:

| Token  | Query  | Key    | Value  |
| ------ | ------ | ------ | ------ |
| The    | [0, 1] | [0, 1] | [1, 0] |
| cat    | [1, 1] | [2, 0] | [0, 2] |
| sleeps | [1, 0] | [1, 0] | [2, 1] |

Now the complete process makes sense:

```text
Input tokens
     |
     v
Token representations
     |
     +----------------+----------------+
     |                |                |
     v                v                v
 Query vectors     Key vectors     Value vectors
     |                |                |
     +-------+--------+                |
             |                         |
             v                         |
       Dot products                    |
             |                         |
             v                         |
       Attention weights               |
             |                         |
             +------------+------------+
                          |
                          v
                    Weighted sum
                          |
                          v
                    Output vectors
```

But there is still one critical question.

Who determines the numbers inside the three matrices?

### 5.4 How the model learns the matrices

The matrices are model parameters.

Initially, their values are typically randomly initialized.

During training, the model learns useful values through gradient-based optimization.

Consider a language model processing:

> The cat sleeps on the

Its task might be to predict the next token, such as `"mat"`.

The simplified training process is:

```text
Training text
    |
    v
Token embeddings
    |
    v
Q, K, V matrices
    |
    v
Attention
    |
    v
Remaining layers
    |
    v
Token prediction
    |
    v
Calculate loss
    |
    v
Backpropagation
    |
    v
Update parameters (including W_Q, W_K and W_V)
    |
    v
Repeat training
```

Suppose the model predicts an incorrect token.

The loss function measures how poorly the prediction matches the training target.

Backpropagation calculates gradients showing how changes in the parameters would affect that loss.

The optimizer updates the parameters, including the Query, Key, and Value projection matrices.

Over many training examples, these matrices can learn to produce representations that help the model capture useful token relationships.

#### An important distinction

The model is not explicitly told:

> "When processing 'sleeps', pay 70% attention to 'cat'."

Instead, the model learns projection matrices that influence its attention scores. Those matrices are optimized indirectly through the overall training objective.

That is how useful attention patterns can emerge without manually programming linguistic relationships.

### 5.5 The key realization

Three concepts are now connected:

1. Token representations supply the original information.
2. Learned projection matrices transform that information into Queries, Keys, and Values.
3. Attention uses those vectors to construct context-dependent output representations.

And an important subtlety: the projection matrices are persistent learned parameters, whereas Queries, Keys, Values, and attention weights are calculated dynamically for each input.

# Recurrent Neural Networks (RNNs)

A Recurrent Neural Network (RNN) is a neural network architecture designed to process sequential data by maintaining an internal state that carries information from previous inputs.

The central idea is simple:

Instead of processing each input independently, an RNN uses information from previous inputs to interpret the current input.

RNNs were particularly important in natural language processing (NLP), speech recognition, time-series forecasting, and machine translation before Transformers became dominant in many of these applications.

## 1. The problem RNNs solve

Consider the sentence:

> The cat sat on the ...

A language model should predict a plausible next word, such as "mat."

However, predicting that word requires understanding the preceding words.

A traditional feedforward neural network processes an input without having an inherent memory of previous inputs. It can accept a fixed context window, but the architecture does not naturally maintain a state across arbitrary sequence steps.

An RNN introduces a mechanism for retaining information as the sequence is processed.

```text
Input sequence
|
v
"The" "cat" "sat" "on"  "the"
|     |     |     |     |
v     v     v     v     v
+-----+-----+-----+-----+----+
| RNN | RNN | RNN | RNN | RNN|
+-----+-----+-----+-----+----+

|---->|---->|---->|---->
State flows forward
```

Every step receives two pieces of information:

1. Current input: The current token, measurement, or observation.
2. Previous hidden state: A learned representation summarizing the information accumulated from preceding steps.

This recurrent state allows the network to model sequential dependencies.

## 2. How an RNN works

An RNN consists of a recurrent computational unit, often called an RNN cell.

At each time step, the cell reads an input, updates its internal state, and can produce an output.

```text
                  h(t-1)
                    |
                    v
              +----------+
    x(t) ---->| RNN Cell |----> h(t)
              +----------+        |
                    |             |
                    v             |
                   y(t)           |
                                  v
                             Next RNN Cell
```

Where:

- `x(t)` is the input at time step `t`.
- `h(t-1)` is the previous hidden state.
- `h(t)` is the newly computed hidden state.
- `y(t)` is an optional output or prediction.

The most important relationship is:

```text
h_t = f(x_t, h_(t-1))
```

In other words, the new hidden state is a function of the current input and the previous hidden state.

For a basic RNN using a hyperbolic tangent activation, this becomes:

```text
h_t = tanh(W_xh * x_t + W_hh * h_(t-1) + b_h)
```

Here:

| Component | Meaning                          |
| --------- | -------------------------------- |
| `x_t`     | Current input vector             |
| `h_(t-1)` | Previous hidden-state vector     |
| `W_xh`    | Learned input-to-hidden weights  |
| `W_hh`    | Learned hidden-to-hidden weights |
| `b_h`     | Bias vector                      |
| `tanh`    | Nonlinear activation function    |

An optional output layer might compute:

```text
y_t = W_hy * h_t + b_y
```

Here, `W_hy` contains learned hidden-to-output weights, and `b_y` is the output bias vector.

For token prediction, the output logits are typically converted into probabilities using softmax.

These equations describe the classic Elman-style RNN implemented in frameworks such as PyTorch.

The key distinction is that the hidden state changes with each input, while the model's learned weight matrices are reused at every step.

## 3. Understanding the hidden state: the most important concept

The hidden state is the mechanism that gives an RNN its ability to retain information across time.

However, it is important to understand that the hidden state is not a database of previous inputs.

It is a fixed-size vector of numbers whose values are learned representations of the sequence processed so far.

Consider:

> The movie was not good.

An RNN performing sentiment analysis might process the sentence as follows:

```text
Time     Input       Hidden State
----     -----       ------------
t=0      -           h0 (initialized)


t=1      "The" ----> h1
                         |
                         v
t=2      "movie" ------> h2
                             |
                             v
t=3      "was" ------------> h3
                                 |
                                 v
t=4      "not" ----------------> h4
                                     |
                                     v
t=5      "good" -------------------> h5
                                     |
                                     v
                            Sentiment: Negative
```

The word "good" is usually associated with positive sentiment. However, its interpretation changes because of the preceding word "not."

The hidden state can encode information about the negation, allowing the network to interpret the complete sentence.

Several properties are important:

- The hidden state typically has a fixed dimensionality, regardless of sequence length.
- It is updated after every element.
- Earlier information can be retained, transformed, or overwritten.
- There is no guarantee that important information will survive indefinitely.

The last point leads to one of the fundamental limitations of traditional RNNs.

## 4. Recurrence and weight sharing

An RNN is called recurrent because the same computational operation is applied repeatedly, with the result of one step influencing the next.

An equivalent representation is to unroll the RNN over time:

```text
            h0          h1          h2          h3
            |           |           |           |
            v           v           v           v
    x1 -->[RNN]--h1-->[RNN]--h2-->[RNN]--h3-->[RNN]
            |           |           |           |
            v           v           v           v
            y1          y2          y3          y4
```

Here, each RNN box represents the same cell with the same trainable parameters, evaluated at a different time step.

There are not four independently learned networks.

For example, if the hidden state has 128 dimensions, the recurrent weight matrix `W_hh` has shape `128 x 128`, regardless of whether the sequence contains 10 or 10,000 elements.

This parameter sharing is a defining characteristic of RNNs.

It has two consequences.

First, RNNs can naturally operate on variable-length sequences without changing the number of model parameters.

Second, each state transition depends on the preceding state. Consequently, the time steps of a standard RNN cannot be computed simultaneously for an individual sequence.

That creates an important performance limitation.

## 5. How RNNs are trained: Backpropagation Through Time

Training an RNN usually involves a technique called Backpropagation Through Time (BPTT).

The basic idea is to unroll the network, calculate a loss, and propagate gradients backward across the sequence.

```text
Forward pass:

x1 ---> RNN1 ---> RNN2 ---> RNN3 ---> RNN4
         |         |         |         |
         v         v         v         v
         y1        y2        y3        y4
                                       |
                                       v
                                      Loss


Backward pass (simplified):

        <--------- gradients <---------

RNN1 <--- RNN2 <--- RNN3 <--- RNN4 <--- Loss
```

Because the same parameters are used at every time step, their gradients receive contributions from multiple steps.

The optimizer then updates the shared parameters.

In principle, this allows an error at the end of a sequence to influence how earlier inputs are processed.

However, it introduces two problems.

### Problem A: Vanishing gradients

During backpropagation, gradients are repeatedly multiplied by derivatives associated with the recurrent state transitions.

If these products repeatedly reduce the gradient magnitude, the signal becomes extremely small.

For illustration, suppose a gradient is multiplied by 0.5 at each step:

```text
0.5^10 ~= 0.00098
```

```text
0.5^100 ~= 7.9 * 10^-31
```

Eventually, early time steps receive almost no useful learning signal.

This makes it difficult for a conventional RNN to learn long-range dependencies.

### Problem B: Exploding gradients

The opposite can also happen.

When the products repeatedly amplify the gradient, its magnitude can become extremely large, destabilizing training.

Gradient clipping is a common technique for controlling exploding gradients, while truncated BPTT limits how far backward the gradient is propagated during a training update.

Both issues arise from repeated application of the chain rule through recurrent computations.

## 6. LSTM: improving long-term memory

To address the difficulty of learning long-range dependencies, a more sophisticated recurrent architecture was introduced: Long Short-Term Memory (LSTM).

Unlike a basic RNN, an LSTM maintains two forms of state:

- Hidden state: Information exposed to subsequent computations.
- Cell state: An additional pathway for carrying information through time.

LSTMs introduce learned gates that regulate information flow.

```text
              Previous Cell State
                       |
                       v
              +------------------+
              |                  |
Current ----->|   LSTM Cell      |----> Hidden State
 Input        |                  |
              |  Forget Gate     |
              |  Input Gate      |
              |  Output Gate     |
              +------------------+
                       |
                       v
                 New Cell State
```

Conceptually:

- The forget gate determines how much of the previous cell state to retain.
- The input gate controls how much candidate information to incorporate.
- The output gate determines how much of the cell state to expose through the hidden state.

A central LSTM equation is:

```text
c_t = f_t .* c_(t-1) + i_t .* g_t
```

Here, `c_t` is the updated cell state, `f_t` is the forget gate, `i_t` is the input gate, and `g_t` is candidate information. `.*` means element-wise multiplication.

The additive path through the cell state helps gradients propagate across longer intervals, although it does not guarantee unlimited memory.

LSTMs were specifically developed to overcome the difficulty of learning long-term dependencies in recurrent networks.

## 7. GRU: a simpler gated RNN

A Gated Recurrent Unit (GRU) provides another approach to controlling information retention.

Compared with LSTMs, GRUs use a simpler structure with two principal gates:

- Reset gate: Controls the contribution of previous state information when forming a candidate state.
- Update gate: Controls how much previous state is retained versus replaced.

Unlike LSTMs, GRUs do not maintain a separate cell-state vector.

They often require fewer trainable parameters for comparable input and hidden dimensions, although performance depends on the workload and model configuration.

## 8. Where RNNs remain useful

RNNs are not obsolete. They remain relevant for applications where sequential processing and compact state are desirable.

Examples include real-time sensor analysis, streaming signal processing, embedded machine learning, forecasting, and applications with constrained inference resources.

A recurrent architecture may be advantageous when observations arrive continuously and retaining an entire history is unnecessary.

For example:

```text
Sensor stream
     |
     v
Observation 1 ---> State 1
                     |
Observation 2 ---> State 2
                     |
Observation 3 ---> State 3
                     |
Observation 4 ---> State 4
                     |
                     v
                Anomaly Score
```

At inference time, a unidirectional RNN can process the next observation using its current input and previously retained state without reprocessing the entire sequence.

This can provide memory usage independent of the length of the processed stream for a fixed-size recurrent state, excluding any outputs or history deliberately retained elsewhere.

## 9. Key engineering takeaways

1. Recurrence is the defining mechanism. The previous hidden state influences the current computation.
2. Hidden state is learned, compressed information, not a lossless history of previous inputs.
3. Weights are shared across time. Sequence length does not determine the number of recurrent parameters.
4. Long-term dependencies are difficult for basic RNNs, largely because of gradient propagation challenges.
5. LSTMs and GRUs introduce gates to improve information retention and learning.
6. Compact recurrent state remains useful, particularly for certain streaming and resource-constrained workloads.

The most important concept is that an RNN transforms a sequence into an evolving state:

```text
h_t = f(x_t, h_(t-1))
```

That single relationship explains both its primary strength—processing sequences with accumulated context—and its central limitation: information and computation must propagate through successive state transitions.

# Foundation models

A foundation model is trained on broad data and can be adapted to many tasks. Its main value is reuse: one trained base can support several applications.

For example, a language model can provide a starting point for summarization, translation, classification, and question answering.

## Learn a base, then adapt it

**Pretraining** builds the base model. It learns patterns from a large dataset before being adapted to a particular application.

For language, those patterns can include word usage, sentence structure, code structure, and relationships described in text.

```text
broad training data
         |
         v
     pretraining
         |
         v
  foundation model
         |
         +--> summarization
         +--> translation
         +--> classification
         +--> question answering
```

The same base supports different uses. Each application still needs a suitable way to guide, adapt, and evaluate it.

## Where the training signal comes from

Foundation models often use **self-supervised learning**. The data supplies the training targets.

A text model can predict the next token from earlier tokens. An image model can learn from missing regions or different views of the same image.

This makes broad training practical because every example does not need a manually assigned task label.

The full training process can also include labeled examples and feedback. Self-supervision is a common starting point, not the only possible training step.

## Ways to adapt the base

Different adaptations change different parts of the system:

- **Prompting** supplies instructions, examples, or context without changing the model's parameters.
- **Fine-tuning** updates model parameters using examples for a particular behavior or domain.
- **Parameter-efficient fine-tuning** updates a smaller set of parameters. Low-rank adaptation, or **LoRA**, is one method.
- **Retrieval-augmented generation**, or **RAG**, retrieves relevant material and supplies it as context for a generated answer.

The distinction matters because adding information to a prompt is different from changing the model itself.

```text
prompting:    existing model + instructions
fine-tuning:  base parameters --> adapted parameters
retrieval:    question --> relevant material --> model input
```

## Reuse changes the cost structure

One approach trains a separate model for each task. Another invests in a broad pretrained model and reuses it.

| Question               | Separate task models       | Shared foundation model     |
| ---------------------- | -------------------------- | --------------------------- |
| Starting point         | A model for each task      | One broadly trained base    |
| New task               | Task-specific development  | Prompt or adapt the base    |
| Large training cost    | Paid for individual models | Shared across applications  |
| Application evaluation | Needed for every task      | Still needed for every task |

Reuse can reduce repeated development work. Adaptation and serving still have costs, and a smaller specialized model can be a better fit for a narrow task.

## Text is one possible input

A foundation model can work with text, images, audio, or other data.

A **multimodal model** handles more than one kind of input or output. For example, it can use an image and a question together to produce an explanation.

Multimodality is a capability a model may have. It is not a requirement for being a foundation model.

## Broad capability still needs testing

Larger training runs can improve performance and produce capabilities that smaller models do not demonstrate on a given evaluation. These are often described as **emergent abilities**.

A model's size alone does not establish that it can perform a task reliably. The training data, objective, and evaluation all matter.

Applications also inherit weaknesses from the shared base. A foundation model provides a reusable starting point; evaluation establishes whether that starting point is suitable for a particular job.

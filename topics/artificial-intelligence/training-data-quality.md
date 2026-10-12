# Training data quality

A model learns statistical patterns from its training data, and the quality, diversity, and relevance of that data strongly influence what the model can do.

Even a sophisticated model architecture cannot reliably compensate for systematically missing, incorrect, or unrepresentative training data.

## 1. Why training data matters

During training, a model learns relationships between inputs and desired outputs, or statistical relationships within the data itself.

Consider an image classification model trained to recognize animals.

```text
           Training Dataset
          +-----------------+
          | 1,000 dogs      |
          | 1,000 cats      |
          | 1,000 birds     |
          +--------+--------+
                   |
                   v
             Model Training
                   |
                   v
          +-----------------+
          |  Trained Model  |
          +--------+--------+
                   |
          +--------+--------+
          |                 |
          v                 v
      Dog image         Rose image
          |                 |
          v                 v
        "Dog"            "Bird"
       Correct          Incorrect
```

The classifier has learned to distinguish dogs, cats, and birds. However, it has never learned a separate category for plants.

If its output is restricted to those three animal classes, it must assign every image to one of them, even if the image contains something completely different.

This illustrates two important concepts:

**Coverage**: Does the training dataset contain examples of the concepts, situations, and behaviors the model is expected to handle?

**Generalization**: Can the model apply learned patterns to new examples it has never encountered?

Generalization is powerful, but it has limits. A model can recognize a new dog despite never seeing that particular dog during training. Recognizing an entirely new category is a different challenge.

There is an important nuance for LLMs: a language does not necessarily have to appear explicitly in one particular training subset for a multilingual model to exhibit some ability in it, because of transfer learning and related representations. However, a language that is entirely absent or severely underrepresented will generally be much harder to handle reliably.

## 2. Why collecting massive amounts of internet data is insufficient

Internet data is attractive because it is abundant, diverse, and relatively inexpensive to collect.

Unfortunately, it also contains:

- Incorrect or outdated information.
- Duplicated and automatically generated content.
- Spam, advertisements, and low-information pages.
- Harmful or biased material.
- Contradictory information.
- Content unrelated to the model's intended capabilities.

Training indiscriminately on everything creates risks.

For example, suppose a model is expected to produce reliable technical explanations. A dataset containing millions of confidently written but incorrect technical articles can teach the model undesirable patterns.

The model does not inherently know which statements are true. During language-model pretraining, it primarily learns to predict tokens based on their context.

Statistical likelihood is not the same as factual correctness.

## 3. Heuristic filtering: a practical but imperfect solution

A heuristic is a simple rule used to make decisions without performing a complete, expensive assessment.

For example, a web-data collection pipeline might use popularity as a proxy for quality.

GPT-2's WebText collection used outbound Reddit links receiving at least three karma as a selection signal.

Conceptually:

```text
    Internet Pages
          |
          v
+--------------------+
| Popularity Filter  |
|                    |
| Score >= threshold |
+---------+----------+
          |
  +-------+-------+
  |               |
  v               v
Accepted        Rejected
  |
  v
Training Dataset
```

This approach has advantages: it is inexpensive, scalable, and may remove some uninteresting or low-effort content.

But it has a fundamental limitation:

Popularity is a proxy for quality, not a guarantee of quality.

A popular article can contain misinformation, while an excellent technical paper might receive almost no attention.

Furthermore, popularity-based selection can introduce selection bias. The collected dataset will disproportionately reflect the interests, languages, preferences, and demographics of the communities generating those signals.

This matters because models can inherit systematic biases from their datasets.

## 4. Dataset curation: choosing the right data

Dataset curation is the process of selecting, cleaning, organizing, balancing, and validating training data to make it suitable for a particular objective.

It is more sophisticated than simply removing obviously bad examples.

A typical data preparation pipeline looks like this:

```text
                 Raw Data
                    |
                    v
             Data Collection
                    |
                    v
            Quality Filtering
                    |
                    v
              Deduplication
                    |
                    v
          Coverage and Diversity
                    |
                    v
           Task-Specific Selection
                    |
                    v
                Validation
                    |
                    v
             Curated Dataset
                    |
                    v
              Model Training
                    |
                    v
               Evaluation
                    |
                    +----> Identify failures
                                   |
                                   v
                            Improve dataset
```

Each stage serves a different purpose.

| Stage             | Purpose                                                         |
| ----------------- | --------------------------------------------------------------- |
| Collection        | Gather relevant examples                                        |
| Quality filtering | Remove undesirable or unreliable data                           |
| Deduplication     | Reduce redundant examples                                       |
| Coverage          | Ensure important scenarios are represented                      |
| Diversity         | Avoid excessive concentration in particular sources or patterns |
| Task alignment    | Prioritize examples relevant to expected behavior               |
| Validation        | Check correctness, consistency, and suitability                 |
| Evaluation        | Identify weaknesses requiring dataset improvements              |

This is a central principle of data-centric AI: improving the data can be as important as, or more effective than, modifying the model architecture.

## 5. Why alignment with the intended application matters

Imagine developing an LLM to assist with debugging Linux kernel problems.

There are two possible training datasets.

```text
+-------------------------------------------+   +-------------------------------------------+
| DATASET A                                 |   | DATASET B                                 |
|                                           |   |                                           |
| 100 million                               |   | 2 million                                 |
| Random web documents                      |   | Carefully selected technical examples     |
|                                           |   |                                           |
| Large but potentially noisy               |   | Smaller but relevant, diverse,            |
| and weakly relevant                       |   | and validated                             |
+-------------------------------------------+   +-------------------------------------------+
```

Dataset B might include kernel documentation, debugging case studies, annotated traces, networking incidents, and high-quality explanations.

For a targeted fine-tuning task, Dataset B could outperform Dataset A because its examples align more closely with the behavior being optimized.

However, this is not a universal rule: large-scale pretraining benefits greatly from broad data, and a smaller curated dataset may lack necessary diversity. The right balance depends on the training objective.

## 6. The deeper problem: training distribution versus production distribution

This leads to a fundamental machine learning concept: distribution shift.

Training data is sampled from some probability distribution, conventionally written as:

```text
P_train(X, Y)
```

But production requests may come from a different distribution:

```text
P_production(X, Y)
```

When these distributions differ meaningfully, performance can deteriorate.

For example:

```text
TRAINING ENVIRONMENT
--------------------
Clean English text
Well-formed questions
Common technical topics
        |
        v
      Model
        |
        v
PRODUCTION ENVIRONMENT
----------------------
Multilingual requests
Incomplete error messages
Unusual technical failures
Ambiguous instructions
```

A model performing exceptionally on the training distribution might perform poorly in production because important cases were never adequately represented.

This is a well-established source of machine-learning failures.

Dataset curation therefore should not simply optimize overall dataset cleanliness. It must also preserve the variety and difficulty of the actual inputs the model will encounter.

## 7. Key engineering lessons

1. Data quality is multidimensional. Correctness, coverage, diversity, relevance, and representativeness all matter.
2. Heuristics scale, but introduce biases. Every filtering rule implicitly defines what kinds of information are overrepresented or excluded.
3. More data does not automatically mean better performance. Additional examples are useful only to the extent that they improve learning.
4. The production workload should influence data selection. Training and evaluation datasets should reflect the intended application.
5. Dataset curation is iterative. Production failures and evaluation results should inform subsequent improvements to the dataset.

The central engineering insight is that training data is not merely an input to model development; it is part of the system's design.

Choosing what a model learns from is, in significant part, choosing what kinds of problems it will be equipped to solve.

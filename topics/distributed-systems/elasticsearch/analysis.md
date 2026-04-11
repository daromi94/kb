# Analysis

Analysis converts raw document text into the terms the inverted index
stores. `Brutus`, `BRUTUS`, and `Brutus,` can map to the same term or
to three different ones — that decision is made here, and information
thrown away by tokenization cannot be recovered downstream.

## Pipeline stages

**Character filtering.** Strips HTML, normalizes Unicode, expands
ligatures. Output is still a character stream.

**Tokenization.** Splits the character stream into tokens. Each token
carries surface text, character offsets, and a position.

**Token filtering.** Transforms the token stream — lowercasing,
stemming, stopword removal, synonyms, n-grams. Filters can drop,
replace, or emit multiple tokens at the same position.

## Tokenization strategies

- **Whitespace.** Splits on spaces. `Brutus, Caesar` → `Brutus,`,
  `Caesar` — punctuation sticks to words.
- **Standard.** Unicode word boundaries (UAX #29). `Brutus, Caesar` →
  `Brutus`, `Caesar`. Default for Western text.
- **N-gram.** Overlapping character windows. `search` (length 2–6) →
  `se`, `sea`, `sear`, `searc`, `search`. Enables prefix matching via
  plain term lookup.
- **CJK.** Chinese, Japanese, and Korean lack spaces between words.
  Dictionary or statistical segmentation finds word boundaries where
  whitespace tokenizers would emit one giant token per sentence.
- **Keyword.** Whole input as one token. For SKUs, email addresses —
  exact-match fields.

The tokenizer is a structural commitment. Once `search-engine` is
split into `search` and `engine`, no downstream filter can recover the
hyphen.

## Token filters

- **Lowercasing.** Case-insensitive search.
- **Stopword removal.** Drops *the*, *of*, *and*. Shrinks postings but
  breaks phrase queries.
- **Stemming.** Suffix-stripping reduces inflections to a root:
  *running*, *runs* → *run*. Aggressive: *university* and *universe*
  both stem to *univers*.
- **Lemmatization.** Looks up the true base form in a dictionary:
  *better* → *good*, *ran* → *run*. Catches irregulars that stemming
  cannot, at the cost of being slower and language-specific.
- **ASCII folding.** `café` → `cafe`. Harmful when diacritics are
  semantic (`año` vs `ano`).
- **Synonym expansion.** Injects tokens at the same position (`tv`
  also emits `television`).
- **Shingling.** Emits multi-word tokens for phrase-heavy workloads.

## Index/query symmetry

The same pipeline runs at index time and query time, and they must
agree. If the indexer lowercases but the query parser doesn't,
searching for `Brutus` misses every document containing `brutus`.

## Related

- [Inverted index](inverted-index.md) - What analysis feeds into

---

Return to [Elasticsearch](_index.md)

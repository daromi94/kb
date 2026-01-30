#!/usr/bin/env python3
"""
Build an inverted index of all notes in topics/
Output: index/kb.json

Index structure:
{
  "notes": {
    "async-io/asynchronous-io.md": {
      "title": "Asynchronous I/O",
      "terms": ["async", "blocking", "callback", ...]
    }
  },
  "terms": {
    "async": ["async-io/asynchronous-io.md", ...],
    "thread": ["async-io/multithreading.md", ...]
  }
}
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
INDEX_FILE = REPO_ROOT / "index" / "kb.json"

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "is", "it", "be", "as", "by", "this", "that", "with", "from", "are", "was",
    "were", "been", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "can", "not", "you", "your",
    "they", "their", "we", "our", "its", "also", "more", "when", "how", "what",
    "which", "who", "other", "into", "such", "some", "only", "than", "then",
    "these", "those", "each", "all", "any", "most", "both", "few", "use",
    "used", "using", "between", "about", "after", "before", "being", "here",
    "there", "where", "just", "like", "make", "made", "many", "much", "need",
    "new", "now", "one", "see", "way", "well", "back", "even", "get", "got",
    "over", "still", "take", "want", "work", "first", "last", "long", "great",
    "little", "own", "same", "another", "come", "every", "good", "know", "look",
    "think", "day", "give", "two", "part", "because", "through", "very", "say",
    "set", "while", "under"
}


def extract_terms(text: str) -> list[str]:
    """Extract unique terms from text, excluding stopwords."""
    words = re.findall(r'[a-z]{3,}', text.lower())
    return sorted(set(w for w in words if w not in STOPWORDS))


def extract_title(content: str, filename: str) -> str:
    """Extract title from markdown (first H1) or use filename."""
    match = re.search(r'^# (.+)$', content, re.MULTILINE)
    if match:
        return match.group(1)
    return Path(filename).stem.replace('-', ' ').title()


def main():
    topics_dir = REPO_ROOT / "topics"

    # Ensure index directory exists
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not topics_dir.exists():
        with open(INDEX_FILE, 'w') as f:
            json.dump({"notes": {}, "terms": {}}, f)
        print("No topics directory found. Created empty index.")
        return

    print(f"Building inverted index from {topics_dir}...")

    notes = {}
    terms = defaultdict(list)

    # Process all markdown files except _index.md
    for md_file in topics_dir.rglob("*.md"):
        if md_file.name == "_index.md":
            continue

        rel_path = str(md_file.relative_to(topics_dir))
        content = md_file.read_text()

        title = extract_title(content, md_file.name)
        file_terms = extract_terms(content)

        notes[rel_path] = {
            "title": title,
            "terms": file_terms
        }

        for term in file_terms:
            terms[term].append(rel_path)

    # Sort term lists for consistency
    for term in terms:
        terms[term] = sorted(set(terms[term]))

    index = {
        "notes": notes,
        "terms": dict(terms)
    }

    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)

    print(f"Index built: {INDEX_FILE}")
    print(f"  Notes indexed: {len(notes)}")
    print(f"  Unique terms: {len(terms)}")


if __name__ == "__main__":
    main()

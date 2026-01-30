#!/usr/bin/env python3
"""
Match input content against the inverted index to find similar notes.

Usage:
    echo "content" | ./match-notes.py [topic]
    ./match-notes.py [topic] < file.md

Optional topic argument filters results to that topic only.
Output: JSON array of matches with scores, sorted by relevance.
"""

import json
import math
import re
import sys
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


def extract_terms(text: str) -> set[str]:
    """Extract unique terms from text, excluding stopwords."""
    words = re.findall(r'[a-z]{3,}', text.lower())
    return set(w for w in words if w not in STOPWORDS)


def main():
    topic_filter = sys.argv[1] if len(sys.argv) > 1 else None

    # Check if index exists
    if not Path(INDEX_FILE).exists():
        print("Index not found. Run build-index.py first.", file=sys.stderr)
        sys.exit(1)

    # Read content from stdin
    content = sys.stdin.read()
    input_terms = extract_terms(content)

    if not input_terms:
        print("[]")
        return

    # Load index
    with open(INDEX_FILE) as f:
        index = json.load(f)

    matches = []

    for path, note in index["notes"].items():
        # Apply topic filter
        if topic_filter and not path.startswith(f"{topic_filter}/"):
            continue

        note_terms = set(note["terms"])
        matching_terms = input_terms & note_terms

        if not matching_terms:
            continue

        # Cosine similarity: dot product / (|A| * |B|)
        # Here we use: matches^2 / (note_terms * input_terms) for simplicity
        match_count = len(matching_terms)
        score = (match_count ** 2) / (len(note_terms) * len(input_terms))

        matches.append({
            "path": path,
            "title": note["title"],
            "matches": match_count,
            "matching_terms": sorted(matching_terms),
            "score": round(score, 4)
        })

    # Sort by score descending, take top 10
    matches.sort(key=lambda x: -x["score"])
    matches = matches[:10]

    print(json.dumps(matches, indent=2))


if __name__ == "__main__":
    main()

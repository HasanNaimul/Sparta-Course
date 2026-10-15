"""BM25 keyword search.

Built by hand so we can see every part of the score.
No network calls and no model calls.

It indexes the same chunks as the vector index so the two
retrievers can later be fused chunk for chunk.
"""

import math
import re
from collections import Counter

K1 = 1.5  # How quickly repeating a word stops adding much more score.
B = 0.75  # How strongly long chunks are normalised.


def tokenize(text: str) -> list[str]:
    """Lowercase text and split it into words and numbers.

    "LP-3307" -> ["lp", "3307"]
    "What is LP-3307 about?" -> ["what", "is", "lp", "3307", "about"]
    """
    # walkthrough
        # what, is and about appear in many chunks... so they add very little
        # 3307 appers in one chunk, the Tokyo one, so it will carry the highest rarity
        # most of that chunks winning score comes from the rare tokens it sgares with the question
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Index:
    def __init__(self, chunks: list[dict]):
        if not chunks:
            raise ValueError("Cannot build a keyword index from zero chunks")

        self.chunks = chunks

        # Count all terms once when the index is built.
        self.term_counts = [Counter(tokenize(chunk["text"])) for chunk in chunks]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.avg_length = sum(self.lengths) / len(chunks)

        # Number of chunks containing each term.
        self.doc_freq = Counter()
        for counts in self.term_counts:
            self.doc_freq.update(counts.keys())

    def idf(self, term: str) -> float:
        """Return how rare a term is across the chunks."""
        n = len(self.chunks)
        df = self.doc_freq.get(term, 0)

        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def score(self, query_terms: list[str], position: int) -> float:
        """Return the BM25 score for one chunk."""
        counts = self.term_counts[position]
        length_norm = 1 - B + B * self.lengths[position] / self.avg_length
        total = 0.0

        for term in set(query_terms):
            tf = counts.get(term, 0)

            if tf:
                total += self.idf(term) * (
                    tf * (K1 + 1) /
                    (tf + K1 * length_norm)
                )

        return total

    def search(self, query: str, k: int = 10) -> list[dict]:
        """Return the k highest-scoring chunks, best first."""
        if k <= 0:
            raise ValueError("k must be greater than zero")

        terms = tokenize(query)

        if not terms:
            return []

        scored = []

        for position, chunk in enumerate(self.chunks):
            bm25 = self.score(terms, position)

            if bm25 > 0:
                scored.append({
                    "chunk": chunk,
                    "bm25": bm25,
                })

        scored.sort(key=lambda hit: hit["bm25"], reverse=True)

        return scored[:k]

# why we need both types of search 
# keyword (BM25)
    # Good at... Exact codes, names, and numbers (LP-3307)
    # Bad at... codes that carry no meeaning
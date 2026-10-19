"""Simple BM25 keyword retrieval for Credit Intelligence."""

import math
import re
from collections import Counter

K1 = 1.5
B = 0.75


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25Index:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.term_counts = [Counter(tokenize(chunk["text"])) for chunk in chunks]
        self.lengths = [sum(counts.values()) for counts in self.term_counts]
        self.avg_length = sum(self.lengths) / len(self.lengths)

        self.doc_freq = Counter()

        for counts in self.term_counts:
            for term in counts:
                self.doc_freq[term] += 1

    def idf(self, term: str) -> float:
        n = len(self.chunks)
        df = self.doc_freq.get(term, 0)
        return math.log(1 + (n - df + 0.5) / (df + 0.5))

    def score(self, query: str, index: int) -> float:
        query_terms = tokenize(query)
        counts = self.term_counts[index]
        length = self.lengths[index]
        length_norm = 1 - B + B * length / self.avg_length

        score = 0.0

        for term in query_terms:
            tf = counts.get(term, 0)

            if tf:
                score += self.idf(term) * (tf * (K1 + 1) / (tf + K1 * length_norm))

        return score

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        results = []

        for i, chunk in enumerate(self.chunks):
            score = self.score(query, i)

            if score > 0:
                results.append({
                    "chunk": chunk,
                    "bm25": score,
                })

        return sorted(results, key=lambda hit: hit["bm25"], reverse=True)[:top_k]
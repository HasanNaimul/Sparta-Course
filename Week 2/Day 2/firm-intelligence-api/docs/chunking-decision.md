# Chunking decision

**Date:** 13 October 2026  
**Decided by:** Hasan Naimul  
**Corpus:** `documents.py` + `corpus.py` (16 documents)  
**Eval set:** `eval_set.py` (29 answerable, 3 unanswerable)  
**Embedding model:** Voyage embedding model used by the project

## Decision

I choose `sections_contextual` with a relevance floor of `0.53`.

## Evidence

| Strategy | R@1 | R@3 | MRR | Context words@3 | Answer acc. @ 0.53 | Refusal acc. @ 0.53 | Avg input tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| `whole_document` | 0.690 | 1.000 | 0.845 | 862 | 0.59 | 1.00 | 668 |
| `fixed_100_overlap_25` | 0.517 | 0.931 | 0.668 | 277 | 0.55 | 1.00 | 337 |
| `sections_contextual` | 0.862 | 1.000 | 0.931 | 197 | 0.97 | 1.00 | 350 |

## Why this one

`sections_contextual` gave the strongest overall balance of retrieval quality, answer quality and model cost. It achieved the highest MRR at `0.931`, perfect Recall@3, and used only 197 context words at k=3, compared with 862 for `whole_document`.

At the chosen relevance floor of `0.53`, `sections_contextual` achieved `0.97` answer accuracy and `1.00` refusal accuracy with an average of 350 input tokens. At the same floor, `fixed_100_overlap_25` fell to `0.55` answer accuracy and `whole_document` fell to `0.59`, so `sections_contextual` was clearly more robust.

The contextual prefix also made a clear difference. `sections_plain` and `sections_contextual` use the same section boundaries, but adding the document title and section heading improved heading-dependent Recall@3 from `0.50` to `1.00` and title-dependent Recall@3 from `0.75` to `1.00`.

The relevance floor was tested around the decision boundary. `0.53` kept answer accuracy at `0.97` with one false refusal and an average of 350 input tokens. Raising the floor to `0.54` reduced average input tokens to 329, but answer accuracy dropped to `0.90` and false refusals increased to three. This made `0.53` the best tested balance between answer quality and token use.

## Known weaknesses

At `0.53`, `sections_contextual` still falsely refuses `q24`.

The evaluation also showed that answerable and unanswerable similarity scores overlap, so no single relevance floor can perfectly separate them. Some exact-id and negation questions are difficult for semantic embeddings alone and may benefit from hybrid retrieval that combines vector search with lexical or keyword search.

The current evaluation set is small, especially the three unanswerable questions, so the chosen floor should be treated as the best tested value for this corpus rather than a universal optimum.

## Revisit when

Revisit this decision if the corpus grows, documents become longer, document structure changes, the embedding model changes, or the evaluation set is expanded.

Also revisit it after hybrid retrieval is introduced, because keyword or lexical retrieval may improve exact-id and negation queries and could change the best relevance floor or chunking strategy.

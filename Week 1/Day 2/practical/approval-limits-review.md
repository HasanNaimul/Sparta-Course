# Review: Add approval limits

## Gates and scope

| Check | Result |
| --- | --- |
| Ruff | FAIL — 2 errors |
| mypy | FAIL — 4 errors |
| pytest | PASS — 3 tests |

Review continued beyond the failed gates at the requester's instruction, in checklist order: commit messages, changed files, tests, then implementation.

The original exercise contains three changed files, including a Ruff downgrade. The learner's setup stopped early; the subsequently created local commit contains only `src/limits.py` and `tests/test_limits.py`. Finding 7 applies only to the original exercise.

## Findings — blocking

### 1. Shared mutable default

**Where:** `src/limits.py:16–18`  
**What:** `seen=[]` creates one default list shared across calls that omit `seen`; each call appends another amount.  
**Class:** MACHINE — Ruff B006  
**Ask:** Could you use `seen=None` and initialize a fresh list inside the function? What purpose does `seen` serve, given that this implementation appends to it but never reads it?

### 2. Unnecessary Boolean conditional

**Where:** `src/limits.py:19–21`  
**What:** The conditional returns Boolean literals when the comparison already produces a Boolean result.  
**Class:** MACHINE — Ruff SIM103  
**Ask:** Could you return the comparison directly, using the corrected inclusive boundary from Finding 4?

### 3. Missing annotations and return path

**Where:** `src/limits.py:16,24–29`; `tests/test_limits.py:9,13`  
**What:** `requires_approval` lacks annotations, causing three mypy diagnostics including its test calls; `approval_threshold` is already annotated but returns `None` for unknown bands despite promising `Decimal`.  
**Class:** MACHINE — mypy no-untyped-def, no-untyped-call, return  
**Ask:** Could you annotate `requires_approval`, define and explicitly handle unsupported bands in `approval_threshold`, and test that behaviour? Keep its existing signature consistent with the chosen behaviour and rerun mypy.

### 4. Exact approval boundary is wrong

**Where:** `src/limits.py:19`  
**What:** The ticket rule recorded in the docstring says “500.00 and above”, but `>` makes exactly `500.00` return `False`.  
**Class:** HUMAN  
**Ask:** Could you use the inclusive `>=` comparison and verify amounts immediately below, at, and above the limit? This defect alone blocks approval.

### 5. Large-amount test does not check the required answer

**Where:** `tests/test_limits.py:9`  
**What:** The test compares two calls with the same input instead of an expected result, so it passes even when approval always returns `False`.  
**Class:** HUMAN  
**Ask:** Could you assert `requires_approval(Decimal("600.00")) is True` and verify that an always-false implementation makes the test fail?

### 6. Missing boundary test

**Where:** `tests/test_limits.py`  
**What:** No test checks exactly `500.00`, so the existing suite misses the incorrect exclusive comparison.  
**Class:** HUMAN  
**Ask:** Could you add `test_boundary_amount_requires_approval`, asserting `requires_approval(Decimal("500.00")) is True`, alongside below- and above-limit cases?

### 7. Unrelated dependency downgrade — original exercise only

**Where:** `requirements.txt:3`  
**What:** The original “Add approval limits” commit downgrades Ruff from `0.16.6` to `0.14.0` without explaining its relevance to approval limits.  
**Class:** HUMAN  
**Ask:** Could you revert the downgrade in the original PR or move it to a separately justified PR? No change is needed for this finding in the learner's local commit, where the downgrade is absent.

No optional findings. The configured gate failures remain blocking under the checklist.

## Execution evidence

Boundary results reproduced on the learner's machine:

| Amount | Expected approval | Actual approval |
| --- | --- | --- |
| `499.99` | `False` | `False` |
| `500.00` | `True` | **`False` — FAIL** |
| `500.01` | `True` | `True` |

Temporarily replacing `requires_approval` in memory with an always-false function still produced **3 passed** on the learner's machine. Source files were not edited. This proves that the suite misses that incorrect implementation; it does not mean the test can never fail under any circumstances.

Additional execution in the separate exercise copy confirmed that unknown and empty bands return `None`, and repeated approval calls retain amounts in the shared default list.

## Verdict

**REQUEST CHANGES.** Exactly `500.00` incorrectly skips approval, the tests miss both that boundary bug and an always-false implementation, and Ruff and mypy fail. Fix these issues and rerun the gates and behavioural checks before approval. The original exercise PR must also resolve the unrelated dependency downgrade; that finding does not apply to the learner's two-file commit.

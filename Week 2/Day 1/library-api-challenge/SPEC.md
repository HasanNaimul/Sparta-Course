# Personal Library API — Specification

## Why

This is the Sparta Global `library-api-challenge` deliverable. It exists to
practice writing a precise, unambiguous specification — following the
"Writing a Spec" process — and then following the required development
workflow (spec → acceptance tests → implementation → documentation) for a
small REST API that manages a personal collection of books.

## What

A FastAPI service exposing **exactly five endpoints** over a single
in-memory `books` collection, seeded with synthetic data only (no real
book data, no external data source):

1. `GET /books` — list books (paginated)
2. `GET /books/{id}` — get one book
3. `POST /books` — create a book
4. `PATCH /books/{id}` — update a book's `status`
5. `DELETE /books/{id}` — delete a book

All error responses use a single consistent shape: `{"error": "<message>"}`.
FastAPI's default `422` validation response is not used for any case covered
by this spec — every case listed below maps to an explicit status code and
body.

## Context

### Files

- `SPEC.md` — this file.
- `handout-writing-a-spec.pdf` — reference material only; not part of the
  runtime project.
- Nothing else exists yet. The following will be created by the Tasks below:
  - `requirements.txt` — dependency list.
  - `pytest.ini` — minimal pytest configuration (`[pytest]` with
    `pythonpath = .`) that puts the repository root on Python's import
    path. Without it, the literal command `pytest -q` (run as the
    installed console script, not via `python -m pytest`) fails to
    resolve `from src.main import ...` in a clean clone, even though the
    same test suite passes under `python -m pytest -q`. This file makes
    the spec's required `pytest -q` command behave identically in a
    fresh clone and in an existing checkout.
  - `tests/test_api.py` — acceptance tests, written before implementation.
  - `src/__init__.py` — empty, makes `src` an importable package.
  - `src/main.py` — the entire application (FastAPI app instance, in-memory
    store, all five routes, internal test-support reset mechanism).
  - `README.md` — clean-clone setup instructions.

### Pattern

- Single-file FastAPI application — no routers, blueprints, or service
  layers. The project is small enough that splitting adds no value.
- Data lives in a plain in-memory Python list for the lifetime of the
  process. No database, no file persistence.
- Every request or response body that exists is JSON. A successful
  `DELETE /books/{id}` returns `HTTP 204` with no response body.
- Required development workflow, in order: (1) write acceptance tests from
  this spec, (2) implement against those tests, (3) document clean-clone
  setup. Implementation must never come before its acceptance tests.

### Settled decisions

**Runtime**

1. Language/framework: Python + FastAPI.
2. FastAPI app instance is named `app`, defined in `src/main.py`.
3. Run command: `uvicorn src.main:app --reload --port 8000`.
4. Server listens on port `8000`.
5. Storage: in-memory Python list. Data resets to the seed set on every
   restart. No persistence layer of any kind.

**Book schema** — exactly these four fields, no others:

6. `id`: integer. Required on stored/returned records. Server-generated
   only — auto-incrementing, starts at `1`, must be `> 0`. Clients must
   never supply or modify it.
7. `title`: string. Required. After trimming leading/trailing whitespace,
   length must be between `1` and `200` characters inclusive. The stored
   value is the trimmed string.
8. `author`: string. Required. After trimming leading/trailing whitespace,
   length must be between `1` and `100` characters inclusive. The stored
   value is the trimmed string.
9. `status`: string. Required. Must be exactly one of `"unread"`,
   `"reading"`, `"finished"` — comparison is case-sensitive (e.g.
   `"Unread"` is invalid).

**Seed data**

10. Exactly these 5 synthetic books are seeded at startup, in this order:

    | id | title | author | status |
    |----|-------|--------|--------|
    | 1 | "The Silent Planet" | "Mira Cole" | "unread" |
    | 2 | "Beyond the River" | "Sam Rowan" | "reading" |
    | 3 | "Glass Harbour" | "Elena Vale" | "finished" |
    | 4 | "North of Tomorrow" | "Daniel Frost" | "unread" |
    | 5 | "The Last Lantern" | "Nora Blake" | "reading" |

11. The first book created via `POST /books` after startup receives id
    `6`, and the counter continues from there. The internal test-support
    reset mechanism (see Task 1) restores exactly this same 5-book
    dataset (rule 10) and resets the next-id counter to `6` — never a
    different or partial dataset.

**`GET /books`**

12. Returns a plain JSON array (no wrapper object) — not `{"items": [...]}`
    or similar.
13. Accepts optional query params `page` (integer, default `1`, minimum
    `1`, no fixed maximum) and `limit` (integer, default `10`, minimum `1`,
    maximum `50`).
14. Any of the following makes the request invalid, returning
    `HTTP 400 {"error": "Invalid pagination"}`: `page` not an integer,
    `page < 1`, `limit` not an integer, `limit < 1`, `limit > 50`.
    Examples: `?page=0`, `?page=-1`, `?page=abc`, `?limit=0`, `?limit=-5`,
    `?limit=51`, `?limit=abc`.
15. Results are ordered by `id` ascending, then sliced by `page`/`limit`.
16. A page beyond the available results is valid, not an error: returns
    `HTTP 200 []`. Example: `?page=4&limit=2` against 5 seeded books → `[]`.

**`GET /books/{id}`**

17. If `{id}` is not a valid positive integer (non-numeric, or `< 1`, e.g.
    `/books/abc`, `/books/0`, `/books/-1`): `HTTP 400
    {"error": "Invalid book id"}`.
18. If `{id}` is a valid positive integer but no book with that id exists:
    `HTTP 404 {"error": "Book not found"}`.
19. If a matching book exists: `HTTP 200` with the full book object
    (`id`, `title`, `author`, `status`).

**`POST /books`**

20. Accepted body fields: exactly `title`, `author`, `status`. Any other
    field present — including `id` — is rejected.
21. If the request body is not syntactically valid JSON, or is valid JSON
    but not a JSON object (e.g. an array, string, number, `null`):
    `HTTP 400 {"error": "Invalid request body"}`. This check happens
    before any field-level check, since field checks require a parsed
    object.
22. If the body is a valid JSON object, check for unexpected fields next.
    If one or more exist: `HTTP 400
    {"error": "Unexpected field: <name>"}`, where `<name>` is the first
    unexpected field name in alphabetical order (e.g. body with both
    `price` and `id` unexpected → reports `"id"` first).
23. If there are no unexpected fields, validate known fields in this
    fixed order, reporting only the first failure: `title`, then
    `author`, then `status`.
24. `title` check, in this order:
    a. If the `title` key is missing → `HTTP 400
       {"error": "Title must be between 1 and 200 characters"}`.
    b. Else if `title` is present but is not a JSON string (number,
       `null`, boolean, array, object) → `HTTP 400
       {"error": "Invalid request body"}`.
    c. Else (`title` is a string): if, after trimming leading/trailing
       whitespace, its length is `0` or greater than `200` → `HTTP 400
       {"error": "Title must be between 1 and 200 characters"}`.
25. `author` check: same structure as `title` (rule 24a–c), with message
    `"Author must be between 1 and 100 characters"` in place of the
    title message, and the `1`–`100` boundary in place of `1`–`200`.
26. `status` check: if the key is missing, or the value (of any type) is
    not exactly one of `"unread"`, `"reading"`, `"finished"` →
    `HTTP 400 {"error": "Status must be one of: unread, reading,
    finished"}`. Unlike title/author, there is no separate "wrong type"
    message for `status` — any non-matching value, including wrong type
    or missing key, collapses into this one message, since the check is
    membership-based rather than a length range.
27. On success: assign the next auto-increment `id`, store the trimmed
    `title`/`author` and the given `status`, and return `HTTP 201` with
    the complete created book, including the generated `id`.

**`PATCH /books/{id}`**

28. `{id}` is validated **before** the body is read or parsed at all,
    using the same rules as `GET /books/{id}` (rules 17–18): invalid
    format/`< 1` → `HTTP 400 {"error": "Invalid book id"}`; valid but
    nonexistent → `HTTP 404 {"error": "Book not found"}`.
29. Only after `{id}` resolves to an existing book is the body validated.
    If the body is not syntactically valid JSON, or is valid JSON but not
    a JSON object: `HTTP 400 {"error": "Invalid request body"}`.
30. Accepted body field: exactly `status`. No other fields — including
    `title`, `author`, or `id` — are accepted.
31. Body validation priority, reporting only the first failure:
    a. If any field other than `status` is present (e.g. `title`,
       `author`, `id`, or anything else) → `HTTP 400
       {"error": "Only status may be updated"}`.
    b. Else if `status` is missing (including an empty `{}` body) →
       `HTTP 400 {"error": "Status is required"}`.
    c. Else if `status` is present but not exactly one of `"unread"`,
       `"reading"`, `"finished"` (case-sensitive, any type) →
       `HTTP 400 {"error": "Status must be one of: unread, reading,
       finished"}`.
    d. Else: update the book's `status` in place and return `HTTP 200`
       with the full updated book (`id`, `title`, `author`, `status`).

**`DELETE /books/{id}`**

32. `{id}` is validated using the same rules as rule 17–18: invalid
    format/`< 1` → `HTTP 400 {"error": "Invalid book id"}`; valid but
    nonexistent → `HTTP 404 {"error": "Book not found"}`.
33. On success: remove the book from the store and return `HTTP 204` with
    an empty response body.
34. Requesting the same `id` again afterward (via `GET` or `DELETE`)
    returns `HTTP 404 {"error": "Book not found"}`.

**General**

35. Every error response in this spec uses exactly the shape
    `{"error": "<message>"}` — a single string field, no nested `details`,
    no arrays, no additional keys.
36. None of the cases enumerated above may fall through to FastAPI's
    default `422 Unprocessable Entity` response — all are overridden to
    return the `400`/`404` codes and bodies specified.

## Constraints

- Python + FastAPI only, run via `uvicorn` on port `8000` (decisions 1–4).
- No database, no ORM, no external services — in-memory storage only
  (decision 5).
- No new fields beyond `id`, `title`, `author`, `status` (decisions 6–9).
- No new endpoints beyond the five listed under **What**.
- Acceptance tests must be written from this spec *before* any
  implementation code exists, and must not be edited afterward merely to
  make a failing implementation pass.

### Out of scope

- Authentication or authorization of any kind.
- Filtering or searching books by `title`, `author`, or `status`.
- Sorting other than the fixed ascending-by-`id` order (rule 15).
- Updating `title` or `author` — `PATCH` only ever changes `status`
  (rules 30–31).
- Data persistence across process restarts (no file writes, no DB).
- Rate limiting, CORS configuration, API versioning.
- Any book fields beyond the four listed (no genre, ISBN, publish year,
  description, timestamps, etc.).
- Bulk create/update/delete endpoints.
- Multi-user concepts or ownership — a single global collection shared by
  all callers.
- A reset/clear-state HTTP endpoint. State reset is internal test support
  only (a plain Python function called directly by the test fixture) and
  must never be exposed as an HTTP route.
- `Content-Type` header enforcement (e.g. rejecting non-`application/json`
  requests) — not specified, not tested.
- FastAPI's auto-generated `/docs` and `/openapi.json` are not disabled,
  but their content/behavior is not covered by this spec.

## Tasks

The project is built in three stages — acceptance tests, then
implementation, then documentation — and implementation is split into
small, independently reviewable subtasks per endpoint.

### Task 1 — Write acceptance tests from the specification

**Build:**
- `tests/test_api.py` with acceptance tests for all five endpoints, using
  FastAPI's `TestClient` against the `app` object imported from
  `src.main` — which does not exist yet.
- `requirements.txt` listing `fastapi`, `uvicorn`, `pytest`, `httpx` — all
  four added now, since Task 2's manual verification needs `uvicorn` to
  run the server, not just import it.
- `pytest.ini` containing exactly:

  ```ini
  [pytest]
  pythonpath = .
  ```

  This is required for acceptance-test execution: it puts the repository
  root on Python's import path so the literal `pytest -q` command
  resolves `tests/test_api.py`'s `from src.main import ...` from any
  clean clone, not just from an environment where `python -m pytest` was
  used or the root happened to already be on `sys.path`.
- An autouse, function-scoped pytest fixture that resets the
  application's in-memory state to the clean seed before **every** test:
  exactly 5 books, ids `1`–`5`, next id `6`. The fixture calls an internal
  reset mechanism in `src.main` (a plain Python function/state reset, not
  an HTTP route) — no reset endpoint is added to the API.

**Touches:** `tests/test_api.py`, `requirements.txt`, `pytest.ini`

**Verify:**
- At least one test function exists for each endpoint: `GET /books`,
  `GET /books/{id}`, `POST /books`, `PATCH /books/{id}`,
  `DELETE /books/{id}`.
- Each test function names the rule number(s) it covers (e.g. a docstring
  or comment `# rule 14`).
- Boundary cases are tested with exact values, e.g.: `limit=50` (valid)
  vs `limit=51` (invalid, rule 14); `page=1` (valid) vs `page=0` (invalid,
  rule 14); `title` of exactly 200 chars (valid, rule 7) vs 201 chars
  (invalid, rule 24); `title` of exactly 1 char (valid) vs `""` (invalid);
  `author` of 100 vs 101 chars; `id=1` (valid) vs `id=0` (invalid, rule 17).
- At least one test asserts `HTTP 400` for each of: invalid pagination
  (rule 14), invalid book-id format (rule 17), unexpected POST field
  (rule 22), invalid `title`/`author`/`status` (rules 24–26), PATCH extra
  field / missing `status` / invalid `status` (rule 31), malformed JSON
  body (rules 21, 29).
- At least one test asserts `HTTP 404` for a well-formed but nonexistent
  id on `GET`, `PATCH`, and `DELETE` (rules 18, 28, 32).
- A test that creates a book (`POST /books`, expecting id `6`) followed
  by a test that asserts `GET /books` returns exactly 5 books passes
  regardless of which order the two tests run in — proving the reset
  fixture, not test order, controls state.
- `pip install -r requirements.txt` succeeds.
- `pytest -q` run at this stage **fails** (import error or test failures)
  — expected, since `src/main.py` doesn't exist yet.

### Task 2a — Project scaffold and clean seed/reset state

**Build:** `src/main.py` and `src/__init__.py` with the FastAPI `app`
instance, the in-memory `books` list seeded with exactly 5 books (ids
`1`–`5`, satisfying rules 7–9), a next-id counter starting at `6`, and the
internal reset function the Task 1 fixture calls (not an HTTP route). No
endpoints implemented yet.

**Touches:** `src/__init__.py`, `src/main.py`

**Verify:**
- `python -c "from src.main import app"` succeeds with no error.
- Calling the internal reset function (directly, in a Python shell or via
  the test fixture) leaves the store with exactly 5 books, ids `1`–`5`,
  and the next generated id equal to `6`.

### Task 2b — Implement `GET /books`

**Build:** the `GET /books` route implementing rules 12–16.

**Touches:** `src/main.py`

**Verify:** the acceptance tests covering rules 12–16 pass (e.g.
`pytest -q tests/test_api.py -k "list_books or pagination"` reports
`0 failed`).

### Task 2c — Implement `GET /books/{id}`

**Build:** the `GET /books/{id}` route implementing rules 17–19.

**Touches:** `src/main.py`

**Verify:** the acceptance tests covering rules 17–19 pass (e.g.
`pytest -q tests/test_api.py -k "get_book"` reports `0 failed`).

### Task 2d — Implement `POST /books`

**Build:** the `POST /books` route implementing rules 20–27.

**Touches:** `src/main.py`

**Verify:** the acceptance tests covering rules 20–27 pass (e.g.
`pytest -q tests/test_api.py -k "create_book"` reports `0 failed`).

### Task 2e — Implement `PATCH /books/{id}`

**Build:** the `PATCH /books/{id}` route implementing rules 28–31.

**Touches:** `src/main.py`

**Verify:** the acceptance tests covering rules 28–31 pass (e.g.
`pytest -q tests/test_api.py -k "patch_book or update_book"` reports
`0 failed`).

### Task 2f — Implement `DELETE /books/{id}`

**Build:** the `DELETE /books/{id}` route implementing rules 32–34.

**Touches:** `src/main.py`

**Verify:** the acceptance tests covering rules 32–34 pass (e.g.
`pytest -q tests/test_api.py -k "delete_book"` reports `0 failed`).

**After Task 2f:** run the complete suite — `pytest -q` from the repo
root exits `0`, output ends `N passed in X.XXs` with `0 failed`,
`0 errors`. `tests/test_api.py` is unchanged from Task 1 across all of
Tasks 2a–2f (confirmed via `git diff`).

### Task 3 — Document clean-clone setup

**Build:** `README.md` with exact, copy-pasteable steps from a fresh
clone to a running server and a passing test suite.

**Touches:** `README.md` only — `requirements.txt` is touched here only
if a genuine dependency gap is discovered while validating clean-clone
setup (not expected, since all four packages were added in Task 1).

**Verify:**
- Starting from `git clone <repo> && cd library-api-challenge` and
  following only the steps written in `README.md`, in order, produces: a
  working virtual environment, a successful
  `pip install -r requirements.txt`, a server serving on port 8000 via
  `uvicorn src.main:app --reload --port 8000`, and a passing `pytest -q`.
- `README.md` states the literal commands for: creating/activating a
  virtualenv, `pip install -r requirements.txt`, the run command, and
  `pytest -q` — no step assumes information the reader doesn't already
  have from the README itself.

## Done

This spec is fully implemented when:

1. All five endpoints (`GET /books`, `GET /books/{id}`, `POST /books`,
   `PATCH /books/{id}`, `DELETE /books/{id}`) are implemented in
   `src/main.py`.
2. Every numbered rule describing API behavior (rules 6–36) has at least
   one corresponding acceptance test in `tests/test_api.py`.
3. `pytest -q` run from the repo root passes with zero failures and zero
   errors, and passes regardless of test execution order (each test
   starts from the reset clean state: 5 books, ids 1–5, next id 6).
4. `HTTP 400` and `HTTP 404` are returned exactly where, and with exactly
   the bodies, specified in rules 14, 17–18, 21–26, 28–32, 35–36 —
   confirmed by the passing test suite.
5. `README.md` lets a person starting from a clean clone, with no prior
   context, install dependencies, run the API, and run the test suite
   using only the instructions in `README.md`.
6. No functionality listed under **Out of scope** has been added — in
   particular, no reset endpoint exists in `src/main.py`.

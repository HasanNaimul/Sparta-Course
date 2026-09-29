# Personal Library API

A small FastAPI service that manages a personal collection of books,
seeded with synthetic data only. It exposes exactly five endpoints:

- `GET /books` — list books (paginated)
- `GET /books/{id}` — get one book
- `POST /books` — create a book
- `PATCH /books/{id}` — update a book's status
- `DELETE /books/{id}` — delete a book

The full behavior is defined in `SPEC.md`.

## Requirements

- Python (3.9+)
- Git

## Setup (PowerShell on Windows)

From a fresh clone:

```powershell
git clone <repo>
cd library-api-challenge

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
```

## Running the API

```powershell
uvicorn src.main:app --reload --port 8000
```

The API runs at:

```
http://127.0.0.1:8000
```

Interactive FastAPI docs are available at:

```
http://127.0.0.1:8000/docs
```

## Running the tests

```powershell
pytest -q
```

Expected result: all 91 acceptance tests pass, with zero failures and
zero errors.

## Endpoints

- `GET /books`
- `GET /books/{id}`
- `POST /books`
- `PATCH /books/{id}`
- `DELETE /books/{id}`

## Data

Books are stored in an in-memory Python list only — no database, no
file persistence. All data is synthetic (no real book data). The
collection resets to the seed set of 5 books every time the server
process restarts.

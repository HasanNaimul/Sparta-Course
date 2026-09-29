# Runbook

This runbook explains how to set up and verify the Day 5 ship-prep project from a clean machine.

## Requirements

- Git
- Python 3.12
- uv

## Clone the repository

```bash
git clone https://github.com/HasanNaimul/day5-ship-prep.git
cd day5-ship-prep

```

## Create the virtual environment

```bash
uv venv .venv --python 3.12
```

## Install dependencies

### Windows

```bash
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

### macOS/Linux

```bash
uv pip install --python .venv/bin/python -r requirements.txt
```

## Run the checks

### Windows

```bash
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m mypy src tests
.venv/Scripts/python.exe -m pytest -q
bash smoke.sh
```

### macOS/Linux

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src tests
.venv/bin/python -m pytest -q
bash smoke.sh
```

## Expected output

Ruff:

```text
All checks passed!
```

Mypy:

```text
Success: no issues found in 2 source files
```

Pytest:

```text
8 passed
```

Smoke test:

```text
smoke OK: reconcile match and mismatch correct, worst_line correct, empty handled
```

The smoke test should exit with status code `0`.
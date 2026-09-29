#!/usr/bin/env bash
# CA-1 checkpoint 3: a real textual conflict, for you to resolve.
# Two people changed the SAME line for two different good reasons.
# Run from this directory:  ./build.sh   then work inside ./repo
set -eu
rm -rf repo; mkdir repo; cd repo
git init -q
git config user.email "you@institute.local"; git config user.name "You"
mkdir -p src tests
cat > pyproject.toml <<'EOF'
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
EOF
cat > src/ledger.py <<'EOF'
"""Synthetic transaction ledger. SYNTHETIC PLACEHOLDER DATA ONLY."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Entry:
    reference: str
    amount: Decimal


def describe(entry: Entry) -> str:
    return f"{entry.reference}: {entry.amount}"


def total(entries: Sequence[Entry]) -> Decimal:
    return sum((entry.amount for entry in entries), start=Decimal("0.00"))
EOF
cat > tests/test_ledger.py <<'EOF'
from decimal import Decimal

from ledger import Entry, describe

E = Entry(reference="SYN-001", amount=Decimal("10.10"))


def test_describe_shows_reference_and_amount() -> None:
    out = describe(E)
    assert "SYN-001" in out
    assert "10.10" in out
EOF
git add -A; git commit -q -m "Ledger with describe helper"

git switch -q -c pad-the-reference
python3 - <<'PY'
import pathlib
p = pathlib.Path("src/ledger.py")
p.write_text(p.read_text().replace(
  'return f"{entry.reference}: {entry.amount}"',
  'return f"{entry.reference:<12} {entry.amount}"'))
PY
git commit -q -am "Pad the reference so columns line up in the report"

git switch -q main
python3 - <<'PY'
import pathlib
p = pathlib.Path("src/ledger.py")
p.write_text(p.read_text().replace(
  'return f"{entry.reference}: {entry.amount}"',
  'return f"{entry.reference}: GBP {entry.amount}"'))
PY
git commit -q -am "Show the currency in describe output"

echo "### Two commits, one line, two good reasons."
git log --oneline --graph --all
echo
echo "### Now merge. This one really does conflict."
set +e
git merge --no-edit pad-the-reference
echo
echo "### Conflicted files:"
git status --short
echo
echo "Resolve src/ledger.py so BOTH intentions survive, then:"
echo "  git add src/ledger.py && git commit"
echo "  python3 -m pytest -q      <- the test must still pass"

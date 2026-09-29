#!/usr/bin/env bash
# CA-2a: find the regression yourself. Seven commits. One of them broke the suite.
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
cat > src/limits.py <<'EOF'
"""Approval limits. SYNTHETIC PLACEHOLDER DATA ONLY.

Rule: amounts of 500.00 and above require a second approver.
"""

from decimal import Decimal

APPROVAL_LIMIT = Decimal("500.00")


def requires_approval(amount: Decimal) -> bool:
    return amount >= APPROVAL_LIMIT
EOF
cat > tests/test_limits.py <<'EOF'
from decimal import Decimal

from limits import requires_approval


def test_boundary_requires_approval() -> None:
    assert requires_approval(Decimal("500.00")) is True
    assert requires_approval(Decimal("499.99")) is False
EOF
git add -A; git commit -q -m "Add approval limit with boundary test"

cat >> src/limits.py <<'EOF'


def band_for(amount: Decimal) -> str:
    return "elevated" if amount >= Decimal("2000.00") else "standard"
EOF
git commit -q -am "Add band_for helper"

python3 - <<'PY'
import pathlib
p = pathlib.Path("src/limits.py")
p.write_text(p.read_text().replace(
  "    return amount >= APPROVAL_LIMIT",
  "    return amount > APPROVAL_LIMIT"))
PY
git commit -q -am "Tidy the comparison in requires_approval"

cat >> src/limits.py <<'EOF'


def limit_for_band(band: str) -> Decimal:
    return Decimal("2000.00") if band == "elevated" else APPROVAL_LIMIT
EOF
git commit -q -am "Add limit_for_band"

python3 - <<'PY'
import pathlib
p = pathlib.Path("src/limits.py")
p.write_text(p.read_text().replace('"""Approval limits. SYNTHETIC PLACEHOLDER DATA ONLY.',
  '"""Approval limits for synthetic ledger entries. SYNTHETIC PLACEHOLDER DATA ONLY.'))
PY
git commit -q -am "Clarify module docstring"

cat >> tests/test_limits.py <<'EOF'


def test_band_for() -> None:
    from limits import band_for

    assert band_for(Decimal("2500.00")) == "elevated"
EOF
git commit -q -am "Add test for band_for"

cat >> src/limits.py <<'EOF'


def is_zero(amount: Decimal) -> bool:
    return amount == Decimal("0.00")
EOF
git commit -q -am "Add is_zero helper"

echo "### Seven commits. The suite is red today."
git log --oneline
echo
set +e
python3 -m pytest -q 2>&1 | tail -8
echo
echo "Find the commit that did it. Do not read the diffs."
echo "  git bisect start"
echo "  git bisect bad"
echo "  git bisect good <the first commit>"
echo "  git bisect run python3 -m pytest -q"

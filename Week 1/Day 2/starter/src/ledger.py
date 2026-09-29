"""Synthetic transaction ledger. carried forward from Day 1.

SYNTHETIC PLACEHOLDER DATA ONLY. Every reference and amount used with this
module is invented for teaching purposes. No client data appears here.

Three decisions in this file are the point of the lesson:

1. A frozen dataclass instead of a bare dict.
   A dict of str to object tells mypy almost nothing, so mypy cannot help you.
   A dataclass gives every field a type, which turns the type checker from a
   formality into a reviewer that can actually catch a wrong field name.

2. Decimal instead of float for money.
   Binary floats cannot represent 10.10 exactly, so a float sum of
   10.10 + 20.20 + 5.05 returns 35.349999999999994, not 35.35. Decimal
   represents the value you typed and sums it exactly.

3. `entries: list[Entry] | None = None` instead of `entries: list = []`.
   A default argument is evaluated once, when the function is defined, so a
   mutable default is shared by every call. The None sentinel gives each call
   a fresh list.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Entry:
    """One ledger line. Frozen so an entry cannot be mutated after creation."""

    reference: str
    amount: Decimal


def add_entry(
    reference: str,
    amount: Decimal,
    entries: Sequence[Entry] | None = None,
) -> list[Entry]:
    """Return a NEW ledger with one entry appended.

    Returning a new list rather than mutating the argument means the caller
    can never be surprised by an alias they did not ask for.
    """
    ledger = list(entries) if entries is not None else []
    ledger.append(Entry(reference=reference, amount=amount))
    return ledger


def total(entries: Sequence[Entry]) -> Decimal:
    """Sum the amounts on a ledger exactly."""
    return sum((entry.amount for entry in entries), start=Decimal("0.00"))


def find_reference(entries: Sequence[Entry], reference: str) -> Entry | None:
    """Return the matching entry, or None when the reference is not present.

    The return type says None is possible, so every caller is forced by mypy
    to handle the miss. The broken version claimed it always returned a str.
    """
    for entry in entries:
        if entry.reference == reference:
            return entry
    return None

def largest(entries: list[Entry]) -> Entry | None:
    """Return the entry with the largest amount, or None if the ledger is empty."""
    if not entries:
        return None

    return max(entries, key=lambda entry: entry.amount)
"""Synthetic transaction ledger. LEARNER STARTER."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Entry:
    reference: str
    amount: float


def add_entry(
    entry: Entry,
    entries: list[Entry] | None = None,
) -> list[Entry]:
    """Add an entry and return a new ledger."""

    if entries is None:
        entries = []

    return entries + [entry]


def total(entries: list[Entry]) -> Decimal:
    """Return the exact total of all entries."""

    running = Decimal("0.00")

    for entry in entries:
        running += Decimal(str(entry.amount))

    return running


def find_reference(
    entries: list[Entry],
    reference: str,
) -> Entry | None:
    """Return the matching entry, or None if it is not found."""

    for entry in entries:
        if entry.reference == reference:
            return entry

    return None
"""Wire the ledger together and print the day's headline numbers.

carried forward from Day 1. Synthetic placeholder data only.
"""

from decimal import Decimal

from ledger import Entry, add_entry, find_reference, total

SYNTHETIC_AMOUNTS: list[tuple[str, str]] = [
    ("SYN-001", "10.10"),
    ("SYN-002", "20.20"),
    ("SYN-003", "5.05"),
]


def main() -> None:
    ledger: list[Entry] = []
    for reference, amount in SYNTHETIC_AMOUNTS:
        ledger = add_entry(reference, Decimal(amount), ledger)

    print(f"entries on the ledger: {len(ledger)}")
    print(f"total: {total(ledger)}")
    print(f"total == Decimal('35.35'): {total(ledger) == Decimal('35.35')}")

    hit = find_reference(ledger, "SYN-002")
    print(f"lookup SYN-002: {hit}")

    miss = find_reference(ledger, "SYN-999")
    print(f"lookup SYN-999: {miss}")


if __name__ == "__main__":
    main()

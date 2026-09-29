"""Tests for the ledger. carried forward from Day 1. Synthetic data only."""

from decimal import Decimal

import pytest

from ledger import Entry, add_entry, find_reference, total, largest


@pytest.fixture
def sample_ledger() -> list[Entry]:
    """Three synthetic entries whose amounts are chosen to break float maths."""
    return [
        Entry(reference="SYN-001", amount=Decimal("10.10")),
        Entry(reference="SYN-002", amount=Decimal("20.20")),
        Entry(reference="SYN-003", amount=Decimal("5.05")),
    ]


def test_total_is_exact(sample_ledger: list[Entry]) -> None:
    assert total(sample_ledger) == Decimal("35.35")


def test_total_of_an_empty_ledger_is_zero() -> None:
    assert total([]) == Decimal("0.00")


def test_add_entry_does_not_leak_between_calls() -> None:
    first = add_entry("SYN-001", Decimal("10.10"))
    second = add_entry("SYN-002", Decimal("20.20"))
    assert len(first) == 1
    assert len(second) == 1


def test_add_entry_returns_a_new_list(sample_ledger: list[Entry]) -> None:
    extended = add_entry("SYN-004", Decimal("1.00"), sample_ledger)
    assert len(sample_ledger) == 3
    assert len(extended) == 4


def test_find_reference_hit(sample_ledger: list[Entry]) -> None:
    hit = find_reference(sample_ledger, "SYN-002")
    assert hit is not None
    assert hit.amount == Decimal("20.20")


def test_find_reference_miss_returns_none(sample_ledger: list[Entry]) -> None:
    assert find_reference(sample_ledger, "SYN-999") is None


def test_largest_returns_entry_with_largest_amount(sample_ledger):
    assert largest(sample_ledger) == Entry(
    reference="SYN-002",
    amount=Decimal("20.20"),
)


def test_largest_returns_none_for_empty_ledger():
    assert largest([]) is None
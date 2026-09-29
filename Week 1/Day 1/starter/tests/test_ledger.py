"""Tests for the ledger. LEARNER STARTER. Synthetic data only."""

from decimal import Decimal

import pytest

from ledger import Entry, add_entry, find_reference, total


@pytest.fixture
def sample_ledger():
    return [
        Entry(reference="SYN-001", amount=10.10),
        Entry(reference="SYN-002", amount=20.20),
        Entry(reference="SYN-003", amount=5.05),
    ]


def test_total_is_exact(sample_ledger):
    assert total(sample_ledger) == Decimal("35.35")


def test_total_of_an_empty_ledger_is_zero():
    assert total([]) == Decimal("0.00")


def test_add_entry_does_not_leak_between_calls():
    entry1 = Entry(reference="SYN-004", amount=10.00)
    entry2 = Entry(reference="SYN-005", amount=20.00)

    ledger1 = add_entry(entry1)
    ledger2 = add_entry(entry2)

    assert len(ledger1) == 1
    assert len(ledger2) == 1


def test_add_entry_returns_a_new_list(sample_ledger):
    new_entry = Entry(reference="SYN-004", amount=10.00)

    new_ledger = add_entry(new_entry, sample_ledger)

    assert len(sample_ledger) == 3
    assert len(new_ledger) == 4


def test_find_reference_hit(sample_ledger):
    result = find_reference(sample_ledger, "SYN-002")

    assert result is not None
    assert result.reference == "SYN-002"


def test_find_reference_miss_returns_none(sample_ledger):
    result = find_reference(sample_ledger, "SYN-999")

    assert result is None
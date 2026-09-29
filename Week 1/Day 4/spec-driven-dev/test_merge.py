"""Tests for merge.py, one per verify line in Task 2 of
spec-merge-duplicate-tickets.md.
"""

import unittest
from datetime import datetime, timedelta

from tickets import Ticket
from merge import merge_duplicate_tickets


def make_ticket(**overrides) -> Ticket:
    """Build a Ticket with sensible defaults, overriding only what a test cares about."""
    defaults = dict(
        id="HD-1",
        customer="Priya Shah",
        subject="Invoice PDF won't download",
        priority="Normal",
        status="open",
        created_at=datetime(2026, 1, 1),
        last_customer_reply_at=datetime(2026, 1, 1),
        reply_deadline=datetime(2026, 1, 15),
        closed_by=None,
        first_response_at=None,
        escalated_to=None,
        merged_into=None,
    )
    defaults.update(overrides)
    return Ticket(**defaults)


class MergeDuplicateTicketsTests(unittest.TestCase):
    def setUp(self):
        # Fixed "now" so every test is deterministic, not dependent on the clock.
        self.now = datetime(2026, 2, 1, 12, 0, 0)
        # Three duplicates: HD-1 open/10d (oldest), HD-2 open/6d, HD-3 closed/2d.
        self.hd1 = make_ticket(id="HD-1", created_at=self.now - timedelta(days=10))
        self.hd2 = make_ticket(id="HD-2", created_at=self.now - timedelta(days=6))
        self.hd3 = make_ticket(
            id="HD-3", created_at=self.now - timedelta(days=2), status="closed"
        )

    def test_newer_duplicate_is_merged_into_older_survivor(self):
        merged = merge_duplicate_tickets([self.hd1, self.hd2, self.hd3])

        self.assertEqual(self.hd2.status, "closed")
        self.assertEqual(self.hd2.closed_by, "system")
        self.assertEqual(self.hd2.merged_into, "HD-1")
        self.assertIn(self.hd2, merged)

    def test_survivor_is_left_unchanged(self):
        merge_duplicate_tickets([self.hd1, self.hd2, self.hd3])

        self.assertEqual(self.hd1.status, "open")
        self.assertIsNone(self.hd1.closed_by)
        self.assertIsNone(self.hd1.merged_into)

    def test_already_closed_duplicate_is_left_unchanged_and_not_merged(self):
        merged = merge_duplicate_tickets([self.hd1, self.hd2, self.hd3])

        self.assertEqual(self.hd3.status, "closed")
        self.assertIsNone(self.hd3.closed_by)
        self.assertIsNone(self.hd3.merged_into)
        self.assertNotIn(self.hd3, merged)

    def test_same_subject_but_different_customer_is_not_merged(self):
        other = make_ticket(id="HD-4", customer="Someone Else")

        merged = merge_duplicate_tickets([self.hd1, other])

        self.assertEqual(other.status, "open")
        self.assertIsNone(other.merged_into)
        self.assertEqual(merged, [])

    def test_same_customer_but_different_subject_is_not_merged(self):
        other = make_ticket(id="HD-5", subject="A totally different problem")

        merged = merge_duplicate_tickets([self.hd1, other])

        self.assertEqual(other.status, "open")
        self.assertIsNone(other.merged_into)
        self.assertEqual(merged, [])

    def test_no_merges_when_survivor_itself_is_already_closed(self):
        closed_hd1 = make_ticket(
            id="HD-1", created_at=self.now - timedelta(days=10), status="closed"
        )

        merged = merge_duplicate_tickets([closed_hd1, self.hd2, self.hd3])

        self.assertEqual(merged, [])
        self.assertEqual(self.hd2.status, "open")
        self.assertIsNone(self.hd2.merged_into)


if __name__ == "__main__":
    unittest.main()

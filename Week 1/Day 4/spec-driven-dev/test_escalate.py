"""Tests for escalate.py, one per verify line in Task 2 of
spec-escalate-overdue-first-response.md.
"""

import unittest
from datetime import datetime, timedelta

from tickets import Ticket
from escalate import escalate_overdue_tickets


def make_ticket(**overrides) -> Ticket:
    """Build a Ticket with sensible defaults, overriding only what a test cares about."""
    defaults = dict(
        id="HD-TEST",
        customer="Test Customer",
        subject="Test subject",
        priority="Normal",
        status="open",
        created_at=datetime(2026, 1, 1),
        last_customer_reply_at=datetime(2026, 1, 1),
        reply_deadline=datetime(2026, 1, 15),
        closed_by=None,
        first_response_at=None,
        escalated_to=None,
    )
    defaults.update(overrides)
    return Ticket(**defaults)


class EscalateOverdueTicketsTests(unittest.TestCase):
    def setUp(self):
        # Fixed "now" so every test is deterministic, not dependent on the clock.
        self.now = datetime(2026, 2, 1, 12, 0, 0)

    def test_normal_ticket_over_5_days_with_no_response_is_escalated(self):
        ticket = make_ticket(created_at=self.now - timedelta(days=5, hours=1))

        escalated = escalate_overdue_tickets([ticket], now=self.now)

        self.assertEqual(ticket.priority, "Urgent")
        self.assertEqual(ticket.escalated_to, "Senior Customer Service Manager")
        self.assertIn(ticket, escalated)

    def test_normal_ticket_at_exactly_5_days_is_unchanged(self):
        ticket = make_ticket(created_at=self.now - timedelta(days=5))

        escalated = escalate_overdue_tickets([ticket], now=self.now)

        self.assertEqual(ticket.priority, "Normal")
        self.assertIsNone(ticket.escalated_to)
        self.assertEqual(escalated, [])

    def test_already_urgent_ticket_still_gets_escalated_to_set(self):
        ticket = make_ticket(priority="Urgent", created_at=self.now - timedelta(days=10))

        escalated = escalate_overdue_tickets([ticket], now=self.now)

        self.assertEqual(ticket.priority, "Urgent")
        self.assertEqual(ticket.escalated_to, "Senior Customer Service Manager")
        self.assertIn(ticket, escalated)

    def test_closed_ticket_is_skipped_without_error(self):
        ticket = make_ticket(status="closed", created_at=self.now - timedelta(days=30))

        escalated = escalate_overdue_tickets([ticket], now=self.now)

        self.assertEqual(ticket.priority, "Normal")
        self.assertIsNone(ticket.escalated_to)
        self.assertNotIn(ticket, escalated)
        self.assertEqual(escalated, [])

    def test_ticket_with_first_response_is_unchanged(self):
        ticket = make_ticket(
            created_at=self.now - timedelta(days=10),
            first_response_at=self.now - timedelta(days=1),
        )

        escalated = escalate_overdue_tickets([ticket], now=self.now)

        self.assertEqual(ticket.priority, "Normal")
        self.assertIsNone(ticket.escalated_to)
        self.assertEqual(escalated, [])


if __name__ == "__main__":
    unittest.main()

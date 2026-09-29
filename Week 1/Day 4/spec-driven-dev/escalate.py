from datetime import datetime, timedelta
from typing import List, Optional

from tickets import Ticket

FIRST_RESPONSE_TARGET = timedelta(days=5)
ESCALATION_OWNER = "Senior Customer Service Manager"


def escalate_overdue_tickets(tickets: List[Ticket], now: Optional[datetime] = None) -> List[Ticket]:
    """Escalate open tickets that have had no first response for more than 5 days.

    Closed tickets and tickets that already got a first response are skipped.
    Returns the list of tickets that were escalated.
    """
    if now is None:
        now = datetime.now()

    escalated = []
    for ticket in tickets:
        if ticket.status == "closed":
            continue
        if ticket.first_response_at is not None:
            continue
        if now - ticket.created_at > FIRST_RESPONSE_TARGET:
            ticket.escalated_to = ESCALATION_OWNER
            if ticket.priority != "Urgent":
                ticket.priority = "Urgent"
            escalated.append(ticket)

    return escalated

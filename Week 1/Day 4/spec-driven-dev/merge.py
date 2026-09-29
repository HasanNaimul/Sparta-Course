from typing import Dict, List, Tuple

from tickets import Ticket

MERGED_BY = "system"


def _duplicate_key(ticket: Ticket) -> Tuple[str, str]:
    return (ticket.customer.strip().lower(), ticket.subject.strip().lower())


def merge_duplicate_tickets(tickets: List[Ticket]) -> List[Ticket]:
    """Merge newer duplicate tickets into the oldest matching ticket.

    Two tickets are duplicates when their customer and subject match
    (case-insensitive, whitespace trimmed). Within a group of duplicates,
    the ticket with the earliest created_at (ties broken by smaller id) is
    the survivor and is never changed. Every other ticket in the group is
    closed and linked to the survivor via merged_into, unless it is already
    closed. If the survivor itself is already closed, the whole group is
    skipped.

    Returns the list of tickets that were merged.
    """
    groups: Dict[Tuple[str, str], List[Ticket]] = {}
    for ticket in tickets:
        groups.setdefault(_duplicate_key(ticket), []).append(ticket)

    merged = []
    for group in groups.values():
        if len(group) < 2:
            continue

        group.sort(key=lambda t: (t.created_at, t.id))
        survivor, *duplicates = group

        if survivor.status == "closed":
            continue

        for duplicate in duplicates:
            if duplicate.status == "closed":
                continue
            duplicate.status = "closed"
            duplicate.closed_by = MERGED_BY
            duplicate.merged_into = survivor.id
            merged.append(duplicate)

    return merged

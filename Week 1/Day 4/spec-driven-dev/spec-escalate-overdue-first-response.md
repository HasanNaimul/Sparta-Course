# Spec: Escalate Tickets That Miss Their First Response Target

## Why

Tickets that sit untouched by an agent get forgotten, and the customer is left
waiting with no idea anyone is looking at their problem. Flagging these tickets
as Urgent and naming a senior manager responsible makes sure a human notices
before the customer chases it or churns.

## What

- A ticket **misses its first response target** when more than 5 days have
  passed since it was created (`now - created_at > 5 days`) and no one has
  sent a first reply yet.
  - Example: a ticket created exactly 5 days ago (5 days, 0 hours) has **not**
    missed the target yet. A ticket created 5 days and 1 hour ago **has**.
- "No one has sent a first reply yet" means the ticket's `first_response_at`
  field is `None`. If it holds a timestamp, the target was already met and the
  ticket is never eligible, no matter how old it is.
- When a ticket misses the target:
  - Set `escalated_to = "Senior Customer Service Manager"`.
  - If `priority` is not already `"Urgent"`, set it to `"Urgent"`.
  - If `priority` is already `"Urgent"`, leave `priority` alone — only
    `escalated_to` is set.
- Tickets with `status == "closed"` are skipped entirely: not checked, not
  escalated, not treated as an error.
- Nothing else about the ticket changes.

## Context

- **Files:** `tickets.py` (the `Ticket` data class — currently has no field
  for "when did an agent first reply" or "who this was escalated to"; both
  need to be added). No other project code exists yet — this is a fresh
  addition, not a change to existing escalate/close logic.
- **Pattern:** none established yet in this project. Use the same shape as
  the spec for this: a function that takes a list of `Ticket`s and an
  optional `now: datetime` (defaulting to `datetime.now()` so tests can pass
  a fixed clock), mutates matching tickets in place, and returns the list of
  tickets it escalated.
- **Settled:**
  - No new libraries.
  - Ticket state stays on the `Ticket` record — no separate escalation log
    or table.
  - "Urgent" is stored in the existing `priority` field, not `status`.

## Constraints

- Out of scope: emailing or notifying the customer or the manager, any UI,
  changing `reply_deadline`, changing `status` (open/closed), any ticket-close
  behaviour, logging, and anything touching billing.
- Do not re-escalate logic for closed tickets under any condition.
- Do not invent a value for `first_response_at` — it is only ever set by
  code outside this spec's scope; here it is read, never written.

## Tasks

1. **Add the two missing fields to `Ticket`.**
   Touches: `tickets.py`
   Add `first_response_at: Optional[datetime] = None` and
   `escalated_to: Optional[str] = None` to the `Ticket` data class.
   Verify: `load_sample_tickets()` still runs with no errors, and every
   ticket it returns has `first_response_at is None` and
   `escalated_to is None`.

2. **Build the escalation function.**
   Touches: `escalate.py` (new)
   Add `escalate_overdue_tickets(tickets, now=None)` implementing the rules
   in **What**.
   Verify, using a fixed `now`:
   - A Normal-priority, open ticket created 5 days + 1 hour before `now`,
     with `first_response_at=None`, ends up with `priority="Urgent"` and
     `escalated_to="Senior Customer Service Manager"`.
   - A Normal-priority, open ticket created exactly 5 days before `now`
     (not more) is unchanged.
   - An Urgent, open ticket created 10 days before `now`, with
     `first_response_at=None`, keeps `priority="Urgent"` but gets
     `escalated_to="Senior Customer Service Manager"`.
   - A closed ticket created 30 days before `now`, with
     `first_response_at=None`, is returned unchanged and does not appear in
     the function's returned list.
   - An open ticket created 10 days before `now` but with
     `first_response_at` set to 1 day before `now` is unchanged.

3. **Add tests for each rule above.**
   Touches: `test_escalate.py` (new)
   One test per verify line in Task 2, each using the real values given
   there (not placeholder data).

## Done

Run `python -m unittest discover` — all tests pass. Then run
`escalate_overdue_tickets` against `load_sample_tickets()` and confirm by eye
that only tickets older than 5 days with no `first_response_at` were
escalated, closed tickets were left alone, and no ticket's `reply_deadline`
or `status` changed.

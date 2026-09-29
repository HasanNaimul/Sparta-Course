# Spec: Merge Duplicate Tickets

## Why

Customers sometimes raise the same problem twice, splitting the conversation
across two tickets and doubling the work for support. Merging the newer
duplicate into the older ticket keeps one place to track the issue instead of
two.

## What

- Two tickets are **duplicates** when both of these match, compared with
  whitespace trimmed and case ignored:
  - `customer` (e.g. `"Priya Shah"` and `"priya shah"` count as the same).
  - `subject` (this project has no separate description field — `subject`
    *is* the description of the problem, e.g. `"Invoice PDF won't
    download"`).
- Tickets that are **not** duplicates of each other (different customer, or
  different subject, or both) are never touched.
- Among a group of duplicate tickets, the one with the earliest `created_at`
  is the **survivor**. If two duplicates have the exact same `created_at`,
  the one with the lexicographically smaller `id` is the survivor.
- For every other (newer) ticket in the group:
  - If it is already `status == "closed"`, leave it exactly as it is — it is
    already completed, so it is not merged and not touched.
  - Otherwise, merge it into the survivor:
    - Set `status = "closed"`.
    - Set `closed_by = "system"`.
    - Set `merged_into = <survivor's id>`.
- If the survivor itself is already `status == "closed"`, **skip the whole
  group** — nothing in that group is merged, and nothing is touched. You do
  not merge new complaints into a ticket that is already completed.
- The survivor's own fields are never changed, whether or not anything gets
  merged into it.

### Example

Given these three tickets, all for `"Priya Shah"` / `"Invoice PDF won't
download"`, oldest first:

| id | created_at | status | before | after |
|----|------------|--------|--------|-------|
| HD-1 | 10 days ago | open | survivor | unchanged |
| HD-2 | 6 days ago | open | duplicate | `status="closed"`, `closed_by="system"`, `merged_into="HD-1"` |
| HD-3 | 2 days ago | closed | duplicate, already completed | unchanged |

## Context

- **Files:**
  - `tickets.py` — the `Ticket` data class. Needs one new field:
    `merged_into: Optional[str] = None`.
  - `escalate.py` — shows the pattern already used in this project: a
    function taking a `List[Ticket]`, mutating matching tickets in place,
    and returning the list of tickets it changed.
- **Pattern:** follow `escalate_overdue_tickets` in `escalate.py` — same
  shape (take the list, mutate in place, return what changed), same
  `closed_by = "system"` convention already used for automated actions on a
  ticket.
- **Settled:**
  - No new libraries.
  - Matching is on `customer` + `subject` only — no other field affects
    whether two tickets are duplicates.
  - Ticket state stays on the `Ticket` record — no separate merge log.

## Constraints

- Out of scope: emailing or notifying the customer, any UI, changing
  `priority`, `reply_deadline`, `first_response_at`, or `escalated_to` on
  any ticket, and combining the two tickets' content (subjects, replies,
  etc.) in any way — merging only means closing the duplicate and pointing
  `merged_into` at the survivor.
- Never delete a ticket from the list. A merged ticket still exists, just
  closed and linked.
- Never modify the survivor ticket's own fields.
- Never merge a ticket that is already closed, whether it's the survivor or
  the duplicate.

## Tasks

1. **Add the missing field to `Ticket`.**
   Touches: `tickets.py`
   Add `merged_into: Optional[str] = None` to the `Ticket` data class.
   Verify: `load_sample_tickets()` still runs with no errors, and every
   ticket it returns has `merged_into is None`.

2. **Build the merge function.**
   Touches: `merge.py` (new)
   Add `merge_duplicate_tickets(tickets: List[Ticket]) -> List[Ticket]`
   implementing the rules in **What**.
   Verify, using the three-ticket example above (HD-1 open/10 days,
   HD-2 open/6 days, HD-3 closed/2 days, all same customer+subject):
   - HD-2 ends up `status="closed"`, `closed_by="system"`,
     `merged_into="HD-1"`, and is in the function's returned list.
   - HD-1 (the survivor) is completely unchanged.
   - HD-3 is completely unchanged and not in the returned list (already
     closed, so never merged).
   - A ticket with the same `subject` but a different `customer` is left
     untouched and not merged with any of the above.
   - A ticket with the same `customer` but a different `subject` is left
     untouched and not merged with any of the above.
   - If the survivor itself is closed (e.g. HD-1 above were `status="closed"`
     instead of open), neither HD-2 nor HD-3 is merged, and none of the
     three tickets change.

3. **Add tests for each rule above.**
   Touches: `test_merge.py` (new)
   One test per verify line in Task 2, each using the real values given
   there (not placeholder data).

## Done

Run `python -m unittest discover` — all tests pass, including the existing
`test_escalate.py` tests (unaffected by this change). Then run
`merge_duplicate_tickets` against `load_sample_tickets()` and confirm by eye
that no sample ticket is merged (none of the 7 sample tickets share both
customer and subject), and nothing else about them changed.

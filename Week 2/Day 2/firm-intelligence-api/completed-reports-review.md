# Reports API Contractor Review

## Scenario

A contractor handed over `reports.py` for the Firm Intelligence API. The API runs and the endpoints return responses, but the code had not been reviewed for production safety.

The review goal was to answer: **is this safe to ship?**

The review followed the challenge constraints:

- Minimal diffs only; do not rewrite the file.
- Every finding must be demonstrable with a command.
- Treat the existing API contract as public: do not rename paths, fields, or status codes casually.
- Fix the highest-ranked issue first and prove the fix.

---

## Baseline check

`GET /reports` returns the two supplied reports:

```bash
curl http://127.0.0.1:8000/reports
```

Expected baseline response:

```json
[
  {
    "id": 1,
    "title": "UK Market Outlook",
    "firm_id": 1,
    "revisions": ["v1"]
  },
  {
    "id": 2,
    "title": "US Partner Compensation",
    "firm_id": 2,
    "revisions": ["v1"]
  }
]
```

---

# Ranked findings

## 1. Critical: the export endpoint blocks unrelated requests

### Code involved

```python
@router.get("/{report_id}/export")
async def export_report(report_id: int):
    report = get_report_or_404(report_id)
    time.sleep(3)
    return {"id": report["id"], "title": report["title"], "format": "pdf"}
```

### Why this is the highest priority

The route is declared with `async def`, so it runs on the event loop, but `time.sleep(3)` is synchronous blocking work. While that sleep is happening, unrelated async work handled by the same event loop can also be delayed.

This has the largest blast radius because a single slow export request can affect callers that are not using the export endpoint at all.

### Proof command

Use two Git Bash windows.

**Terminal 1:**

```bash
curl http://127.0.0.1:8000/reports/1/export
```

Immediately run this in **Terminal 2**:

```bash
curl -w "\nhealth_time=%{time_total}\n" http://127.0.0.1:8000/health
```

Before the fix, `/health` can wait behind the 3-second blocking call.

In a local reproduction of the contractor code, the health request took approximately:

```text
health_time=2.81s
```

### Fix applied

Minimal change only: change the export endpoint from `async def` to normal `def`.

```python
@router.get("/{report_id}/export")
def export_report(report_id: int):
    report = get_report_or_404(report_id)
    time.sleep(3)
    return {"id": report["id"], "title": report["title"], "format": "pdf"}
```

FastAPI runs a normal synchronous route in its thread pool, so the blocking sleep no longer blocks the main async event loop.

### Proof after the fix

Repeat the same two-terminal test:

**Terminal 1:**

```bash
curl http://127.0.0.1:8000/reports/1/export
```

**Terminal 2:**

```bash
curl -w "\nhealth_time=%{time_total}\n" http://127.0.0.1:8000/health
```

In the local verification after the one-line fix:

```text
health_time=0.0018s
```

The export still took about 3 seconds, but `/health` returned immediately.

**Result: fixed without changing the public route, response body, or status code.**

---

## 2. High: `POST /reports` is unsafe to retry

### Code involved

```python
@router.post("", status_code=201)
def create_report(new: NewReport):
    new_id = max(report["id"] for report in REPORTS) + 1
    ...
    REPORTS.append(report)
    return report
```

### Problem

If the client sends a POST and the server creates the report but the response is lost, the client may retry the exact same request. The second request creates another report with another ID.

The client cannot tell whether the first attempt succeeded.

### Proof command

Run the same request twice:

```bash
curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"title":"Retry Test","firm_id":1}'
```

Run it again:

```bash
curl -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"title":"Retry Test","firm_id":1}'
```

Observed behaviour in local verification:

```json
{"id":3,"title":"Retry Test","firm_id":1,"revisions":["v1"]}
```

then:

```json
{"id":4,"title":"Retry Test","firm_id":1,"revisions":["v1"]}
```

### Recommended remediation

Add an **idempotency key** supplied by the client, for example:

```text
Idempotency-Key: 8d41...
```

The server should remember the result for that key and return the original result if the same key is retried.

This was **not changed in this review** because it adds new request semantics and storage behaviour and should be agreed as part of the API contract.

---

## 3. High: `PUT /reports/{report_id}` is not idempotent

### Code involved

```python
@router.put("/{report_id}")
def update_report(report_id: int, new: NewReport):
    report = get_report_or_404(report_id)
    report["title"] = new.title
    report["firm_id"] = new.firm_id
    report["revisions"].append(f"v{len(report['revisions']) + 1}")
    return report
```

### Problem

HTTP PUT is expected to be idempotent: repeating the same request should leave the resource in the same state.

Here, every retry appends another revision even when the body is identical.

### Proof command

Run this twice:

```bash
curl -X PUT http://127.0.0.1:8000/reports/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Outlook","firm_id":1}'
```

First response can contain:

```json
"revisions": ["v1", "v2"]
```

The same request again can produce:

```json
"revisions": ["v1", "v2", "v3"]
```

### Recommended remediation

The revision system needs an explicit product/API decision. Options include:

- only add a revision when the resource actually changes;
- use a separate revision endpoint;
- use a request/idempotency identifier so a retry does not create another revision.

This was **not changed** because revision behaviour is visible API behaviour and changing it should be agreed with the client.

---

## 4. Medium: `GET /reports/{report_id}` changes server state

### Code involved

```python
@router.get("/{report_id}")
async def get_report(report_id: int):
    report = get_report_or_404(report_id)
    _view_counts[report_id] = _view_counts.get(report_id, 0) + 1
    return {**report, "views": _view_counts[report_id]}
```

### Problem

A GET request is normally expected to be safe/read-only, but this GET increments `_view_counts` every time it is called.

Retries, browser refreshes, monitoring, pre-fetching, or automated clients therefore change state.

### Proof command

Run:

```bash
curl http://127.0.0.1:8000/reports/1
```

Then run the same request again:

```bash
curl http://127.0.0.1:8000/reports/1
```

Observed behaviour:

First call:

```json
"views": 1
```

Second call:

```json
"views": 2
```

### Recommended remediation

Decide whether views are analytics or part of the report resource. Possible approaches include recording analytics separately or using a dedicated event/write endpoint.

This was **not changed** because removing or changing `views` would alter visible behaviour and needs an API/product decision.

---

## 5. Medium: reports can reference a firm that does not exist

### Code involved

```python
class NewReport(BaseModel):
    title: str = Field(min_length=1)
    firm_id: int
```

and:

```python
@router.post("", status_code=201)
def create_report(new: NewReport):
```

### Problem

The request validates that `firm_id` is an integer, but it does not verify that the referenced firm exists.

That allows orphaned report data.

This differs from the people router, where a new person's `firm_id` is checked before creation.

### Proof command

```bash
curl -i -X POST http://127.0.0.1:8000/reports \
  -H "Content-Type: application/json" \
  -d '{"title":"Orphan Report","firm_id":9999}'
```

Observed in local verification:

```text
HTTP 201 Created
```

with a report containing:

```json
{"firm_id":9999}
```

### Recommended remediation

Validate `new.firm_id` against the firms resource before creating or updating a report, using the same shared lookup logic already used elsewhere in the API.

This was not included in the top-priority fix because its blast radius is smaller than blocking the whole service.

---

# Findings deliberately not treated as major defects

## `DELETE` returns 404 on a second request

A repeated DELETE may return 404 after the resource has already been removed. That does not necessarily make the operation non-idempotent: after both attempts, the resource is still absent.

No change recommended from the evidence reviewed.

## `get_report` uses `async def` without awaiting anything

This is unnecessary and could be simplified, but by itself it is not the same severity as the blocking `time.sleep()` problem in the export route. It was not ranked as a standalone production defect in this review.

---

# Final ranking

| Rank | Finding | Severity | Main reason |
|---:|---|---|---|
| 1 | Blocking `time.sleep()` inside async export route | Critical | One request can delay unrelated requests across the service |
| 2 | POST is unsafe to retry | High | Lost responses/retries can create duplicate data |
| 3 | PUT creates another revision on identical retry | High | Violates expected PUT idempotency and corrupts revision history |
| 4 | GET increments view state | Medium | A safe/read operation has side effects |
| 5 | No validation that `firm_id` exists | Medium | Allows orphaned/inconsistent data |

---

# Code change made

Only the number-one issue was changed, following the challenge requirement for a minimal diff.

```diff
 @router.get("/{report_id}/export")
-async def export_report(report_id: int):
+def export_report(report_id: int):
     report = get_report_or_404(report_id)
     time.sleep(3)
     return {"id": report["id"], "title": report["title"], "format": "pdf"}
```

No path, response field, or status code was changed.

---

# 60-second engineering handover

> We reviewed the contractor's reports API and found five material issues. We ranked the blocking export endpoint first because it has the widest blast radius: it was declared async but calls `time.sleep(3)`, so a single export can delay unrelated requests on the event loop. We proved it by starting an export and then calling `/health`; before the fix, the health request waited about 2.8 seconds in our reproduction. We made the smallest possible fix by changing the export handler from `async def` to normal `def`, allowing FastAPI to run the blocking work in its thread pool. The same test then returned `/health` in about 0.002 seconds while the export was still running. We also found retry-unsafe POST creation, non-idempotent PUT revisions, a GET that mutates view state, and missing validation of report `firm_id`. We deliberately did not change those because they involve visible API or data semantics and need agreement before modifying the public contract.

---

# Commands to demonstrate every finding

```bash
# Baseline
curl http://127.0.0.1:8000/reports

# Finding 1: blocking export
# Terminal 1
curl http://127.0.0.1:8000/reports/1/export

# Terminal 2, immediately
curl -w "\nhealth_time=%{time_total}\n" http://127.0.0.1:8000/health

# Finding 2: duplicate POST on retry
curl -X POST http://127.0.0.1:8000/reports -H "Content-Type: application/json" -d '{"title":"Retry Test","firm_id":1}'
curl -X POST http://127.0.0.1:8000/reports -H "Content-Type: application/json" -d '{"title":"Retry Test","firm_id":1}'

# Finding 3: repeated PUT changes revisions
curl -X PUT http://127.0.0.1:8000/reports/1 -H "Content-Type: application/json" -d '{"title":"Updated Outlook","firm_id":1}'
curl -X PUT http://127.0.0.1:8000/reports/1 -H "Content-Type: application/json" -d '{"title":"Updated Outlook","firm_id":1}'

# Finding 4: GET changes view state
curl http://127.0.0.1:8000/reports/1
curl http://127.0.0.1:8000/reports/1

# Finding 5: nonexistent firm accepted
curl -i -X POST http://127.0.0.1:8000/reports -H "Content-Type: application/json" -d '{"title":"Orphan Report","firm_id":9999}'
```

---

## Conclusion

**Not safe to ship unchanged.**

The most urgent service-wide blocking problem has a small, non-breaking fix. The remaining issues should be addressed before production, but several require agreement on retry behaviour, analytics semantics, revision semantics, and cross-resource validation rather than an unreviewed rewrite.

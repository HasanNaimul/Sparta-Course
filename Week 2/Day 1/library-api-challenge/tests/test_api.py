"""Acceptance tests for the Personal Library API, written from SPEC.md.

These tests are written BEFORE any implementation exists (Task 1 of SPEC.md).
They are expected to fail with an ImportError until Task 2a creates
`src/main.py` with an `app` FastAPI instance and an internal, non-HTTP
reset function named `reset_state`.

Every test function includes a comment naming the SPEC.md rule number(s)
it verifies.
"""

import pytest
from fastapi.testclient import TestClient

# `src.main` does not exist yet (Task 1 precedes Task 2a). This import is
# expected to fail until Task 2a provides `app` and `reset_state`.
from src.main import app, reset_state

client = TestClient(app)

# Exact seed dataset per rule 10, in seeded order.
SEEDED_BOOKS = [
    {"id": 1, "title": "The Silent Planet", "author": "Mira Cole", "status": "unread"},
    {"id": 2, "title": "Beyond the River", "author": "Sam Rowan", "status": "reading"},
    {"id": 3, "title": "Glass Harbour", "author": "Elena Vale", "status": "finished"},
    {"id": 4, "title": "North of Tomorrow", "author": "Daniel Frost", "status": "unread"},
    {"id": 5, "title": "The Last Lantern", "author": "Nora Blake", "status": "reading"},
]

VALID_STATUSES = ["unread", "reading", "finished"]


@pytest.fixture(autouse=True)
def reset_books_state():
    """Function-scoped autouse fixture: resets in-memory state before every
    test to exactly 5 seeded books (ids 1-5) with next id 6. Calls the
    internal (non-HTTP) reset mechanism Task 2a provides in src.main.
    # rule 10, rule 11
    """
    reset_state()
    yield


def assert_error_body(response, status_code, message):
    """Every error response must be exactly {"error": "<message>"}.
    # rule 35, rule 36 (never FastAPI's default 422 for a spec-covered case)
    """
    assert response.status_code == status_code
    assert response.status_code != 422
    body = response.json()
    assert body == {"error": message}
    assert list(body.keys()) == ["error"]
    assert isinstance(body["error"], str)


# ---------------------------------------------------------------------------
# GET /books
# ---------------------------------------------------------------------------

def test_list_books_default_pagination_returns_all_seeded_books():
    # rule 10, 12, 13, 15
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == SEEDED_BOOKS


def test_list_books_returns_plain_array_not_wrapped():
    # rule 12
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_books_has_exactly_five_books_by_default():
    # rule 10, 11 - deliberately placed before the "create" test below to
    # prove that the reset fixture (not test execution order) controls
    # state: this test must see exactly 5 books no matter what other
    # tests ran before it.
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_list_books_pagination_slices_by_page_and_limit_ascending_by_id():
    # rule 15
    response = client.get("/books", params={"page": 2, "limit": 2})
    assert response.status_code == 200
    assert response.json() == SEEDED_BOOKS[2:4]  # ids 3 and 4


def test_list_books_page_beyond_available_results_returns_empty_list():
    # rule 16
    response = client.get("/books", params={"page": 4, "limit": 2})
    assert response.status_code == 200
    assert response.json() == []


def test_list_books_limit_boundary_50_is_valid():
    # rule 13, 14 (limit=50 valid)
    response = client.get("/books", params={"limit": 50})
    assert response.status_code == 200


def test_list_books_limit_boundary_51_is_invalid():
    # rule 14 (limit=51 invalid)
    response = client.get("/books", params={"limit": 51})
    assert_error_body(response, 400, "Invalid pagination")


def test_list_books_page_boundary_1_is_valid():
    # rule 13, 14 (page=1 valid)
    response = client.get("/books", params={"page": 1})
    assert response.status_code == 200


def test_list_books_page_boundary_0_is_invalid():
    # rule 14 (page=0 invalid)
    response = client.get("/books", params={"page": 0})
    assert_error_body(response, 400, "Invalid pagination")


@pytest.mark.parametrize("page", [-1, "abc"])
def test_list_books_invalid_page_values(page):
    # rule 14
    response = client.get("/books", params={"page": page})
    assert_error_body(response, 400, "Invalid pagination")


@pytest.mark.parametrize("limit", [0, -5, "abc"])
def test_list_books_invalid_limit_values(limit):
    # rule 14
    response = client.get("/books", params={"limit": limit})
    assert_error_body(response, 400, "Invalid pagination")


def test_list_books_invalid_pagination_never_returns_default_422():
    # rule 36 - page/limit type errors must be the spec's 400, not
    # FastAPI's default 422 for a query-param type mismatch.
    response = client.get("/books", params={"page": "abc", "limit": "xyz"})
    assert response.status_code == 400
    assert response.status_code != 422


# ---------------------------------------------------------------------------
# GET /books/{id}
# ---------------------------------------------------------------------------

def test_get_book_valid_id_returns_full_book():
    # rule 19
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json() == SEEDED_BOOKS[0]


def test_get_book_id_boundary_1_is_valid():
    # rule 17 (id=1 valid)
    response = client.get("/books/1")
    assert response.status_code == 200


def test_get_book_id_boundary_0_is_invalid():
    # rule 17 (id=0 invalid)
    response = client.get("/books/0")
    assert_error_body(response, 400, "Invalid book id")


def test_get_book_negative_id_is_invalid():
    # rule 17
    response = client.get("/books/-1")
    assert_error_body(response, 400, "Invalid book id")


def test_get_book_non_numeric_id_is_invalid():
    # rule 17
    response = client.get("/books/abc")
    assert_error_body(response, 400, "Invalid book id")


def test_get_book_valid_format_nonexistent_id_returns_404():
    # rule 18
    response = client.get("/books/999")
    assert_error_body(response, 404, "Book not found")


# ---------------------------------------------------------------------------
# POST /books
# ---------------------------------------------------------------------------

def test_create_book_success_assigns_next_id_and_returns_201():
    # rule 6, 11, 27 - deliberately placed after the "list has exactly
    # five books" test above to prove order independence of the reset
    # fixture.
    payload = {"title": "New Book", "author": "New Author", "status": "unread"}
    response = client.post("/books", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body == {"id": 6, "title": "New Book", "author": "New Author", "status": "unread"}


def test_create_book_trims_title_and_author_whitespace():
    # rule 7, 8, 27
    payload = {"title": "  Padded Title  ", "author": "  Padded Author  ", "status": "unread"}
    response = client.post("/books", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Padded Title"
    assert body["author"] == "Padded Author"


@pytest.mark.parametrize("status_value", VALID_STATUSES)
def test_create_book_accepts_each_valid_status(status_value):
    # rule 9, 27
    payload = {"title": "T", "author": "A", "status": status_value}
    response = client.post("/books", json=payload)
    assert response.status_code == 201
    assert response.json()["status"] == status_value


def test_create_book_title_exactly_200_chars_is_valid():
    # rule 7, 24c (boundary: 200 valid)
    payload = {"title": "x" * 200, "author": "A", "status": "unread"}
    response = client.post("/books", json=payload)
    assert response.status_code == 201


def test_create_book_title_201_chars_is_invalid():
    # rule 24c (boundary: 201 invalid)
    payload = {"title": "x" * 201, "author": "A", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Title must be between 1 and 200 characters")


def test_create_book_title_exactly_1_char_is_valid():
    # rule 7 (boundary: 1 char valid)
    payload = {"title": "x", "author": "A", "status": "unread"}
    response = client.post("/books", json=payload)
    assert response.status_code == 201


def test_create_book_title_empty_after_trim_is_invalid():
    # rule 24c (boundary: "" invalid; also whitespace-only trims to empty)
    payload = {"title": "   ", "author": "A", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Title must be between 1 and 200 characters")


def test_create_book_title_missing_is_invalid():
    # rule 24a
    payload = {"author": "A", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Title must be between 1 and 200 characters")


@pytest.mark.parametrize("bad_title", [123, None, True, [], {}])
def test_create_book_title_wrong_type_is_invalid_request_body(bad_title):
    # rule 24b
    payload = {"title": bad_title, "author": "A", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Invalid request body")


def test_create_book_author_exactly_100_chars_is_valid():
    # rule 8, 25 (boundary: 100 valid)
    payload = {"title": "T", "author": "x" * 100, "status": "unread"}
    response = client.post("/books", json=payload)
    assert response.status_code == 201


def test_create_book_author_101_chars_is_invalid():
    # rule 25 (boundary: 101 invalid)
    payload = {"title": "T", "author": "x" * 101, "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Author must be between 1 and 100 characters")


def test_create_book_author_empty_after_trim_is_invalid():
    # rule 25 (boundary: "" invalid)
    payload = {"title": "T", "author": "   ", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Author must be between 1 and 100 characters")


def test_create_book_author_missing_is_invalid():
    # rule 25 (mirrors 24a)
    payload = {"title": "T", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Author must be between 1 and 100 characters")


@pytest.mark.parametrize("bad_author", [123, None, True, [], {}])
def test_create_book_author_wrong_type_is_invalid_request_body(bad_author):
    # rule 25 (mirrors 24b)
    payload = {"title": "T", "author": bad_author, "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Invalid request body")


def test_create_book_status_missing_is_invalid():
    # rule 26
    payload = {"title": "T", "author": "A"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Status must be one of: unread, reading, finished")


def test_create_book_status_unknown_value_is_invalid():
    # rule 26
    payload = {"title": "T", "author": "A", "status": "borrowed"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Status must be one of: unread, reading, finished")


def test_create_book_status_case_sensitive_is_invalid():
    # rule 9, 26 ("Unread" is invalid, comparison is case-sensitive)
    payload = {"title": "T", "author": "A", "status": "Unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Status must be one of: unread, reading, finished")


@pytest.mark.parametrize("bad_status", [123, None, True, [], {}])
def test_create_book_status_wrong_type_collapses_to_membership_error(bad_status):
    # rule 26 - unlike title/author there is no separate wrong-type message
    payload = {"title": "T", "author": "A", "status": bad_status}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Status must be one of: unread, reading, finished")


def test_create_book_unexpected_field_is_rejected():
    # rule 20, 22
    payload = {"title": "T", "author": "A", "status": "unread", "price": 9.99}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Unexpected field: price")


def test_create_book_client_supplied_id_is_rejected():
    # rule 6, 20, 22 - clients must never supply id
    payload = {"id": 999, "title": "T", "author": "A", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Unexpected field: id")


def test_create_book_unexpected_fields_reported_alphabetically_first():
    # rule 22 - both "price" and "id" unexpected -> "id" reported first
    payload = {"id": 999, "title": "T", "author": "A", "status": "unread", "price": 9.99}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Unexpected field: id")


def test_create_book_malformed_json_body_is_invalid_request_body():
    # rule 21
    response = client.post(
        "/books",
        content=b'{"title": "A", "author": "B", "status": "unread",}',
        headers={"Content-Type": "application/json"},
    )
    assert_error_body(response, 400, "Invalid request body")


@pytest.mark.parametrize("non_object_body", [[1, 2, 3], "a string", 123, None])
def test_create_book_valid_json_non_object_is_invalid_request_body(non_object_body):
    # rule 21
    response = client.post("/books", json=non_object_body)
    assert_error_body(response, 400, "Invalid request body")


def test_create_book_validation_priority_title_checked_before_author():
    # rule 23 - both title and author invalid -> title's error reported
    payload = {"title": "", "author": "", "status": "unread"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Title must be between 1 and 200 characters")


def test_create_book_validation_priority_author_checked_before_status():
    # rule 23 - author and status both invalid -> author's error reported
    payload = {"title": "T", "author": "", "status": "bogus"}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Author must be between 1 and 100 characters")


def test_create_book_unexpected_field_checked_before_field_validation():
    # rule 22, 23 - unexpected field takes priority over an invalid title
    payload = {"title": "", "author": "A", "status": "unread", "extra": True}
    response = client.post("/books", json=payload)
    assert_error_body(response, 400, "Unexpected field: extra")


def test_create_book_malformed_body_never_returns_default_422():
    # rule 36
    response = client.post(
        "/books",
        content=b"not json at all",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.status_code != 422


# ---------------------------------------------------------------------------
# PATCH /books/{id}
# ---------------------------------------------------------------------------

def test_patch_book_id_validated_before_body_is_read():
    # rule 28 - invalid id short-circuits before malformed body is parsed
    response = client.patch(
        "/books/abc",
        content=b"{not valid json",
        headers={"Content-Type": "application/json"},
    )
    assert_error_body(response, 400, "Invalid book id")


def test_patch_book_invalid_id_format_zero():
    # rule 17, 28 (id=0 invalid)
    response = client.patch("/books/0", json={"status": "reading"})
    assert_error_body(response, 400, "Invalid book id")


def test_patch_book_invalid_id_format_non_numeric():
    # rule 17, 28
    response = client.patch("/books/abc", json={"status": "reading"})
    assert_error_body(response, 400, "Invalid book id")


def test_patch_book_nonexistent_id_returns_404():
    # rule 18, 28
    response = client.patch("/books/999", json={"status": "reading"})
    assert_error_body(response, 404, "Book not found")


def test_patch_book_malformed_json_after_id_resolves_is_invalid_request_body():
    # rule 29 - id exists, body is malformed JSON
    response = client.patch(
        "/books/1",
        content=b"{bad json",
        headers={"Content-Type": "application/json"},
    )
    assert_error_body(response, 400, "Invalid request body")


@pytest.mark.parametrize("non_object_body", [[1, 2], "a string", 42, None])
def test_patch_book_valid_json_non_object_is_invalid_request_body(non_object_body):
    # rule 29
    response = client.patch("/books/1", json=non_object_body)
    assert_error_body(response, 400, "Invalid request body")


def test_patch_book_extra_field_title_is_rejected():
    # rule 30, 31a
    response = client.patch("/books/1", json={"status": "reading", "title": "New"})
    assert_error_body(response, 400, "Only status may be updated")


def test_patch_book_extra_field_id_is_rejected():
    # rule 30, 31a
    response = client.patch("/books/1", json={"status": "reading", "id": 2})
    assert_error_body(response, 400, "Only status may be updated")


def test_patch_book_missing_status_empty_body_is_invalid():
    # rule 31b
    response = client.patch("/books/1", json={})
    assert_error_body(response, 400, "Status is required")


def test_patch_book_invalid_status_value_is_rejected():
    # rule 31c
    response = client.patch("/books/1", json={"status": "borrowed"})
    assert_error_body(response, 400, "Status must be one of: unread, reading, finished")


def test_patch_book_status_case_sensitive_is_rejected():
    # rule 9, 31c
    response = client.patch("/books/1", json={"status": "Reading"})
    assert_error_body(response, 400, "Status must be one of: unread, reading, finished")


def test_patch_book_validation_priority_extra_field_over_missing_status():
    # rule 31 - extra field present AND status missing -> extra field wins
    response = client.patch("/books/1", json={"title": "New"})
    assert_error_body(response, 400, "Only status may be updated")


def test_patch_book_validation_priority_extra_field_over_invalid_status():
    # rule 31 - extra field present AND status invalid -> extra field wins
    response = client.patch("/books/1", json={"title": "New", "status": "bogus"})
    assert_error_body(response, 400, "Only status may be updated")


@pytest.mark.parametrize("status_value", VALID_STATUSES)
def test_patch_book_success_updates_status_only(status_value):
    # rule 31d - success case; also confirms title/author are unchanged
    original = client.get("/books/2").json()
    response = client.patch("/books/2", json={"status": status_value})
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 2
    assert body["status"] == status_value
    assert body["title"] == original["title"]
    assert body["author"] == original["author"]


def test_patch_book_never_returns_default_422():
    # rule 36
    response = client.patch("/books/1", json={"status": "bogus"})
    assert response.status_code == 400
    assert response.status_code != 422


# ---------------------------------------------------------------------------
# DELETE /books/{id}
# ---------------------------------------------------------------------------

def test_delete_book_invalid_id_format_zero():
    # rule 17, 32
    response = client.delete("/books/0")
    assert_error_body(response, 400, "Invalid book id")


def test_delete_book_invalid_id_format_non_numeric():
    # rule 17, 32
    response = client.delete("/books/abc")
    assert_error_body(response, 400, "Invalid book id")


def test_delete_book_nonexistent_id_returns_404():
    # rule 18, 32
    response = client.delete("/books/999")
    assert_error_body(response, 404, "Book not found")


def test_delete_book_success_returns_204_with_empty_body():
    # rule 33
    response = client.delete("/books/1")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_book_then_get_returns_404():
    # rule 34
    delete_response = client.delete("/books/1")
    assert delete_response.status_code == 204
    get_response = client.get("/books/1")
    assert_error_body(get_response, 404, "Book not found")


def test_delete_book_then_delete_again_returns_404():
    # rule 34
    first = client.delete("/books/1")
    assert first.status_code == 204
    second = client.delete("/books/1")
    assert_error_body(second, 404, "Book not found")

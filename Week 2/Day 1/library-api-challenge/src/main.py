import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

VALID_STATUSES = ("unread", "reading", "finished")

SEED_BOOKS = [
    {"id": 1, "title": "The Silent Planet", "author": "Mira Cole", "status": "unread"},
    {"id": 2, "title": "Beyond the River", "author": "Sam Rowan", "status": "reading"},
    {"id": 3, "title": "Glass Harbour", "author": "Elena Vale", "status": "finished"},
    {"id": 4, "title": "North of Tomorrow", "author": "Daniel Frost", "status": "unread"},
    {"id": 5, "title": "The Last Lantern", "author": "Nora Blake", "status": "reading"},
]

books = []
next_id = 1


def reset_state():
    """Internal test-support reset (rule 11). Not exposed as an HTTP route."""
    global books, next_id
    books = [dict(book) for book in SEED_BOOKS]
    next_id = 6


reset_state()


def _parse_pagination(page_raw, limit_raw):
    """Returns (page, limit) or None if invalid per rule 14."""
    try:
        page = int(page_raw)
        limit = int(limit_raw)
    except (TypeError, ValueError):
        return None
    if page < 1 or limit < 1 or limit > 50:
        return None
    return page, limit


@app.get("/books")
def list_books(page: str = "1", limit: str = "10"):
    # rules 12-16
    parsed = _parse_pagination(page, limit)
    if parsed is None:
        return JSONResponse(status_code=400, content={"error": "Invalid pagination"})
    page_num, limit_num = parsed
    ordered_books = sorted(books, key=lambda book: book["id"])
    start = (page_num - 1) * limit_num
    end = start + limit_num
    return ordered_books[start:end]


def _parse_book_id(book_id_raw):
    """Returns a positive int book id, or None if invalid per rule 17."""
    try:
        book_id = int(book_id_raw)
    except (TypeError, ValueError):
        return None
    if book_id < 1:
        return None
    return book_id


def _find_book(book_id):
    return next((book for book in books if book["id"] == book_id), None)


@app.get("/books/{book_id}")
def get_book(book_id: str):
    # rules 17-19
    parsed_id = _parse_book_id(book_id)
    if parsed_id is None:
        return JSONResponse(status_code=400, content={"error": "Invalid book id"})
    book = _find_book(parsed_id)
    if book is None:
        return JSONResponse(status_code=404, content={"error": "Book not found"})
    return book


async def _parse_json_object(request: Request):
    """Returns the parsed JSON object, or None if malformed/non-object (rule 21/29)."""
    try:
        parsed = json.loads(await request.body())
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _validate_length_bound_string(value_present, value, field_label, min_len, max_len):
    """Validates title/author per rule 24/25. Returns an error message or None."""
    length_error = f"{field_label} must be between {min_len} and {max_len} characters"
    if not value_present:
        return length_error
    if not isinstance(value, str):
        return "Invalid request body"
    trimmed = value.strip()
    if len(trimmed) < min_len or len(trimmed) > max_len:
        return length_error
    return None


@app.post("/books")
async def create_book(request: Request):
    # rule 21
    body = await _parse_json_object(request)
    if body is None:
        return JSONResponse(status_code=400, content={"error": "Invalid request body"})

    # rule 22
    allowed_fields = {"title", "author", "status"}
    unexpected_fields = sorted(field for field in body if field not in allowed_fields)
    if unexpected_fields:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unexpected field: {unexpected_fields[0]}"},
        )

    # rule 23-24
    title_error = _validate_length_bound_string(
        "title" in body, body.get("title"), "Title", 1, 200
    )
    if title_error:
        return JSONResponse(status_code=400, content={"error": title_error})

    # rule 25
    author_error = _validate_length_bound_string(
        "author" in body, body.get("author"), "Author", 1, 100
    )
    if author_error:
        return JSONResponse(status_code=400, content={"error": author_error})

    # rule 26
    status_value = body.get("status")
    if status_value not in VALID_STATUSES:
        return JSONResponse(
            status_code=400,
            content={"error": "Status must be one of: unread, reading, finished"},
        )

    # rule 27
    global next_id
    new_book = {
        "id": next_id,
        "title": body["title"].strip(),
        "author": body["author"].strip(),
        "status": status_value,
    }
    books.append(new_book)
    next_id += 1
    return JSONResponse(status_code=201, content=new_book)


@app.patch("/books/{book_id}")
async def patch_book(book_id: str, request: Request):
    # rule 28
    parsed_id = _parse_book_id(book_id)
    if parsed_id is None:
        return JSONResponse(status_code=400, content={"error": "Invalid book id"})
    book = _find_book(parsed_id)
    if book is None:
        return JSONResponse(status_code=404, content={"error": "Book not found"})

    # rule 29
    body = await _parse_json_object(request)
    if body is None:
        return JSONResponse(status_code=400, content={"error": "Invalid request body"})

    # rule 31a
    if any(field != "status" for field in body):
        return JSONResponse(status_code=400, content={"error": "Only status may be updated"})

    # rule 31b
    if "status" not in body:
        return JSONResponse(status_code=400, content={"error": "Status is required"})

    # rule 31c
    status_value = body["status"]
    if status_value not in VALID_STATUSES:
        return JSONResponse(
            status_code=400,
            content={"error": "Status must be one of: unread, reading, finished"},
        )

    # rule 31d
    book["status"] = status_value
    return book


@app.delete("/books/{book_id}")
def delete_book(book_id: str):
    # rule 32
    parsed_id = _parse_book_id(book_id)
    if parsed_id is None:
        return JSONResponse(status_code=400, content={"error": "Invalid book id"})
    book = _find_book(parsed_id)
    if book is None:
        return JSONResponse(status_code=404, content={"error": "Book not found"})

    # rule 33
    books.remove(book)
    return Response(status_code=204)

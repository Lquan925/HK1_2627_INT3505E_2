"""Lab 1: four required Books API tests (A-D)."""


def test_get_books_returns_empty_array(client):
    """A: An empty database returns [], rather than null."""
    response = client.get("/books")

    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == []


def test_get_nonexistent_book_returns_not_found(client):
    """B: A nonexistent book returns 404 with the expected error code."""
    response = client.get("/books/9999")

    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["code"] == "NOT_FOUND"


def test_post_book_without_title_returns_validation_error(client):
    """C: Omitting title returns 400 and identifies the missing field."""
    response = client.post("/books", json={"author": "J.J. Geewax"})

    assert response.status_code == 400
    assert response.is_json
    errors = response.get_json()["errors"]
    assert any(error["field"] == "title" for error in errors)


def test_get_deleted_book_returns_not_found(client):
    """D: Create and delete a book, then verify the same ID returns 404."""
    created = client.post(
        "/books",
        json={"title": "API Design Patterns", "author": "J.J. Geewax"},
    )
    assert created.status_code == 201
    book_id = created.get_json()["id"]

    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["code"] == "NOT_FOUND"

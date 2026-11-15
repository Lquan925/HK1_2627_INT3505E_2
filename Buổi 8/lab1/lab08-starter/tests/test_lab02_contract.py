"""Validate Flask responses against the declared OpenAPI Book contract."""
from copy import deepcopy

import pytest
from jsonschema import Draft4Validator, ValidationError

from models import Book
from tools import get_book_schema


@pytest.fixture
def book_validator():
    schema = deepcopy(get_book_schema())
    # OpenAPI 3.0 nullable is not a JSON Schema keyword.
    for field in schema["properties"].values():
        if field.pop("nullable", False):
            field["type"] = [field["type"], "null"]
    Draft4Validator.check_schema(schema)
    return Draft4Validator(schema)


def test_book_crud_responses_match_contract(client, book_validator):
    created = client.post("/books", json={
        "title": "API Design Patterns", "author": "J.J. Geewax", "year": 2021,
    })
    assert created.status_code == 201
    assert created.is_json
    book_validator.validate(created.get_json())
    book_id = created.get_json()["id"]

    fetched = client.get(f"/books/{book_id}")
    assert fetched.status_code == 200
    assert fetched.is_json
    book_validator.validate(fetched.get_json())

    listed = client.get("/books")
    assert listed.status_code == 200
    assert listed.is_json
    books = listed.get_json()
    assert isinstance(books, list) and len(books) == 1
    book_validator.validate(books[0])

    updated = client.put(f"/books/{book_id}", json={
        "title": "Updated", "author": "Author", "year": 2024,
    })
    assert updated.status_code == 200
    assert updated.is_json
    book_validator.validate(updated.get_json())
    assert updated.get_json()["year"] == 2024

    updated = client.put(f"/books/{book_id}", json={
        "title": "Updated", "author": "Author",
    })
    assert updated.status_code == 200
    assert updated.is_json
    book_validator.validate(updated.get_json())
    assert updated.get_json()["year"] is None

    deleted = client.delete(f"/books/{book_id}")
    assert deleted.status_code == 204
    assert deleted.data == b""


@pytest.mark.parametrize("defect", ["wrong_type", "missing_field", "extra_field"])
def test_contract_detects_incorrect_flask_fields(
    client, sample_book, monkeypatch, book_validator, defect,
):
    original = Book.to_dict

    def broken_response(book):
        payload = original(book)
        if defect == "wrong_type":
            payload["year"] = "2021"
        elif defect == "missing_field":
            payload.pop("title")
        else:
            payload["unexpected"] = True
        return payload

    monkeypatch.setattr(Book, "to_dict", broken_response)
    response = client.get(f"/books/{sample_book}")
    assert response.status_code == 200
    with pytest.raises(ValidationError):
        book_validator.validate(response.get_json())

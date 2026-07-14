"""
Unit tests for the helper functions in app/books.py:
  - error_response  (uniform error shape, issue #20)
  - is_owner        (ownership check contract, issues #21 / #33)
  - load_books / save_books (data-access layer, issue #18)

These test the functions directly, with no HTTP server. `error_response`
uses `jsonify`, so it needs a Flask application context — provided by the
`app_ctx` fixture below.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from flask import Flask

import app.books as books


@pytest.fixture
def app_ctx():
    app = Flask(__name__)
    with app.app_context():
        yield app


class TestErrorResponse:
    """error_response must always return {"message": ...} plus the status code."""

    def test_returns_message_body_and_status_code(self, app_ctx):
        resp, code = books.error_response("not found", 404)
        assert code == 404
        assert resp.get_json() == {"message": "not found"}

    def test_always_uses_the_message_key(self, app_ctx):
        resp, _ = books.error_response("anything", 400)
        assert "message" in resp.get_json()
        assert "error" not in resp.get_json()

    def test_preserves_arbitrary_status_codes(self, app_ctx):
        for code in (400, 401, 403, 404, 409):
            _, returned = books.error_response("x", code)
            assert returned == code


class TestIsOwner:
    """
    is_owner is defined as `book[book_entry].get('added_by') == username`,
    i.e. it expects a dict KEY and indexes the module-level `book` itself.
    These tests pin that contract and document the crashes that happen when
    callers break it (issue #33).
    """

    def setup_method(self):
        self._original = books.book
        books.book = {
            "1": {"book_id": 1, "added_by": "alice"},
            "2": {"book_id": 2, "added_by": "bob"},
        }

    def teardown_method(self):
        books.book = self._original

    def test_true_when_key_owner_matches(self):
        assert books.is_owner("1", "alice") is True

    def test_false_when_key_owner_differs(self):
        assert books.is_owner("1", "bob") is False

    def test_false_for_unknown_username(self):
        assert books.is_owner("2", "carol") is False

    def test_missing_key_raises_keyerror_known_bug(self):
        # KNOWN BUG (#33): update_book calls is_owner(str(book_id)) without
        # first checking the book exists, so a non-existent id does
        # book['9999'] -> KeyError -> HTTP 500 instead of a clean 404.
        with pytest.raises(KeyError):
            books.is_owner("9999", "alice")

    def test_passing_entry_instead_of_key_raises_typeerror_known_bug(self):
        # KNOWN BUG (#33): delete_book and update_book pass the book ENTRY
        # (a dict) instead of the key, so is_owner does book[<dict>] ->
        # TypeError: unhashable type -> HTTP 500.
        entry = books.book["1"]
        with pytest.raises(TypeError):
            books.is_owner(entry, "alice")


class TestLoadSaveBooks:
    """load_books / save_books should round-trip and write atomically."""

    def _point_to_temp(self, tmp_path, monkeypatch):
        f = tmp_path / "Book_Loader.json"
        f.write_text("{}")
        monkeypatch.setattr(books, "BOOKS_FILE", str(f))
        return f

    def test_roundtrip_preserves_data(self, tmp_path, monkeypatch):
        self._point_to_temp(tmp_path, monkeypatch)
        data = {"1": {"book_id": 1, "book_name": "Dune"}}
        books.save_books(data)
        assert books.load_books() == data

    def test_save_overwrites_previous_content(self, tmp_path, monkeypatch):
        self._point_to_temp(tmp_path, monkeypatch)
        books.save_books({"1": {"book_id": 1}})
        books.save_books({"2": {"book_id": 2}})
        assert books.load_books() == {"2": {"book_id": 2}}

    def test_save_leaves_no_tmp_file_behind(self, tmp_path, monkeypatch):
        self._point_to_temp(tmp_path, monkeypatch)
        books.save_books({"a": 1})
        assert not (tmp_path / "Book_Loader.json.tmp").exists()

    def test_load_empty_file_returns_empty_dict(self, tmp_path, monkeypatch):
        self._point_to_temp(tmp_path, monkeypatch)
        assert books.load_books() == {}

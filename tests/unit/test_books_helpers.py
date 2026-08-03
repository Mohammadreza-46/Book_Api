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
    is_owner takes a book ENTRY (a dict) and checks its 'added_by' field:
    `book_entry.get('added_by') == username`. It never indexes the module
    dict itself, so it cannot crash on a missing id — that keeps update_book
    and delete_book able to return a clean 403/404 (issues #21 / #33).
    """

    ALICE_BOOK = {"book_id": 1, "added_by": "alice"}
    BOB_BOOK = {"book_id": 2, "added_by": "bob"}

    def test_true_when_owner_matches(self):
        assert books.is_owner(self.ALICE_BOOK, "alice") is True

    def test_false_when_owner_differs(self):
        assert books.is_owner(self.ALICE_BOOK, "bob") is False

    def test_false_for_unknown_username(self):
        assert books.is_owner(self.BOB_BOOK, "carol") is False

    def test_false_when_entry_has_no_added_by(self):
        # A malformed entry without 'added_by' is simply not owned by anyone,
        # rather than raising — .get() returns None, which never equals a name.
        assert books.is_owner({"book_id": 3}, "alice") is False


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

    def test_roundtrip_preserves_non_ascii_text(self, tmp_path, monkeypatch):
        # Persian/Unicode book data must survive save -> load unchanged.
        # load_books/save_books open files with encoding='utf-8'; without that,
        # Windows would fall back to the locale codepage and corrupt or crash.
        self._point_to_temp(tmp_path, monkeypatch)
        data = {
            "1": {
                "book_id": 1,
                "book_name": "کتاب فارسی",
                "writer": "نویسنده",
                "book_content": "متنِ نمونه با emoji 📚",
            }
        }
        books.save_books(data)
        assert books.load_books() == data

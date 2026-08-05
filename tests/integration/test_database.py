"""
Integration tests that verify book and user data is stored in the DATABASE
(issues #43 and #44), not in the old JSON files — and that the test suite runs
against an isolated test database (issue #46).

These run against the live server started by tests/conftest.py. They then open
the SQLite database file directly to confirm rows really landed in the tables.
"""
import sqlite3

import pytest
import requests

from tests.conftest import (
    BASE_URL,
    DATA_DIR,
    USERS_DIR,
    unique_user,
    unique_book_id,
    register,
    register_and_login,
    auth_headers,
    make_book,
)

# The server falls back to this database when no override is set (see main.py).
DEV_DB = DATA_DIR / "app.db"
TEST_DB = DATA_DIR / "test_app.db"


def _query(db_path, sql, params=()):
    con = sqlite3.connect(str(db_path))
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


class TestUserPersistence:
    """Issue #43: signup/login use the users table, not data/Users/*.json."""

    def test_signup_creates_a_users_row(self):
        username = unique_user()
        register(username)
        rows = _query(DEV_DB, "SELECT username FROM users WHERE username = ?", (username,))
        assert rows, f"no users row created for {username}"

    def test_signup_does_not_create_a_json_user_file(self):
        username = unique_user()
        register(username)
        assert not (USERS_DIR / f"{username}.json").exists(), (
            "signup still wrote a JSON user file — file storage not removed"
        )

    def test_password_is_stored_as_bcrypt_hash_in_db(self):
        username = unique_user()
        register(username, "PlainPassword1")
        rows = _query(DEV_DB, "SELECT password FROM users WHERE username = ?", (username,))
        assert rows, "user not found in db"
        stored = rows[0][0]
        assert stored != "PlainPassword1"
        assert stored.startswith("$2b$")


class TestBookPersistence:
    """Issue #44: book endpoints read/write the books table, not the JSON file."""

    def test_added_book_creates_a_books_row(self):
        tokens = register_and_login(unique_user())
        bid = unique_book_id()
        requests.post(f"{BASE_URL}/add_book", json=make_book(bid, book_name="DB Row Book"),
                      headers=auth_headers(tokens["token"]))
        rows = _query(DEV_DB, "SELECT book_name FROM books WHERE book_id = ?", (bid,))
        assert rows and rows[0][0] == "DB Row Book"

    def test_book_owner_id_links_to_the_users_table(self):
        username = unique_user()
        tokens = register_and_login(username)
        bid = unique_book_id()
        requests.post(f"{BASE_URL}/add_book", json=make_book(bid),
                      headers=auth_headers(tokens["token"]))
        rows = _query(
            DEV_DB,
            "SELECT u.username FROM books b JOIN users u ON b.owner_id = u.id "
            "WHERE b.book_id = ?",
            (bid,),
        )
        assert rows and rows[0][0] == username

    def test_deleting_a_book_removes_the_row(self):
        tokens = register_and_login(unique_user())
        h = auth_headers(tokens["token"])
        bid = unique_book_id()
        requests.post(f"{BASE_URL}/add_book", json=make_book(bid), headers=h)
        requests.delete(f"{BASE_URL}/delete_book/{bid}", headers=h)
        rows = _query(DEV_DB, "SELECT 1 FROM books WHERE book_id = ?", (bid,))
        assert rows == []


class TestTestDatabaseIsolation:
    """
    Issue #46: integration tests should run against a SEPARATE test database
    (e.g. data/test_app.db via DATABASE_URL), not pollute the developer's
    data/app.db. conftest.py does not set this up yet.
    """

    def test_integration_server_uses_isolated_test_database(self):
        # EXPECTED TO FAIL (open bug #46): no dedicated test database is
        # configured, so the live server reads/writes the real dev DB.
        assert TEST_DB.exists(), (
            "tests run against the dev database (data/app.db); "
            "no isolated data/test_app.db was created"
        )

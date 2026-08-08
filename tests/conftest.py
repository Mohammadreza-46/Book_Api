import os
import subprocess
import time
import uuid
from pathlib import Path
import pytest
import requests
import sys

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
TEST_DB = DATA_DIR / "test_app.db"
USERS_DIR = DATA_DIR / "Users"
BOOK_LOADER = DATA_DIR / "Book_Loader.json"
BASE_URL = "http://localhost:5000"
TEST_JWT_SECRET = "integration-test-secret-key-very-long-and-secure"
if TEST_DB.exists():
    TEST_DB.unlink()
def _wait_for_server(timeout=15):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = requests.get(f"{BASE_URL}/get_all_book", timeout=1)
            if r.status_code in (200, 401, 422):
                return True
        except Exception:
            pass
        time.sleep(0.3)
    return False


@pytest.fixture(scope="session", autouse=True)
def flask_server():
    USERS_DIR.mkdir(parents=True, exist_ok=True)

    original_books = BOOK_LOADER.read_text() if BOOK_LOADER.exists() else "{}"
    BOOK_LOADER.write_text("{}")
    for f in USERS_DIR.glob("*.json"):
        f.unlink()
    env = os.environ.copy()
    env["JWT_SECRET_KEY"] = TEST_JWT_SECRET
    # Run a single-process server (no auto-reloader child), so terminate()
    # below reliably stops it on every OS — Windows included — instead of
    # leaving an orphan holding port 5000.
    env["USE_RELOADER"] = "0"
    # Point the whole stack at an isolated throwaway DB (issue #46) so tests
    # never touch the developer's data/app.db.
    env["DATABASE_URL"] = "sqlite:///" + TEST_DB.as_posix()

    # Build the schema in the fresh test DB before the server starts. main.py
    # does not create tables on its own, so without this the server would come
    # up against an empty file and every DB write would 500 with "no such
    # table". `flask db upgrade` runs the migrations (issue #42) into test_app.db.
    upgrade = subprocess.run(
        [sys.executable, "-m", "flask", "--app", "main", "db", "upgrade"],
        cwd=str(PROJECT_DIR), env=env,
        capture_output=True, text=True,
    )
    if upgrade.returncode != 0:
        raise RuntimeError(
            "flask db upgrade failed while preparing the test database:\n"
            + upgrade.stderr[-1000:]
        )

    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=str(PROJECT_DIR), env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    if not _wait_for_server():
        proc.terminate()
        raise RuntimeError("Flask server did not start — check that port 5000 is free")

    yield BASE_URL

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()

    BOOK_LOADER.write_text(original_books)
    for f in USERS_DIR.glob("*.json"):
        f.unlink()


def unique_user():
    return f"testuser_{uuid.uuid4().hex[:8]}"


def unique_book_id():
    return int(uuid.uuid4().int % 900_000) + 100_000


def register(username, password="Password123"):
    return requests.post(f"{BASE_URL}/signup", json={"username": username, "password": password})


def login(username, password="Password123"):
    return requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})


def register_and_login(username, password="Password123"):
    register(username, password)
    r = login(username, password)
    return r.json()


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def make_book(book_id, **overrides):
    book = {
        "book_name": f"Test Book {book_id}",
        "book_content": "This is the content of the test book.",
        "book_id": book_id,
        "writer": "Test Author",
        "published_year": 2024,
        "rating": 4,
        "genre": "Fiction",
        "created_at": "2024-01-01",
    }
    book.update(overrides)
    return book
if TEST_DB.exists():
    TEST_DB.unlink()
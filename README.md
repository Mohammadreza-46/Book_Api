# Book API

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-black)
![JWT](https://img.shields.io/badge/Auth-JWT-green)
![License](https://img.shields.io/badge/License-MIT-orange)

A REST API for managing a book collection, built with Flask. It provides JWT-based authentication, full CRUD operations on books, and simple file-based storage — with no external database required. The project runs the same way on Linux, macOS, and Windows.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [Running Tests](#running-tests)
- [API Reference](#api-reference)
- [Security](#security)
- [Technologies](#technologies)

---

## Features

- User signup and login with password hashing
- JWT access token + refresh token authentication
- Add, update, delete, and search books
- Pagination on book listing
- Per-user ownership — only the book owner can edit or delete
- File-based JSON storage
- Structured logging

---

## Project Structure

```
Book_Api/
├── app/
│   ├── __init__.py
│   ├── auth.py               # signup, login, refresh token
│   ├── books.py              # book CRUD and search
│   └── check_data.py         # request-body validation
├── data/
│   ├── Book_Loader.json      # book storage
│   └── Users/                # one JSON file per user
├── tests/
│   ├── conftest.py           # shared fixtures + test server
│   ├── unit/                 # fast, in-process tests
│   │   ├── test_check_data.py
│   │   ├── test_auth_helpers.py
│   │   └── test_books_helpers.py
│   └── integration/          # end-to-end tests against a live server
│       ├── test_auth.py
│       └── test_books.py
├── main.py                   # application entry point
├── Makefile                  # cross-platform dev commands
├── requirements.txt
└── .env.example
```

---

## Getting Started

### Prerequisites

- **Python 3.10 or newer**
- **GNU Make** — preinstalled on most Linux/macOS systems. On Windows, install it once with any of:
  ```
  winget install ezwinports.make      # or
  choco install make                  # or
  scoop install make
  ```
  The `make` targets then work identically from cmd, PowerShell, or a Unix shell.

### 1. Clone the repository

```bash
git clone https://github.com/Mohammadreza-46/Book_Api.git
cd Book_Api
```

### 2. Configure the secret key

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

Then open `.env` and set a long, random value. **`JWT_SECRET_KEY` must be at least 32 characters** — the server refuses to start otherwise:

```
JWT_SECRET_KEY=your-long-random-secret-key-at-least-32-chars
```

### 3. Install dependencies

```bash
make setup
```

This creates a virtual environment in `venv/` and installs everything from `requirements.txt`. To do it by hand:

```bash
python3 -m venv venv                # Windows: python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | Yes | Secret used to sign JWT tokens. Must be a long, random string of **at least 32 characters**. |

---

## Running the Server

```bash
make run
```

`make run` creates the required data directories, loads `JWT_SECRET_KEY` from your environment (falling back to an insecure dev default if it is unset), and starts the server. To run it manually with your own secret:

```bash
# Linux / macOS
JWT_SECRET_KEY=your-long-random-secret python3 main.py

# Windows (PowerShell)
$env:JWT_SECRET_KEY="your-long-random-secret"; python main.py
```

The server listens at:

```
http://localhost:5000
```

Stop it with `Ctrl+C`, or `make stop` from another terminal.

---

## Running Tests

The test suite runs the same on every platform — unit tests execute in-process, and integration tests boot a real server on port 5000 automatically (no manual setup needed).

```bash
make test              # run everything (unit + integration)
make test-unit         # unit tests only
make test-integration  # integration tests only
```

---

## API Reference

### Authentication

All book endpoints require a valid JWT access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

### Signup

```
POST /signup
```

**Body**

```json
{
  "username": "myusername",
  "password": "mypassword"
}
```

**Rules**
- `username`: minimum 8 characters, only letters, numbers, and underscores
- `password`: string

**Responses**

| Status | Description |
|--------|-------------|
| `200` | User created successfully |
| `400` | Validation failed (short username, invalid chars, wrong types) |
| `409` | Username already exists |

---

### Login

```
POST /login
```

**Body**

```json
{
  "username": "myusername",
  "password": "mypassword"
}
```

**Response `200`**

```json
{
  "message": "success",
  "token": "<access_token>",
  "refresh_token": "<refresh_token>"
}
```

| Status | Description |
|--------|-------------|
| `200` | Login successful |
| `400` | Wrong credentials or missing fields |

---

### Refresh Token

```
POST /refresh_token
```

**Header**

```
Authorization: Bearer <refresh_token>
```

**Response `200`**

```json
{
  "token": "<new_access_token>"
}
```

| Status | Description |
|--------|-------------|
| `200` | New access token issued |
| `401` | Invalid or expired refresh token |

---

### Get All Books

```
GET /get_all_book?page=1&per_page=10
```

**Query Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | `1` | Page number |
| `per_page` | `10` | Items per page |

**Response `200`**

```json
{
  "book": [
    {
      "book_id": 1,
      "book_name": "Clean Code",
      "writer": "Robert C. Martin",
      "genre": "Programming",
      "published_year": 2008,
      "rating": 5,
      "book_content": "...",
      "created_at": "2024-01-01",
      "added_at": "2025-06-01",
      "added_by": "myusername"
    }
  ]
}
```

---

### Get Book by ID

```
GET /get_book/<book_id>
```

**Response `200`**

```json
{
  "book_id": 1,
  "book_name": "Clean Code",
  "writer": "Robert C. Martin",
  "genre": "Programming",
  "published_year": 2008,
  "rating": 5,
  "book_content": "...",
  "created_at": "2024-01-01",
  "added_at": "2025-06-01",
  "added_by": "myusername"
}
```

| Status | Description |
|--------|-------------|
| `200` | Book found |
| `404` | Book not found |

---

### Add Book

```
POST /add_book
```

**Body**

```json
{
  "book_name": "Clean Code",
  "book_content": "A handbook of agile software craftsmanship.",
  "book_id": 1,
  "writer": "Robert C. Martin",
  "published_year": 2008,
  "rating": 5,
  "genre": "Programming",
  "created_at": "2024-01-01"
}
```

**Field Types**

| Field | Type |
|-------|------|
| `book_name` | string |
| `book_content` | string |
| `book_id` | integer |
| `writer` | string |
| `published_year` | integer |
| `rating` | integer |
| `genre` | string |
| `created_at` | string |

**Response `201`**

```json
{
  "Success": "New book added"
}
```

| Status | Description |
|--------|-------------|
| `201` | Book added |
| `400` | Validation failed or `book_id` already exists |

---

### Update Book

```
POST /update_book/<book_id>
```

Requires the same body fields as Add Book. Only the owner of the book can update it.

**Response `200`**

```json
{
  "Success": "Book updated"
}
```

| Status | Description |
|--------|-------------|
| `200` | Book updated |
| `400` | Validation failed |
| `404` | Book not found or user is not the owner |

---

### Delete Book

```
DELETE /delete_book/<book_id>
```

Only the owner of the book can delete it.

**Response `200`**

```json
{
  "Success": "Book deleted"
}
```

| Status | Description |
|--------|-------------|
| `200` | Book deleted |
| `404` | Book not found or user is not the owner |

---

### Search Books

```
POST /search
```

Provide at least one of the following fields:

**Body**

```json
{
  "book_name": "Clean"
}
```

```json
{
  "genre": "Programming"
}
```

```json
{
  "writer": "Martin"
}
```

Search is case-insensitive and matches partial strings.

**Response `200`**

```json
[
  {
    "book_id": 1,
    "book_name": "Clean Code",
    "writer": "Robert C. Martin"
  }
]
```

| Status | Description |
|--------|-------------|
| `200` | Results list (empty array if nothing found) |
| `400` | No search field provided |

---

## Security

| Mechanism | Detail |
|-----------|--------|
| Password hashing | `bcrypt` with cost factor 12 |
| Authentication | JWT via `Flask-JWT-Extended` |
| Access token lifetime | 1 hour |
| Refresh token lifetime | 30 days |
| Username validation | Alphanumeric and underscores only — blocks path traversal |
| Secret key | Loaded from environment variable — never hardcoded |

---

## Technologies

| Library | Purpose |
|---------|---------|
| Flask | Web framework |
| Flask-JWT-Extended | JWT authentication |
| bcrypt | Password hashing |
| pytest | Testing |
| requests | HTTP client for integration tests |

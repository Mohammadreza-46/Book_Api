# 📚 Book API

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![JWT](https://img.shields.io/badge/Auth-JWT-green)
![License](https://img.shields.io/badge/License-MIT-orange)

A simple yet secure REST API built with Flask for managing books and users using JWT Authentication.

---

## ✨ Features

* 🔐 User Registration
* 🔑 JWT Authentication
* ♻️ Refresh Token Support
* 📖 Add New Books
* 📚 Get All Books (Pagination)
* ✏️ Update Books
* 🗑 Delete Books
* 🔍 Search Books
* 🔒 Protected Routes
* 📝 Logging System
* 💾 JSON File Storage

---

## 📂 Project Structure

```text
book_api/
│
├── app/
│   ├── auth.py
│   ├── books.py
│   ├── storage.py
│   └── __init__.py
│
├── data/
│   ├── Book_Loader.json
│   ├── Keys.json
│   └── Users/
│
├── main.py
├── requirements.txt
├── app.log
└── README.md
```

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/Mohammadreza-46/book_api.git
cd book_api
```

## 2. Create Virtual Environment

### Linux / Mac

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run Project

```bash
python main.py
```

Server:

```text
http://localhost:5000
```

---

# 🔐 Authentication

This API uses JWT Access Token and Refresh Token.

After login you will receive:

```json
{
  "token": "ACCESS_TOKEN",
  "refresh_token": "REFRESH_TOKEN"
}
```

Use token in headers:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

# 📑 API Endpoints

---

## Signup

### Request

```http
POST /signup
```

### Body

```json
{
  "username": "testuser",
  "password": "12345678"
}
```

### Response

```json
{
  "message": "success"
}
```

---

## Login

### Request

```http
POST /login
```

### Body

```json
{
  "username": "testuser",
  "password": "12345678"
}
```

### Response

```json
{
  "message": "success",
  "token": "...",
  "refresh_token": "..."
}
```

---

## Refresh Token

### Request

```http
POST /refresh_token
```

### Header

```http
Authorization: Bearer REFRESH_TOKEN
```

### Response

```json
{
  "token": "NEW_ACCESS_TOKEN"
}
```

---

# 📚 Book Endpoints

All book routes require authentication.

---

## Get All Books

### Request

```http
GET /get_all_book?page=1&per_page=10
```

### Response

```json
{
  "book": [
    {
      "book_id": 1,
      "book_name": "Flask Guide"
    }
  ]
}
```

---

## Add Book

### Request

```http
POST /add_book
```

### Body

```json
{
  "book_name": "Flask Guide",
  "book_content": "Learning Flask",
  "book_id": 1,
  "writer": "John Doe",
  "published_year": 2025,
  "rating": 5,
  "genre": "Programming",
  "created_at": "2025-01-01"
}
```

### Response

```json
{
  "Success": "New book added"
}
```

---

## Update Book

### Request

```http
POST /update_book/<book_id>
```

### Response

```json
{
  "message": "Book updated"
}
```

---

## Delete Book

### Request

```http
GET /delete_book/<book_id>
```

### Response

```json
{
  "Success": "Book deleted"
}
```

---

## Search Book

### Request

```http
POST /search
```

### Body

```json
{
  "book_name": "Flask"
}
```

### Response

```json
[
  {
    "book_id": 1,
    "book_name": "Flask Guide"
  }
]
```

---

# 🔒 Security

Passwords are stored using:

```python
bcrypt
```

Authentication uses:

```python
Flask-JWT-Extended
```

Access Token Lifetime:

```text
1 Hour
```

Refresh Token Lifetime:

```text
30 Days
```

---

# 🧪 Example Using cURL

## Login

```bash
curl -X POST http://localhost:5000/login \
-H "Content-Type: application/json" \
-d '{
    "username":"testuser",
    "password":"12345678"
}'
```

---

## Add Book

```bash
curl -X POST http://localhost:5000/add_book \
-H "Authorization: Bearer TOKEN" \
-H "Content-Type: application/json" \
-d '{
    "book_name":"Flask Guide",
    "book_content":"Learn Flask",
    "book_id":1,
    "writer":"John",
    "published_year":2025,
    "rating":5,
    "genre":"Programming",
    "created_at":"2025-01-01"
}'
```

---

# 🛠 Technologies

* Python
* Flask
* Flask-JWT-Extended
* bcrypt
* JSON Storage
* Logging

---

# 📈 Future Improvements

* Swagger / OpenAPI Documentation
* PostgreSQL Support
* SQLAlchemy ORM
* Docker Support
* Role-Based Access Control (RBAC)
* Unit Tests
* CI/CD Pipeline

---

# 👨‍💻 Author

Developed with ❤️ using Flask.

If you found this project useful, consider giving it a ⭐ on GitHub.

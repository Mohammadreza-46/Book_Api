from pathlib import Path
import json

from main import app
from app.extensions import db
from app.models import User, Book


BASE_DIR = Path(__file__).resolve().parent.parent


def import_users():
    users_path = BASE_DIR / "data" / "Users"

    if not users_path.exists():
        return

    for file in users_path.glob("*.json"):
        with open(file, encoding="utf-8") as f:
            data = json.load(f)

        if User.query.filter_by(username=data["username"]).first():
            continue

        db.session.add(
            User(
                username=data["username"],
                password=data["password"],
            )
        )

    db.session.commit()


def import_books():
    books_path = BASE_DIR / "data" / "Book_Loader.json"

    if not books_path.exists():
        return

    with open(books_path, encoding="utf-8") as f:
        books = json.load(f)

    for data in books:
        if Book.query.filter_by(book_name=data["book_name"]).first():
            continue

        owner = User.query.filter_by(username=data["owner"]).first()

        db.session.add(
            Book(
                book_name=data["book_name"],
                book_content=data["book_content"],
                writer=data["writer"],
                published_year=data["published_year"],
                rating=data["rating"],
                genre=data["genre"],
                owner=owner,
            )
        )

    db.session.commit()


def main():
    with app.app_context():
        import_users()
        import_books()


if __name__ == "__main__":
    main()
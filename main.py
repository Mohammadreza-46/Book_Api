from flask import Flask
from app import books
from app import auth
from flask_jwt_extended import JWTManager
import os
from pathlib import Path
from app.check_data import check_data, check_data_nl
from app.extensions import db
from flask_migrate import Migrate

app = Flask(__name__)
books_bp = books.books_bp
auth_bp = auth.auth_bp
jwt_manager = JWTManager(app)

secret = os.environ.get('JWT_SECRET_KEY')

BASE_DIR = Path(__file__).resolve().parent
default_sqlite = f"sqlite:///{BASE_DIR / 'data' / 'database.db'}"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('kx%40jj5%2Fg', default_sqlite)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
migrate = Migrate(app, db)

if not secret or len(secret) < 32:
    raise RuntimeError('JWT_SECRET_KEY must be set and at least 32 characters')
app.config['JWT_SECRET_KEY'] = secret

app.register_blueprint(books_bp)
app.register_blueprint(auth_bp)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

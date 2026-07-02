from flask import Flask
from app import books
from app import auth
from flask_jwt_extended import JWTManager
import os
from app.check_data import check_data, check_data_nl
app = Flask(__name__)
books_bp = books.books_bp
auth_bp = auth.auth_bp
jwt_manager = JWTManager(app)

secret = os.environ.get('JWT_SECRET_KEY')

if not secret or len(secret) < 32:
    raise RuntimeError('JWT_SECRET_KEY must be set and at least 32 characters')
app.config['JWT_SECRET_KEY'] = secret

app.register_blueprint(books_bp)
app.register_blueprint(auth_bp)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

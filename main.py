from flask import Flask
from app import books
from app import auth
from flask_jwt_extended import JWTManager

app = Flask(__name__)
books_bp = books.books_bp
auth_bp = auth.auth_bp
jwt_manager = JWTManager(app)
app.config['JWT_SECRET_KEY'] = '123546578910'
if __name__ == '__main__':
    app.register_blueprint(books_bp)
    app.register_blueprint(auth_bp)
    app.run(debug=True, host='0.0.0.0', port=5000)
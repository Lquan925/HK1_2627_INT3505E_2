import os
from pathlib import Path
from flask import Flask
from models import db, Book, Author, Category, User, Review, BookAuthor

BASE_DIR = Path(__file__).resolve().parent

def create_app():
    app = Flask(__name__)

    # Cấu hình SQLite database tuyệt đối với đường dẫn posix chuẩn
    db_path = (BASE_DIR / 'books.db').as_posix()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Đăng ký blueprint
    from routes.books import books_bp
    app.register_blueprint(books_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
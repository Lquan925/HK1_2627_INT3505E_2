from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id', ondelete='CASCADE'), primary_key=True)
    role = db.Column(db.String(50), default='co')

    book = db.relationship('Book', back_populates='author_associations')
    author = db.relationship('Author', back_populates='book_associations')

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)

    books = db.relationship('Book', back_populates='category', lazy='dynamic')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug
        }

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, nullable=True)

    book_associations = db.relationship('BookAuthor', back_populates='author', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio
        }

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String(255), nullable=False)
    isbn = db.Column(db.String(13), nullable=False, unique=True)
    price_vnd = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', back_populates='books')

    author_associations = db.relationship('BookAuthor', back_populates='book', cascade='all, delete-orphan')

    reviews = db.relationship('Review', back_populates='book', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": f"book_{self.id}",
            "title": self.title,
            "isbn": self.isbn,
            "price_vnd": self.price_vnd,
            "stock": self.stock,
            "category": self.category.to_dict() if self.category else None,
            "authors": [{"id": assoc.author.id, "name": assoc.author.name, "role": assoc.role} for assoc in self.author_associations]
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.LargeBinary, nullable=False)  # Giữ bảo mật, không expose ra to_dict

    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": f"user_u_{self.id}",
            "displayName": self.display_name
        }

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # Từ 1 đến 5 sao
    comment = db.Column(db.Text, nullable=True)

    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    book = db.relationship('Book', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def to_dict(self):
        return {
            "id": self.id,
            "rating": self.rating,
            "comment": self.comment,
            "user": self.user.to_dict() if self.user else None
        }
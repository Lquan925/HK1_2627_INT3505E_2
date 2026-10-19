
from app import app 
from models import db, Category, Author, Book, User, Review, BookAuthor
import bcrypt

def seed_database():
    with app.app_context():
        print("Đang xóa dữ liệu cũ và tạo lại cấu trúc bảng...")
        db.drop_all()
        db.create_all()

        print("Đang thêm dữ liệu mẫu (Seeding)...")

        cat_tech = Category(name="Technology", slug="tech")
        cat_novel = Category(name="Novel", slug="novel")
        cat_science = Category(name="Science", slug="science")
        
        db.session.add_all([cat_tech, cat_novel, cat_science])
        db.session.commit()

        author_1 = Author(name="Robert C. Martin", bio="Author of Clean Code and agile software craftsmanship.")
        author_2 = Author(name="J.K. Rowling", bio="Author of the Harry Potter series.")
        author_3 = Author(name="Stephen Hawking", bio="Theoretical physicist and cosmologist.")
        
        db.session.add_all([author_1, author_2, author_3])
        db.session.commit()

        hashed_pw = bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt())
        user_1 = User(email="quan@uet.vnu.edu.vn", display_name="Lê Hồng Quân", password_hash=hashed_pw)
        user_2 = User(email="giang@gmail.com", display_name="Nguyễn Hương Giang", password_hash=hashed_pw)
        
        db.session.add_all([user_1, user_2])
        db.session.commit()

        books_data = [
            {"title": "Clean Code", "isbn": "9780132350884", "price_vnd": 450000, "stock": 15, "category": cat_tech},
            {"title": "The Pragmatic Programmer", "isbn": "9780201616224", "price_vnd": 520000, "stock": 8, "category": cat_tech},
            {"title": "Design Patterns", "isbn": "9780201633610", "price_vnd": 600000, "stock": 12, "category": cat_tech},
            {"title": "Harry Potter 1", "isbn": "9780747532699", "price_vnd": 250000, "stock": 30, "category": cat_novel},
            {"title": "Harry Potter 2", "isbn": "9780747538493", "price_vnd": 270000, "stock": 25, "category": cat_novel},
            {"title": "A Brief History of Time", "isbn": "9780553380163", "price_vnd": 320000, "stock": 10, "category": cat_science},
            {"title": "The Universe in a Nutshell", "isbn": "9780553802023", "price_vnd": 380000, "stock": 5, "category": cat_science},
            {"title": "Refactoring", "isbn": "9780134757599", "price_vnd": 580000, "stock": 14, "category": cat_tech},
            {"title": "Code Complete", "isbn": "9780735619678", "price_vnd": 550000, "stock": 20, "category": cat_tech},
            {"title": "Python Crash Course", "isbn": "9781593279288", "price_vnd": 420000, "stock": 25, "category": cat_tech},
        ]

        created_books = []
        for b_info in books_data:
            cat = b_info.pop("category")
            book = Book(**b_info, category_id=cat.id)
            db.session.add(book)
            created_books.append(book)
        db.session.commit()

        for book in created_books[:5]:
            assoc = BookAuthor(book_id=book.id, author_id=author_1.id, role="lead")
            db.session.add(assoc)
            
        for book in created_books[3:5]:
            assoc = BookAuthor(book_id=book.id, author_id=author_2.id, role="lead")
            db.session.add(assoc)

        for book in created_books[5:]:
            assoc = BookAuthor(book_id=book.id, author_id=author_3.id, role="lead")
            db.session.add(assoc)

        db.session.commit()

        review_1 = Review(rating=5, comment="Sách cực kỳ hay và bổ ích cho lập trình viên!", book_id=created_books[0].id, user_id=user_1.id)
        review_2 = Review(rating=4, comment="Đọc rất cuốn, giao hàng nhanh.", book_id=created_books[3].id, user_id=user_2.id)
        
        db.session.add_all([review_1, review_2])
        db.session.commit()

        print("✅ Đã seed dữ liệu mẫu thành công!")

if __name__ == "__main__":
    seed_database()
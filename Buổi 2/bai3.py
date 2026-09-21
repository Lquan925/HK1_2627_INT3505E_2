from flask import Flask, request, jsonify, make_response
app = Flask(__name__)
BOOKS = [
    {"id": 1, "title": "Mắt Biếc", "author": "Nguyễn Nhật Ánh"},
    {"id": 2, "title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "author": "Nguyễn Nhật Ánh"},
    {"id": 3, "title": "Cho Tôi Xin Một Vé Đi Tuổi Thơ", "author": "Nguyễn Nhật Ánh"},
    {"id": 4, "title": "Cô Gái Đến Từ Hôm Qua", "author": "Nguyễn Nhật Ánh"},
    {"id": 5, "title": "Harry Potter và Hòn Đá Phù Thủy", "author": "J.K. Rowling"},
    {"id": 6, "title": "Harry Potter và Phòng Chứa Bí Mật", "author": "J.K. Rowling"},
    {"id": 7, "title": "Harry Potter và Tên Tù Nhân Ngục Azkaban", "author": "J.K. Rowling"},
    {"id": 8, "title": "Nhà Giả Kim", "author": "Paulo Coelho"},
    {"id": 9, "title": "Đắc Nhân Tâm", "author": "Dale Carnegie"},
    {"id": 10, "title": "Tuổi Trẻ Đáng Giá Bao Nhiêu", "author": "Rosie Nguyễn"},
    {"id": 11, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài"},
    {"id": 12, "title": "Chí Phèo", "author": "Nam Cao"},
    {"id": 13, "title": "Lão Hạc", "author": "Nam Cao"},
    {"id": 14, "title": "Số Đỏ", "author": "Vũ Trọng Phụng"},
    {"id": 15, "title": "Lược Sử Loài Người", "author": "Yuval Noah Harari"},
    {"id": 16, "title": "1984", "author": "George Orwell"},
    {"id": 17, "title": "Trại Súc Vật", "author": "George Orwell"},
    {"id": 18, "title": "Bắt Trẻ Đồng Xanh", "author": "J.D. Salinger"},
    {"id": 19, "title": "Tội Ác Và Hình Phạt", "author": "Fyodor Dostoevsky"},
    {"id": 20, "title": "Không Gia Đình", "author": "Hector Malot"},
    {"id": 21, "title": "Hai Vạn Dặm Dưới Đáy Biển", "author": "Jules Verne"},
    {"id": 22, "title": "Hành Trình Vào Tâm Trái Đất", "author": "Jules Verne"},
    {"id": 23, "title": "Hoàng Tử Bé", "author": "Antoine de Saint-Exupéry"},
    {"id": 24, "title": "Bố Già", "author": "Mario Puzo"},
    {"id": 25, "title": "Suối Nguồn", "author": "Ayn Rand"}
]
DEFAULT_SIZE, MAX_SIZE = 20, 100
@app.get('/books')
def list_books():
    try:
        arg = request.args
        page = int(arg.get("page", 1))
        size = int(arg.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400
    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)

    flt = BOOKS
    author = arg.get("author")
    word = arg.get("word")
    if author:
        array = []
        for book in flt:
            if book.get("author").lower() == author.lower():
                array.append(book)
        flt = array
    if word:
        array = []
        for book in flt:
            if word.lower() in book.get("title").lower():
                array.append(book)
        flt = array

    start = (page - 1) * size
    end = start + size
    items = flt[start:end]
    total = len(flt)
    last = (total + size - 1) // size

    def u(page):
        return f"/books?page={page}&size={size}"
    links = {
        "self":{"href":u(page)},
        "first":{"href": u(1)},
        "last": {"href": u(last)}
    }
    if (page > 1):
        links["prev"] = {"href":u(page - 1)}
    if (end < total):
        links["next"] = {"href":u(page + 1)}
    body = {
        "data":items,
        "pagination":{
            "page":page,
            "size":size,
            "total":total,
            "total_pages":last,
            "links":links
        }
    }
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"]="public, max-age=30"
    return resp
if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 5000, debug = True)
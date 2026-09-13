from flask import Flask, jsonify, request
app = Flask(__name__)
books = [
    {"id": "1", "title" : "book 1"},
    {"id": "2", "title" : "book 2"},
    {"id": "3", "title" : "book 3"},
    {"id": "4", "title" : "book 4"}
]
def find_by_id(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None
@app.route("/book/<book_id>", methods = ["GET"])
def get_book(book_id):
    book = find_by_id(book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book),200
@app.route("/books", methods = ["GET"])
def get_list_book():
    limit = request.args.get("limit", 20)
    word = request.args.get("word", "")
    word = word.strip().lower()
    selected_books = []
    for book in books:
        title = book["title"].strip().lower()
        if word in title:
            selected_books.append(book)
    return jsonify({"item": selected_books}), 200
@app.route("/items/<int:item_id>", methods = ["GET"])
def get_item(item_id):
    return jsonify({"item_id": item_id}), 200
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
from flask import Flask, request, jsonify, make_response
app = Flask(__name__)

BOOKS = [
    {"id": 1, "title": "book1", "author": "author1"}
]
def find_index_book(bid):
    for index, book in enumerate(BOOKS):
        if book['id'] == bid:
            return index
    return -1

@app.get('/books/<int:bid>')
def fetch(bid):
    index = find_index_book(bid)
    if index == -1:
        return jsonify({'error': 'not found'}), 404
    resp = make_response(jsonify(BOOKS[index]), 200)
    resp.headers["Cache-Control"] = "max-age=60"
    return resp

@app.put('/books/<int:bid>')
def put(bid):
    index = find_index_book(bid)
    if index == -1:
        return jsonify({'error': 'not found'}), 404
    p = request.get_json()
    title = p.get('title')
    author = p.get('author')
    if not title or not author:
        return jsonify({'error': 'need title and author'}), 422
    BOOKS[index] = {'id': bid, 'title': title, 'author': author, "isbn" : p.get('isbn'), "price" : p.get('price')}
    return jsonify(BOOKS[index]), 200
@app.patch('/books/<int:bid>')
def patch(bid):
    index = find_index_book(bid)
    if index == -1:
        return jsonify({'error': 'not found'}), 404
    p = request.get_json()
    if p.get("price", 0) < 0:
        return jsonify(error="price must be positive"), 422
    for word in "title author isbn price".split():
        if word in p:
            BOOKS[index][word] = p.get(word)
    return jsonify(BOOKS[index]), 200
@app.delete('/books/<int:bid>')
def delete(bid):
    index = find_index_book(bid)
    if index == -1:
        return jsonify({'error': 'not found'}), 404
    BOOKS.pop(index)
    return jsonify({'message': 'deleted'}), 200
if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 5000, debug = True)
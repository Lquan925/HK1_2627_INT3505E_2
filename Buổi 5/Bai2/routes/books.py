import base64
import json
from flask import Blueprint, request, jsonify
from sqlalchemy import asc, desc, tuple_
from models import db, Book, Author, Category, User, Review, BookAuthor

books_bp = Blueprint('books', __name__)

# Cac truong duoc phep sort
SORTABLE_FIELDS = {
    'id':        Book.id,
    'title':     Book.title,
    'price_vnd': Book.price_vnd,
    'stock':     Book.stock,
    'isbn':      Book.isbn,
}

def encode_cursor(data: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

def decode_cursor(cursor_str: str):
    try:
        return json.loads(base64.urlsafe_b64decode(cursor_str.encode()).decode())
    except Exception:
        return None

def parse_sort_clauses(sort_param: str, order_param: str):
    keys   = [k.strip() for k in sort_param.split(',') if k.strip()]
    orders = [o.strip().lower() for o in order_param.split(',') if o.strip()]
    clauses  = []
    col_list = []
    for i, key in enumerate(keys):
        col = SORTABLE_FIELDS.get(key)
        if col is None:
            continue
        direction = orders[i] if i < len(orders) else (orders[-1] if orders else 'asc')
        clauses.append(desc(col) if direction == 'desc' else asc(col))
        col_list.append(key)
    if 'id' not in col_list:
        clauses.append(asc(Book.id))
    return clauses, col_list


@books_bp.route('/books', methods=['GET'])
def list_books():
    strategy    = request.args.get('strategy', 'offset').lower()
    genre       = request.args.get('genre')
    sort_param  = request.args.get('sort', 'id')
    order_param = request.args.get('order', 'asc')
    try:
        limit = max(1, min(int(request.args.get('limit', 10)), 100))
    except ValueError:
        return jsonify({"error": "limit phai la so nguyen"}), 400

    order_clauses, sort_keys = parse_sort_clauses(sort_param, order_param)

    query = db.session.query(Book).join(
        Category, Book.category_id == Category.id, isouter=True
    )
    if genre:
        query = query.filter(Category.slug == genre)

    if strategy == 'cursor':
        return _cursor_pagination(query, order_clauses, sort_keys, limit)
    else:
        return _offset_pagination(query, order_clauses, limit)


def _offset_pagination(query, order_clauses, limit):
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        return jsonify({"error": "page phai la so nguyen"}), 400

    total       = query.count()
    total_pages = max(1, (total + limit - 1) // limit)
    books       = query.order_by(*order_clauses).offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        "strategy":   "offset",
        "data":       [b.to_dict() for b in books],
        "pagination": {
            "total":       total,
            "page":        page,
            "limit":       limit,
            "total_pages": total_pages,
            "has_prev":    page > 1,
            "has_next":    page < total_pages,
        }
    })


def _cursor_pagination(query, order_clauses, sort_keys, limit):
    cursor_str = request.args.get('cursor')
    if cursor_str:
        cursor_data = decode_cursor(cursor_str)
        if cursor_data is None:
            return jsonify({"error": "cursor khong hop le"}), 400

        sort_cols = [SORTABLE_FIELDS[k] for k in sort_keys if k in SORTABLE_FIELDS]
        sort_vals = [cursor_data.get(k) for k in sort_keys if k in SORTABLE_FIELDS]
        last_id   = cursor_data.get('id')

        if sort_cols and all(v is not None for v in sort_vals) and last_id is not None:
            sort_cols.append(Book.id)
            sort_vals.append(last_id)
            query = query.filter(tuple_(*sort_cols) > tuple(sort_vals))
        elif last_id is not None:
            query = query.filter(Book.id > last_id)

    books    = query.order_by(*order_clauses).limit(limit + 1).all()
    has_more = len(books) > limit
    if has_more:
        books = books[:limit]

    next_cursor = None
    if has_more and books:
        last = books[-1]
        next_cursor = encode_cursor({
            'id':        last.id,
            'title':     last.title,
            'price_vnd': last.price_vnd,
            'stock':     last.stock,
        })

    return jsonify({
        "strategy":   "cursor",
        "data":       [b.to_dict() for b in books],
        "pagination": {
            "next_cursor": next_cursor,
            "has_more":    has_more,
            "limit":       limit,
        }
    })


@books_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if book is None:
        return jsonify({"error": f"Khong tim thay sach id={book_id}"}), 404
    return jsonify(book.to_dict())

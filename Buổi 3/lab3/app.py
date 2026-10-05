import base64
import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_, desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    customer_id = db.Column(db.Integer)
    total = db.Column(db.Float)
    created_at = db.Column(db.String(50)) 

def decode_cursor(cursor_str):
    try:
        decoded_bytes = base64.urlsafe_b64decode(cursor_str)
        return json.loads(decoded_bytes.decode('utf-8'))
    except Exception:
        return None

def encode_cursor(order):
    cursor_dict = {"id": order.id, "created_at": order.created_at}
    cursor_json = json.dumps(cursor_dict)
    return base64.urlsafe_b64encode(cursor_json.encode('utf-8')).decode('utf-8')

@app.route('/orders', methods=['GET'])
def get_orders():
    query = Order.query

    status = request.args.get('status')
    if status:
        query = query.filter(Order.status == status)
        
    customer_id = request.args.get('customer_id', type=int)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)

    cursor = request.args.get('cursor')
    if cursor:
        cursor_data = decode_cursor(cursor)
        if not cursor_data:
            return jsonify({"error": "Invalid cursor format"}), 400
        
        c_time = cursor_data.get("created_at")
        c_id = cursor_data.get("id")
        
        query = query.filter(or_(
            Order.created_at < c_time,
            and_(Order.created_at == c_time, Order.id < c_id)
        ))

    query = query.order_by(desc(Order.created_at), desc(Order.id))

    limit = request.args.get('limit', 10, type=int)
    orders = query.limit(limit + 1).all()
    
    has_next = len(orders) > limit
    if has_next:
        orders = orders[:limit]
        next_cursor = encode_cursor(orders[-1])
    else:
        next_cursor = None

    fields_arg = request.args.get('fields')
    valid_fields = ['id', 'status', 'customer_id', 'total', 'created_at']
    fields = fields_arg.split(',') if fields_arg else valid_fields

    result = []
    for o in orders:
        order_data = {}
        for f in fields:
            if hasattr(o, f) and f in valid_fields:
                order_data[f] = getattr(o, f)
        result.append(order_data)

    return jsonify({
        "data": result,
        "next_cursor": next_cursor
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Order.query.first():
            sample_orders = [
                Order(id=1, status='pending', customer_id=1, total=100.0, created_at='2024-01-01T10:00:00'),
                Order(id=2, status='shipped', customer_id=1, total=200.0, created_at='2024-01-02T10:00:00'),
                Order(id=3, status='pending', customer_id=2, total=150.0, created_at='2024-01-02T10:00:00'),
                Order(id=4, status='delivered', customer_id=2, total=300.0, created_at='2024-01-03T10:00:00'),
                Order(id=5, status='pending', customer_id=3, total=50.0, created_at='2024-01-04T10:00:00'),
                Order(id=6, status='shipped', customer_id=1, total=120.0, created_at='2024-01-05T10:00:00'),
                Order(id=7, status='delivered', customer_id=3, total=80.0, created_at='2024-01-06T10:00:00'),
                Order(id=8, status='pending', customer_id=2, total=220.0, created_at='2024-01-07T10:00:00'),
                Order(id=9, status='shipped', customer_id=1, total=90.0, created_at='2024-01-08T10:00:00'),
                Order(id=10, status='pending', customer_id=3, total=175.0, created_at='2024-01-09T10:00:00'),
                Order(id=11, status='delivered', customer_id=2, total=60.0, created_at='2024-01-10T10:00:00'),
                Order(id=12, status='pending', customer_id=1, total=310.0, created_at='2024-01-11T10:00:00'),
                Order(id=13, status='shipped', customer_id=3, total=140.0, created_at='2024-01-12T10:00:00'),
                Order(id=14, status='delivered', customer_id=2, total=250.0, created_at='2024-01-13T10:00:00'),
                Order(id=15, status='pending', customer_id=1, total=400.0, created_at='2024-01-14T10:00:00'),
            ]
            db.session.add_all(sample_orders)
            db.session.commit()
    app.run(debug=True, port=5000)
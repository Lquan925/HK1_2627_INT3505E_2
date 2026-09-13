from flask import Flask, jsonify
app = Flask(__name__)
ORDERS = [
    {"id": "1", "status" : "Delivered"},
    {"id": "2", "status" : "Pending"},
    {"id": "3", "status" : "Shipped"}
]
def get(order_id):
    for order in ORDERS:
        if order["id"] == order_id:
            return order
    return None
@app.route("/orders/<order_id>", methods = ["DELETE"])
def delete_order(order_id):
    order = get(order_id)
    if not order:
        return jsonify({"error": "not found"}), 404
    if order["status"] == "Delivered" or order["status"] == "Shipped":
        return jsonify({"error": "Cannot delete"}), 400
    ORDERS.remove(order)
    return jsonify({"message": "Deleted"}), 200
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
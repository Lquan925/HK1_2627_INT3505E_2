from flask import Flask, jsonify, request

app = Flask(__name__)

posts = [
    {"id": 1, "title": "Post1", "author_id": 1, "tags": ["hello", "world"]},
    {"id": 2, "title": "Post2", "author_id": 2, "tags": ["flask", "api"]}
]

@app.route('/api/v1/posts', methods=['POST'])
def create_post():
    """Tạo một bài viết mới (Collection)"""
    data = request.get_json()
    
    if not data or not data.get("title") or not data.get("content"):
        return jsonify({"message": "Thiếu thông tin title hoặc content"}), 400
        
    new_post = {
        "id": len(posts) + 1,
        "title": data.get("title"),
        "content": data.get("content"),
        "author_id": data.get("author_id", 1),
        "tags": data.get("tags", [])
    }
    posts.append(new_post)
    return jsonify(new_post), 201

@app.route('/api/v1/posts/<int:post_id>/comments', methods=['POST'])
def create_post_comment(post_id):
    data = request.get_json()
    if not data or not data.get("content"):
        return jsonify({"message": "Nội dung bình luận không được để trống"}), 400
        
    new_comment = {
        "id": 3,
        "post_id": post_id,
        "content": data.get("content"),
        "user_id": data.get("user_id", 1)
    }
    return jsonify(new_comment), 201

if __name__ == '__main__':
    app.run(debug=True)

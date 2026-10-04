from flask import Flask, jsonify, request

app = Flask(__name__)

posts = [
    {"id": 1, "title": "Post1", "author_id": 1, "tags": ["hello", "world"]},
    {"id": 2, "title": "Post2", "author_id": 2, "tags": ["flask", "api"]}
]

comments = [
    {"id": 1, "post_id": 1, "content": "Bài viết rất hay!", "user_id": 2},
    {"id": 2, "post_id": 1, "content": "Cảm ơn bạn chia sẻ.", "user_id": 3}
]

users = [
    {"id": 1, "username": "user1", "name": "Nguyễn Văn A", "following": [2]},
    {"id": 2, "username": "user2", "name": "Trần Thị B", "following": []},
    {"id": 3, "username": "user3", "name": "Lê Văn C", "following": [1, 2]}
]

@app.route('/api/v1/posts', methods=['POST'])
def create_post():
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
        
    post_exists = any(p["id"] == post_id for p in posts)
    if not post_exists:
        return jsonify({"message": "Không tìm thấy bài viết"}), 404

    new_comment = {
        "id": len(comments) + 1,
        "post_id": post_id,
        "content": data.get("content"),
        "user_id": data.get("user_id", 1)
    }
    comments.append(new_comment)
    return jsonify(new_comment), 201

@app.route('/api/v1/users/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    data = request.get_json()
    target_id = data.get("target_id") if data else None
    
    if not target_id:
        return jsonify({"message": "Thiếu thông tin 'target_id' của người muốn follow"}), 400
        
    user = next((u for u in users if u["id"] == user_id), None)
    target_user = next((u for u in users if u["id"] == target_id), None)
    
    if not user or not target_user:
        return jsonify({"message": "Không tìm thấy user thực hiện hoặc user được follow"}), 404
        
    if target_id == user_id:
        return jsonify({"message": "Không thể tự follow chính mình"}), 400
        
    if target_id not in user["following"]:
        user["following"].append(target_id)
        
    return jsonify({"message": f"User {user_id} đã follow user {target_id} thành công", "following": user["following"]}), 200

if __name__ == '__main__':
    app.run(debug=True)

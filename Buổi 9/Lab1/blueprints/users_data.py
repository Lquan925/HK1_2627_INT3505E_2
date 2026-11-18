from threading import Lock

_lock = Lock()

USERS = {
    1: {"first_name": "Văn", "last_name": "Nguyễn", "email": "a@vnu.vn"},
    2: {"first_name": "Trang", "last_name": "Trần", "email": "b@vnu.vn"},
}


def get_user(uid):
    return USERS.get(uid)


def create_user(data):
    with _lock:
        uid = max(USERS, default=0) + 1
        USERS[uid] = data.copy()
    return {"id": uid, **data}

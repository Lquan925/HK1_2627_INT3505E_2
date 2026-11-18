# User API v1 và v2

Nhấp đúp `run.bat` để tạo môi trường ảo, cài Flask và chạy ứng dụng.
Lần đầu cần kết nối Internet để tải Flask. Máy cần cài Python 3.10 trở lên.

Mở các URL sau:

- http://127.0.0.1:5000/api/v1/users/1 — trả về full_name.
- http://127.0.0.1:5000/api/v2/users/1 — trả về first_name và last_name.
- http://127.0.0.1:5000/api/v2/users/999 — trả về lỗi 404.

Dữ liệu dùng chung nằm trong `blueprints/users_data.py`.
Nhấn Ctrl+C trong cửa sổ chạy để dừng server.

Chạy thủ công trong PowerShell tại thư mục Lab1:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

## Phần mở rộng

### Tạo user bằng v2

Mở PowerShell và chạy (giữ cửa sổ server đang chạy):

```powershell
$body = @{ first_name = "An"; last_name = "Lê"; email = "an@vnu.vn" } | ConvertTo-Json
$result = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/v2/users" -Method Post -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) -UseBasicParsing
$result.StatusCode
$result.Headers["Location"]
$result.Content
```

Kết quả: HTTP 201, ID tự tăng (lần đầu là 3), header Location chỉ tới user mới.
Mở /api/v2/users/3 và /api/v1/users/3 để xem cùng user qua hai schema.
Body phải có đúng ba trường first_name, last_name, email là chuỗi không rỗng.
JSON sai trả 400; Content-Type không phải JSON trả 415.
Dữ liệu chỉ lưu trong RAM: khởi động lại hoặc Flask tự reload sẽ mất user vừa tạo.

### OpenAPI

Mở http://127.0.0.1:5000/openapi.yaml để đọc hoặc nhập URL này vào công cụ hỗ trợ OpenAPI.
File openapi.yaml mô tả hai GET, POST v2, schema, mã lỗi, Location và Sunset.

### Sunset cho v1

```powershell
curl.exe -i http://127.0.0.1:5000/api/v1/users/1
```

Response có header `Sunset: Fri, 31 Dec 2027 23:59:59 GMT`.
Đây là ngày ngừng hỗ trợ minh họa, cấu hình tại V1_SUNSET trong app.py.
Header thông báo kế hoạch; ứng dụng không tự tắt v1 khi đến ngày này.
Các response v2 không gắn Sunset.

Đây là server phát triển dùng cho bài tập.

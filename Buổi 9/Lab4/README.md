# Lab4: Blue-Green routing theo cohort

Cùng URL `POST /orders`, gateway chọn handler theo thứ tự:

1. Header `X-Cohort: beta` hoặc `internal` → v2.
2. `account_id` thuộc `acct_42`, `acct_99` → v2.
3. Tài khoản khác: `MD5(account_id) % 100 < V2_PERCENT` → v2, còn lại v1.

Mặc định rollout 5%. Hash giúp cùng tài khoản luôn vào cùng bucket, không chọn ngẫu nhiên mỗi request. 5% là tỷ lệ bucket, không đảm bảo đúng 5 trên mỗi 100 request. Cohort và allow-list vẫn vào v2 khi phần trăm bằng 0.

## Chạy trong môi trường ảo

Dừng server lab trước bằng Ctrl+C để giải phóng cổng 5000. Trong PowerShell:

```powershell
cd "C:\Lquan925\Buổi 9\Lab4"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:V2_PERCENT = "5"
python app.py
```

Nếu bị chặn Activate.ps1, chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` rồi kích hoạt lại. Có thể chạy `.\run.bat` để tự tạo môi trường và khởi động.

## Test bằng PowerShell thứ hai

Dùng file JSON để curl.exe hoạt động ổn định cả trên Windows PowerShell 5.1. Terminal test không cần kích hoạt môi trường ảo.

```powershell
cd "C:\Lquan925\Buổi 9\Lab4"
'{"account_id":"ordinary"}' | Set-Content -Encoding Ascii "$env:TEMP\lab4-order.json"

# 1. Cohort beta → v2, HTTP 201
curl.exe -i -X POST http://127.0.0.1:5000/orders -H "Content-Type: application/json" -H "X-Cohort: beta" --data-binary "@$env:TEMP\lab4-order.json"

# 2. Account allow-list → v2, HTTP 201
'{"account_id":"acct_42"}' | Set-Content -Encoding Ascii "$env:TEMP\lab4-order.json"
curl.exe -i -X POST http://127.0.0.1:5000/orders -H "Content-Type: application/json" --data-binary "@$env:TEMP\lab4-order.json"

# 3. Account thường → hash quyết định ở mức 5%
'{"account_id":"ordinary"}' | Set-Content -Encoding Ascii "$env:TEMP\lab4-order.json"
curl.exe -i -X POST http://127.0.0.1:5000/orders -H "Content-Type: application/json" --data-binary "@$env:TEMP\lab4-order.json"
```

Xem `X-Order-Handler: v1` (HTTP 200) hoặc `v2` (HTTP 201). Gọi lặp lại account thường sẽ có cùng handler; `order_id` vẫn thay đổi vì mỗi request tạo một đơn mẫu mới.

## 4. Rollout 100%

Ở terminal server, Ctrl+C rồi chạy trong môi trường ảo đang kích hoạt:

```powershell
$env:V2_PERCENT = "100"
python app.py
```

Ở terminal test, gọi lại account thường bằng lệnh cuối bên trên. Kết quả phải là HTTP 201 và `X-Order-Handler: v2`. Biến môi trường được đọc khi khởi động, cần restart sau khi đổi.

## 5. Sunset v1 sau rollout

Theo bài: sau khi chạy 100% ổn định, theo dõi lỗi, độ trễ và kết quả đơn hàng trong 30 ngày rồi mới lưu trữ/xóa handler v1. Lab giữ v1 để thử rollback; không tự động xóa theo đồng hồ. Với 100%, mọi request hợp lệ đã đi v2 trên cùng URL, vì vậy không trả 410 cho `/orders`.

Rollback phần trăm: dừng server, đặt `$env:V2_PERCENT = "0"`, chạy lại. Account thường về v1; cohort và allow-list vẫn đi v2 theo thứ tự ưu tiên của đề.

## Test tự động

Trong terminal đã kích hoạt môi trường ảo, tại Lab4:

```powershell
python -m unittest -v
```

Kiểm tra cohort, allow-list, ranh giới bucket 4/5, tính ổn định, rollout 0/100 và dữ liệu không hợp lệ. Request phải gửi JSON object có `account_id` là chuỗi không rỗng. JSON sai cú pháp trả 400; thiếu Content-Type JSON trả 415 theo Flask.

`handlers.py` tạo dữ liệu minh họa, chưa lưu database. `gateway.py` ghi log handler được chọn. Cấu hình phần trăm qua biến môi trường thay cho dashboard; bài này chưa xây dashboard quản trị.

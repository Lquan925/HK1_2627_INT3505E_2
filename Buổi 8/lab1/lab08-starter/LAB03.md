# Lab 3 – Chạy Books API bằng Newman

## Chuẩn bị
Chạy các lệnh từ thư mục lab08-starter.
Máy cần có Python và Node.js/npm.

Nếu chưa có môi trường Python:
python -m venv .venv

Cài thư viện Python:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Cài Newman nếu chưa có:
npm.cmd install -g newman

## Terminal 1 – Chạy API Flask
New-Item -ItemType Directory -Force instance
.\.venv\Scripts\python.exe -m app --port 5000

Giữ terminal này mở. API chạy tại http://127.0.0.1:5000.

## Terminal 2 – Chạy collection
Mở PowerShell tại cùng thư mục lab08-starter, chạy:

New-Item -ItemType Directory -Force reports
newman.cmd run books-api.postman_collection.json -e postman/local.postman_environment.json -r "cli,junit" --reporter-junit-export reports/junit.xml

Không cần mở Postman UI. API Flask phải đang chạy.

## Nội dung kiểm thử
- 5 request thành công: liệt kê, tạo, đọc, cập nhật và xóa sách.
- 2 request lỗi: POST thiếu title và GET /books/9999.
- Mỗi request có 2 pm.test: kiểm tra status và response body.
- POST thành công lưu book_id bằng pm.collectionVariables.set.
- GET, PUT và DELETE dùng URL {{base_url}}/books/{{book_id}}.

## Kiểm tra báo cáo JUnit
Chạy trong PowerShell:

$report = [xml](Get-Content -Raw .\reports\junit.xml)
Write-Host "Số testcase:" $report.SelectNodes("//testcase").Count
Write-Host "Số failure:" $report.SelectNodes("//failure").Count

Yêu cầu: ít nhất 7 testcase, 0 failure và thời gian chạy Newman dưới 10 giây.

## Kết quả đã chạy
7 requests, 14 assertions, 0 lỗi, thời gian 702 ms.

File báo cáo: reports/junit.xml.

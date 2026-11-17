# Lab 4 — Load test Books API với Locust

## Các file nộp trên GitHub

- [Kịch bản Locust](performance/locustfile.py): có task tìm theo năm và xác suất lỗi giả lập 1%.
- [Phân tích kết quả](performance/analysis.md).
- Báo cáo: [A](reports/A.html), [B](reports/B.html), [C](reports/C.html). Tải file HTML về rồi mở bằng trình duyệt để xem giao diện.
- CSV `reports/A_*.csv`, `B_*.csv`, `C_*.csv` lưu số liệu đối chiếu.

## Tự chạy trên PowerShell

Từ thư mục `lab08-starter`, kích hoạt môi trường và chạy API ở terminal thứ nhất:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app --port 5000
```

Mở terminal thứ hai tại cùng thư mục:

```powershell
.\.venv\Scripts\Activate.ps1
python -m locust -f performance/locustfile.py
```

Vào http://localhost:8089, đặt Host là http://127.0.0.1:5000, thử 10 user với spawn rate 2. Bấm Start rồi Stop để quan sát Statistics, p95 và Failures. Nhấn Ctrl+C trong terminal thứ hai trước khi chạy các lệnh xuất báo cáo bên dưới.

Chạy lần lượt, đợi từng lệnh kết thúc:

```powershell
python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 10 -r 2 -t 30s --html reports/A.html --csv reports/A
python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 50 -r 5 -t 60s --html reports/B.html --csv reports/B
python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 200 -r 50 -t 30s --html reports/C.html --csv reports/C
```

Các lệnh ghi đè báo cáo hiện có và POST thêm sách vào database đang dùng. Cập nhật `performance/analysis.md` theo số liệu lần chạy của bạn. p95 và RPS lấy ở dòng Aggregated; failure rate = Failure Count / Request Count × 100%.

Muốn đo trên bản sao database, giữ dữ liệu gốc và khởi tạo cùng dữ liệu trước mỗi kịch bản:

```powershell
python -X utf8 performance/run_lab4.py
```

Runner dùng port 5054. Lỗi `Simulated HTTP 500 (client-side)` chỉ được đánh dấu bởi Locust, không phải HTTP 500 thật từ API. Với mẫu nhỏ, tỷ lệ quan sát có thể khác 1%. Đặt `$env:LAB_FAIL_RATE = "0"` khi cần tắt lỗi giả lập cho một lần chạy Locust trực tiếp.

## Đưa lên GitHub

Chạy từ `lab08-starter`. Chỉ stage các file của Lab 4:

```powershell
git add -- .gitignore LAB04.md performance/locustfile.py performance/analysis.md performance/run_lab4.py reports/A.html reports/B.html reports/C.html reports/A_*.csv reports/B_*.csv reports/C_*.csv
git diff --cached --stat
git commit -m "Complete Lab 4 Books API load tests with Locust"
git push origin HEAD
```

Nếu GitHub yêu cầu đăng nhập, hoàn thành đăng nhập bằng tài khoản của bạn. Các file môi trường ảo, cache, database và log cục bộ đã được loại khỏi Git bằng `.gitignore`.

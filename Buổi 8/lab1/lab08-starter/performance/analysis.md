# Lab 4 — Load test Books API với Locust

## Môi trường và cách chạy

Đo ngày 17/11/2026, Python 3.13.5, Locust 2.47.0, Flask development server và SQLite trên cùng máy Windows. Dùng `performance/locustfile.py`, chạy tuần tự A/B/C với host `http://127.0.0.1:5054`. Port 5054 chỉ để tách server đo khỏi server người dùng có thể đang chạy ở 5000. Không thay đổi code API.

`performance/run_lab4.py` khởi động server riêng và sao chép database gốc bằng SQLite backup trước mỗi kịch bản. Các lần chạy bắt đầu từ cùng dữ liệu; POST chỉ ghi vào `reports/lab4-test.db`, không ghi vào database gốc. Trong mỗi lần chạy, số sách vẫn tăng do POST.

Các task có trọng số: list=3, read=2, create=1, search_by_year=1. Mỗi user nghỉ ngẫu nhiên 1–3 giây giữa các task. Read chấp nhận 404 do chọn ID ngẫu nhiên theo quy ước của starter. Search chọn năm 2020–2024; kết quả rỗng vẫn là HTTP 200 hợp lệ. Mỗi search thành công có xác suất 1% bị đánh dấu `Simulated HTTP 500 (client-side)` bằng Locust. Đây là lỗi giả lập phía client, không phải server trả HTTP 500. Tỷ lệ quan sát không nhất thiết đúng 1% ở mẫu nhỏ. Tỷ lệ lỗi tổng kỳ vọng khoảng 0,143% do search có trọng số 1/7.

Chạy lại toàn bộ từ thư mục dự án:

```powershell
.\.venv\Scripts\python.exe -X utf8 performance/run_lab4.py
```

Hoặc khởi động API ở port 5000 rồi chạy từng lệnh sau, lần lượt:

```powershell
python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 10 -r 2 -t 30s --html reports/A.html --csv reports/A
python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 50 -r 5 -t 60s --html reports/B.html --csv reports/B
python -m locust -f performance/locustfile.py --headless -H http://127.0.0.1:5000 -u 200 -r 50 -t 30s --html reports/C.html --csv reports/C
```

## Kết quả thực đo

p95 và RPS lấy từ dòng Aggregated trong CSV tương ứng với ba báo cáo HTML. Failure rate = số lỗi / số request × 100%. Thời lượng cấu hình gồm cả giai đoạn tăng user; RPS do Locust tính theo khoảng thống kê thực tế.

| Kịch bản | Users | Spawn/s | Thời gian | Requests | Lỗi | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 135 | 0 | 43 | 0,000% | 4,66 |
| B | 50 | 5 | 60s | 1396 | 1 | 64 | 0,072% | 23,51 |
| C | 200 | 50 | 30s | 2679 | 7 | 200 | 0,261% | 95,35 |

### 1. Kịch bản nào có p95 cao nhất? Vì sao?

C cao nhất với 200 ms, so với B 64 ms và A 43 ms. Khi tăng từ 50 lên 200 user, p95 tăng khoảng 3,13 lần. p95 của POST tăng từ 87 lên 270 ms; list và read đều tăng lên 200 ms. Dữ liệu phù hợp với hiện tượng tranh chấp tài nguyên và tăng thời gian chờ khi nhiều request được xử lý đồng thời.

Dựa trên code, POST cần commit vào SQLite; SQLite giới hạn ghi đồng thời nên có thể gây chờ khóa. Flask development server, CPU, I/O và việc client/server cùng máy cũng có thể góp phần. Chưa có profiling hoặc số liệu pool/CPU để xác định nút thắt chính. Ba điểm đo này chưa đủ chứng minh một ngưỡng quá tải hoặc quy luật phi tuyến.

### 2. Endpoint nào có fail rate tăng theo số user?

| Endpoint | A: lỗi/requests | B: lỗi/requests | C: lỗi/requests |
|---|---:|---:|---:|
| GET /books | 0/61 (0%) | 0/569 (0%) | 0/1133 (0%) |
| GET /books/{id} | 0/34 (0%) | 0/406 (0%) | 0/798 (0%) |
| GET /books?year | 0/17 (0%) | 1/231 (0,433%) | 7/363 (1,928%) |
| POST /books | 0/23 (0%) | 0/190 (0%) | 0/385 (0%) |

Tỷ lệ lỗi search quan sát tăng từ A đến C, nhưng toàn bộ lỗi trong failures CSV là lỗi giả lập phía client. Code vẫn dùng xác suất cố định 1%; mẫu nhỏ và ngẫu nhiên giải thích sự dao động. Không có bằng chứng lỗi thật tăng theo số user trong lần đo này. Không thấy Traceback, OperationalError hoặc TimeoutError trong log server của ba lần chạy.

Không thể suy ra cứ tăng user thì xác suất giả lập tăng. Nếu những lần đo khác có lỗi POST thật, cần đối chiếu log SQLite locked, pool timeout hoặc lỗi kết nối; hiện tại đó chỉ là khả năng dựa trên code.

### 3. SLO p95 < 300 ms và baseline CI

Cả A (43 ms), B (64 ms), C (200 ms) đều đạt điều kiện p95 tổng < 300 ms trong lần đo này. Tất cả endpoint cũng có p95 dưới 300 ms, cao nhất là POST ở C: 270 ms. Đây là kết quả trên máy cục bộ với Flask/SQLite, không chứng minh production đạt SLO. Mỗi kịch bản mới chạy một lần và thời lượng ngắn; cần chạy lặp và đo lâu hơn trên môi trường giống production.

Đề xuất baseline CI ban đầu: A, 10 user, spawn rate 2/s, 30 giây, cùng dữ liệu khởi tạo và môi trường cố định. Gate: p95 tổng và từng endpoint < 300 ms, không có lỗi thật. Tắt lỗi giả lập bằng `$env:LAB_FAIL_RATE = "0"` trước khi chạy CI; giữ mặc định 0.01 cho bài lab. Quy ước chấp nhận 404 của starter cần được thống nhất khi áp dụng CI.

Locust có thể trả exit code khác 0 khi có failure. Với ngưỡng p95, bước CI riêng phải đọc cột 95% của stats CSV và trả exit code 1 nếu có dòng vượt hoặc bằng 300 ms; lệnh Locust mặc định không tự áp ngưỡng này. Lần đo hiện tại không chạy lại chế độ CI tắt lỗi giả lập.

## Bonus: pool giới hạn 5 với 200 user

Nếu tổng kết nối database thực sự giới hạn 5, tối đa 5 kết nối được mượn cùng lúc; các request cần DB khác phải chờ. Thời gian chờ làm p95 tăng, throughput có thể chững lại, và nếu quá pool_timeout thì có thể lỗi. 200 user Locust không có nghĩa 200 kết nối DB cùng lúc vì còn think time và request không giữ kết nối suốt phiên user.

Để xác nhận: chạy C trên cùng snapshot và môi trường với `SQLALCHEMY_ENGINE_OPTIONS` đặt `pool_size=5`, `max_overflow=0` và pool_timeout xác định, trước khi db.init_app. Chạy đối chứng với pool lớn hơn, giữ các tham số khác không đổi, lặp vài lần. Đối chiếu p95 từng endpoint, RPS, lỗi và log SQLAlchemy QueuePool timeout; bổ sung đo thời gian chờ lấy kết nối ở server. Nếu chưa gây đủ tranh chấp, thử giảm think time ở một kịch bản bổ sung và ghi rõ thay đổi.

Chỉ có p95 tăng trong Locust chưa đủ xác nhận pool là nguyên nhân: SQLite còn giới hạn ghi. Không đặt mỗi pool_size=5 rồi coi tổng là 5 vì max_overflow có thể cho phép thêm kết nối. Bài đo A/B/C hiện tại dùng cấu hình pool mặc định; phần bonus là phương án kiểm chứng, chưa phải kết quả một thí nghiệm pool=5.

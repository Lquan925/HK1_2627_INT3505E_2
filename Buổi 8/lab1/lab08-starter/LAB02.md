# Lab 2: Kiểm tra OpenAPI và response Flask

File `openapi.yaml` đã được sửa đủ ba lỗi: bổ sung `operationId` cho
`GET /books`, bỏ `content` khỏi response 204 của DELETE và sửa `Book.year`
thành kiểu `integer` (cho phép giá trị `null`).

Chạy các lệnh sau từ thư mục `lab08-starter`:

```sh
spectral lint openapi.yaml --ruleset .spectral.yml --fail-severity hint
python -m pytest -v -p no:cacheprovider
```

Trên Windows, dùng `spectral.cmd` nếu PowerShell chặn tệp lệnh của npm.
Kết quả kiểm tra đã được lưu trong `reports/spectral-lint.txt` và
`reports/lab02-verification.txt`.

Custom rule `response-200-nonempty-schema` yêu cầu response JSON có ít nhất
một trường được khai báo trong `properties`. Nếu response là mảng, schema của
phần tử phải là đối tượng có ít nhất một trường. Vì vậy, `GET /books` vẫn có
thể trả về mảng hợp lệ.

Spectral phân giải các tham chiếu cục bộ trước khi áp dụng rule, nên schema
tham chiếu đến `Book` cũng được kiểm tra. Rule phát hiện các trường hợp `{}`,
`{type: object}`, `properties` rỗng và phần tử mảng không khai báo trường.
Các custom rule còn lại phát hiện response 204 có `content` và `Book.year`
không được khai báo là `integer`.

Spectral chỉ kiểm tra đặc tả OpenAPI, không gọi API Flask. Vì vậy, đặc tả hợp lệ
vẫn có thể khác với dữ liệu thực tế mà Flask trả về. Contract test (kiểm thử
đối chiếu dữ liệu với đặc tả) dùng pytest và jsonschema để kiểm tra response
thực tế của các thao tác tạo, lấy, liệt kê và cập nhật sách theo schema `Book`
đọc từ `openapi.yaml`. Test cũng xác nhận DELETE trả về body rỗng.

Để kiểm tra đúng giá trị `null`, test chuyển `nullable` của OpenAPI 3.0 sang
kiểu `null` tương ứng trong JSON Schema. Các ràng buộc về trường bắt buộc,
kiểu dữ liệu và `additionalProperties` đều được áp dụng.

Ba test giả lập lỗi dùng `monkeypatch` để thay đổi dữ liệu Flask trả về:

- Trả `year` dưới dạng chuỗi thay vì số nguyên.
- Bỏ trường bắt buộc `title`.
- Thêm một trường không có trong schema.

Mỗi trường hợp phải phát sinh `ValidationError`. Các test này chứng minh
contract test phát hiện được response Flask sai ngay cả khi Spectral đã pass.

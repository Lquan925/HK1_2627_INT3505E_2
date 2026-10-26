1. Rủi ro BOLA / IDOR (Broken Object Level Authorization - OWASP API1:2023)
Mô tả điểm lộ: Endpoint GET /posts/{id} chỉ kiểm tra token hợp lệ và scope posts:read, nhưng thiếu kiểm tra quyền sở hữu đối tượng (Ownership Check). User A có thể sửa tham số {id} để đọc các bài viết ở chế độ riêng tư (Private) hoặc nháp (Draft) của User B.   

2. Rò rỉ thông tin qua phản hồi chi tiết lỗi Đăng nhập (User Enumeration - OWASP API2:2023)
Mô tả điểm lộ: Phản hồi từ POST /auth/login phân biệt chi tiết giữa "Email không tồn tại" và "Mật khẩu không đúng", hoặc thời gian xử lý (response time) khác nhau rõ rệt khi phát hiện email sai. Kẻ tấn công có thể lợi dụng điều này để dò quét (enumerate) danh sách email người dùng đã đăng ký hệ thống.   

3. Thiếu Rate-Limiting dẫn đến tấn công Brute-Force & Credential Stuffing (OWASP API2:2023)
Mô tả điểm lộ: Endpoint POST /auth/login không giới hạn số lượng request được gửi từ một địa chỉ IP hoặc account. Kẻ tấn công có thể chạy script thử hàng triệu mật khẩu công khai nhằm chiếm đoạt tài khoản.   

4. Rò rỉ thông tin cá nhân (PII) hoặc Hash Mật khẩu qua Payload JWT / Response (OWASP API3:2023)
Payload của JWT chỉ được mã hóa Base64URL, không phải mã hóa bảo mật. Nếu lưu các thông tin nhạy cảm như email, phone_number, role chi tiết, hoặc secret trong JWT Payload, kẻ tấn công có thể đọc dễ dàng.   
Endpoint trả về bài viết hoặc thông tin tài khoản chèn nguyên raw DB row (chứa password_hash, two_factor_secret) vào JSON response.   

5. Lưu trữ Token không an toàn phía Client dẫn đến XSS Token Theft (OWASP API5 / API8)
Mô tả điểm lộ: Ứng dụng client (React/Vue Single Page App) nhận Access & Refresh token qua JSON body ở POST /auth/login và lưu trữ chúng trực tiếp vào localStorage hoặc sessionStorage. Nếu trang web dính lỗi Cross-Site Scripting (XSS), mã độc JavaScript của kẻ tấn công có thể lấy trộm toàn bộ token bằng localStorage.getItem(...).   
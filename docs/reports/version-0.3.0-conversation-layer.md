# Báo cáo phiên bản v0.3.0 — Conversation Layer trước AI

**Ngày hoàn thành:** 22/06/2026  
**Loại phiên bản:** Minor feature  
**Phụ thuộc:** `v0.2.1`

## 1. Mục tiêu phiên bản

Xây dựng luồng hội thoại có persistence trước khi tích hợp AI Agent:

- Mỗi trình duyệt có một phiên chat riêng.
- Tin nhắn khách được lưu vào PostgreSQL.
- Phiên chat giữ ngữ cảnh phân khu nếu khách đang xem trang chi tiết.
- Sale có thể đọc và đóng/mở lại phiên từ Dashboard.
- Chat Widget chưa gọi LLM và không giả lập câu trả lời AI.

## 2. Công việc đã thực hiện

### 2.1. Public Conversation API

| Method | Endpoint | Chức năng |
|---|---|---|
| `POST` | `/api/v1/conversations` | Tạo phiên với UUID ngẫu nhiên |
| `GET` | `/api/v1/conversations/{session_id}/messages` | Lấy tin nhắn của phiên |
| `POST` | `/api/v1/conversations/{session_id}/messages` | Lưu tin nhắn khách |

Nội dung tin nhắn được giới hạn từ 1 đến 2.000 ký tự. Phiên đã đóng không nhận thêm tin nhắn.

### 2.2. Admin Conversation API

| Method | Endpoint | Chức năng |
|---|---|---|
| `GET` | `/api/v1/admin/conversations` | Danh sách phiên và số tin nhắn |
| `GET` | `/api/v1/admin/conversations/{id}` | Chi tiết toàn bộ tin nhắn |
| `PATCH` | `/api/v1/admin/conversations/{id}` | Đóng hoặc mở lại phiên |

Các API Admin được bảo vệ bằng JWT và RBAC.

### 2.3. Chat Widget

- Session ID lưu tại `localStorage` với key `ocean_park_chat_session`.
- Session chỉ được tạo khi khách gửi tin nhắn đầu tiên.
- Khi reload trang, Widget tải lại lịch sử của session.
- Nếu session không tồn tại hoặc đã đóng, Widget tạo session mới.
- Khi đang ở `/phan-khu/{slug}`, session tự gắn `subdivision_id` tương ứng.
- Phản hồi hiện tại chỉ xác nhận Sale đã nhận nội dung; không gọi AI.

### 2.4. Sales Dashboard

Route mới:

```text
/admin/conversations
```

Sale có thể:

- Xem danh sách phiên theo thời gian hoạt động gần nhất.
- Nhận biết phiên đang hoạt động hay đã đóng.
- Xem phân khu khách đang quan tâm.
- Đọc toàn bộ tin nhắn.
- Đóng hoặc mở lại phiên.

## 3. Phương án kỹ thuật

### 3.1. UUID cho public session

Không công khai ID tăng dần của Database. Client chỉ sử dụng UUID khó đoán để truy cập lịch sử session của chính nó.

### 3.2. Tạo session khi gửi tin đầu tiên

Không tạo bản ghi khi người dùng chỉ mở/đóng Widget. Cách này tránh tạo hàng loạt conversation rỗng.

### 3.3. Persistence trước AI

API chỉ lưu message với sender `customer`. Nội dung xác nhận trên Client không được ghi thành câu trả lời AI. Khi tích hợp Agent, Backend sẽ bổ sung message sender `ai` vào cùng cấu trúc hiện tại.

### 3.4. Không cần migration mới

Các bảng `conversations` và `messages` đã được chuẩn bị từ `v0.1.0`. Phiên bản này kích hoạt nghiệp vụ trên schema hiện có, không thay đổi Database schema.

## 4. Hướng dẫn sử dụng

### 4.1. Khách hàng

1. Mở website tại `http://localhost:3000`.
2. Nhấn nút **Chat** ở góc phải.
3. Nhập nhu cầu và gửi.
4. Widget hiển thị xác nhận đã ghi nhận.
5. Có thể reload trang và tiếp tục cùng session.

### 4.2. Sale

1. Đăng nhập `http://localhost:3000/admin/login`.
2. Chọn menu **Hội thoại**.
3. Chọn một phiên để đọc nội dung.
4. Nhấn **Đóng phiên** khi đã xử lý xong.

## 5. Hướng dẫn kiểm thử

### 5.1. Backend tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Kết quả phiên bản: **15 tests passed**.

Conversation lifecycle test bao gồm:

1. Tạo session.
2. Gửi customer message.
3. Kiểm tra Admin list có `message_count = 1`.
4. Đọc nội dung chi tiết.
5. Đóng session.

### 5.2. Lint

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests migrations
```

Kết quả mong đợi: `All checks passed!`.

### 5.3. Frontend build

```powershell
cd FE
npm run build
```

Build phải có route `/admin/conversations`.

### 5.4. Test API thủ công

```powershell
$session = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/conversations" `
  -ContentType "application/json" `
  -Body '{"subdivision_slug":"the-zenpark"}'

$body = @{ content = "Tôi muốn tìm căn 2PN" } | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/conversations/$($session.session_id)/messages" `
  -ContentType "application/json" `
  -Body $body
```

### 5.5. Test UI thủ công

1. Mở trang chi tiết The Zenpark.
2. Gửi tin nhắn trong Widget.
3. Xác nhận thông báo đã ghi nhận xuất hiện.
4. Reload trang và xác nhận tin nhắn cũ vẫn hiển thị.
5. Mở Dashboard → Hội thoại.
6. Xác nhận session có nhãn The Zenpark và đúng nội dung.
7. Đóng session, sau đó gửi tin mới ở Client.
8. Xác nhận Client tự tạo session mới.1

## 6. Kết quả xác minh

- Backend: 15 tests passed.
- Ruff: All checks passed.
- Next.js `0.3.0` production build thành công với route hội thoại mới.
- Không thay đổi migration hoặc làm mất dữ liệu phiên bản trước.
- Docker end-to-end test đã tạo session, lưu message, đọc lại qua Admin API và đóng session thành công.
- Backend, Frontend và PostgreSQL đều healthy; `/admin/conversations` trả HTTP 200.

## 7. Giới hạn và phiên bản tiếp theo

- Chưa có streaming response.
- Chưa gắn conversation vào Lead sau khi khách gửi số điện thoại.
- Chưa có rate limiting cho chat.
- Chưa có AI message hoặc RAG retrieval.

Phiên bản tiếp theo nên liên kết Conversation → Lead và bổ sung các guardrail cần thiết trước khi tích hợp Agent.

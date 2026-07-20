# Version 0.9.0 - Agent chat stabilization

Ngày thực hiện: 2026-06-26

## Mục tiêu

Sửa lỗi AI chat trả HTTP 500 khi người dùng bấm chat trên môi trường staging/VPS, đồng thời đồng bộ lịch sử hội thoại AI với phần dashboard/admin hiện tại.

## Hiện trạng trước khi sửa

Sau khi merge phần Agent từ member khác, route `POST /agent/chat` dùng một lớp database/model riêng:

- `src.database.get_session`
- `src.models.chat.Conversation`
- `src.models.chat.Message`
- field tin nhắn là `role`

Trong khi database runtime/dashboard hiện tại đang dùng schema chính:

- `src.db.session.get_db`
- `src.models.entities.Conversation`
- `src.models.entities.Message`
- field tin nhắn là `sender`

Vì vậy trên staging, route chat có nguy cơ query vào các cột không tồn tại như `messages.role`, `conversations.last_intent`, `conversations.daily_usage_count`, dẫn đến HTTP 500.

## Công việc đã thực hiện

### 1. Refactor `POST /agent/chat`

File thay đổi: `src/api/agent_routes.py`

Đã chuyển route chat sang dùng schema chính của app:

- dùng `Session = Depends(get_db)` thay vì async session cũ;
- dùng `src.models.entities.Conversation` và `src.models.entities.Message`;
- lưu tin nhắn khách với `sender="customer"`;
- lưu tin nhắn AI với `sender="ai"`;
- cập nhật `conversation.last_message_at` để dashboard/admin thấy hội thoại mới nhất;
- giữ lại rate limit 5 tin/phút và quota 100 tin/ngày, nhưng đổi điều kiện đếm từ `role="user"` sang `sender="customer"`;
- thêm mapper `sender -> role` để LangGraph Agent vẫn nhận input dạng:

```json
{"role": "user", "content": "..."}
```

### 2. Đồng bộ lead session migration

File thay đổi: `src/api/lead_routes.py`

Route `POST /api/v1/leads` trước đây cũng đọc lịch sử chat từ model cũ. Đã bổ sung helper đọc lịch sử từ schema chính:

- tìm `Conversation` theo `session_id`;
- đọc `Message` theo `conversation_id`;
- map `sender="customer"` thành `role="user"`;
- map `sender="ai"` thành `role="assistant"`;
- lưu lịch sử chat đó vào lead khi khách để lại thông tin.

Kết quả: khi khách chat trước rồi để lại thông tin sau, admin xem lead sẽ thấy lại lịch sử chat liên quan.

### 3. Cập nhật test fixture

File thay đổi: `tests/conftest.py`

Test client trong pytest không tự chạy đầy đủ lifespan startup, nên database sync test chưa được tạo bảng. Đã thêm `init_database()` vào fixture `client` để test phản ánh đúng schema runtime hiện tại.

## Kết quả kiểm tra

Đã chạy các lệnh sau:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_api\test_routes.py tests\test_e2e\test_user_journeys.py tests\test_failure\test_graceful_degradation.py
```

Kết quả:

```text
33 passed
```

```powershell
.\.venv\Scripts\ruff.exe check src tests
```

Kết quả:

```text
All checks passed!
```

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Kết quả:

```text
141 passed
```

```powershell
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
```

## Cách test thủ công sau khi deploy staging

Sau khi push code và GitHub Actions build/publish image mới thành công, SSH vào VPS và chạy:

```bash
cd /opt/ocean-park-advisor
git pull origin dev
bash scripts/deploy/staging_deploy.sh
```

Kiểm tra backend:

```bash
curl http://103.149.87.83:8000/ready
curl http://103.149.87.83:8000/agent/status
```

Kiểm tra chat:

```bash
curl -X POST http://103.149.87.83:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "manual-test-0-9-0",
    "messages": [
      {
        "role": "user",
        "content": "Tôi có khoảng 3 tỷ, muốn tìm căn 2PN để ở thật"
      }
    ]
  }'
```

Kỳ vọng:

- HTTP 200;
- response có `response`;
- không còn HTTP 500;
- response trả lại đúng `session_id`.

Kiểm tra lead migration:

```bash
curl -X POST http://103.149.87.83:8000/api/v1/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manual Test 0.9.0",
    "phone": "0912345678",
    "session_id": "manual-test-0-9-0",
    "chat_history": [],
    "user_profile": {
      "budget": 3000000000,
      "unit_type": "2PN",
      "purpose": "ở thật"
    }
  }'
```

Sau đó vào dashboard admin để kiểm tra lead mới có lịch sử chat đi kèm.

## Lưu ý còn lại

Phần `/api/v1/leads` vẫn đang dùng model lead async cũ để lưu lead AI. Thay đổi lần này chỉ nối lại phần chat history để hết lỗi 500 và không mất lịch sử hội thoại. Ở phase tiếp theo nên hợp nhất hoàn toàn model lead/contact/dashboard để tránh còn hai lớp database tồn tại song song.

## Kết luận

Version 0.9.0 đã xử lý nút thắt chính khiến AI chat lỗi 500 do lệch schema. Chat route hiện đã dùng cùng schema với dashboard/conversation hiện tại, lead có thể lấy lại lịch sử chat theo `session_id`, và toàn bộ backend/frontend test hiện tại đều pass.

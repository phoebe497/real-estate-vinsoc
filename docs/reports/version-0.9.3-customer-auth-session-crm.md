# Version 0.9.3 — Customer Auth, Guest Ephemeral Chat, Multi-session CRM

Ngày thực hiện: 2026-06-27

## Mục tiêu

Triển khai kế hoạch đã duyệt:

- Customer đăng ký/đăng nhập bằng họ tên, số điện thoại, mật khẩu.
- Guest/vãng lai được chat thử nhưng không lưu `conversations/messages` vào database.
- Customer đã đăng nhập mới lưu phiên chat vào database.
- Logout customer chỉ xóa token/session/messages trên browser, không xóa database.
- Một customer có nhiều phiên chat.
- Admin/sale xem chat theo luồng: khách hàng/lead -> phiên chat -> messages.
- Sale không thấy menu “Nhân sự”.
- Admin khóa/mở tài khoản nội bộ thay vì hard delete.

## Công việc đã làm

### 1. Database/schema

Files:

- `src/models/entities.py`
- `migrations/versions/20260627_03_customer_accounts_sessions.py`
- `src/db/session.py`

Thay đổi:

- Thêm bảng `customer_accounts`.
- Thêm `leads.customer_account_id`.
- Thêm `conversations.customer_account_id`.
- Thêm Alembic migration `20260627_03`.
- Thêm compatibility nhẹ cho local/test DB cũ: nếu SQLite local đã tồn tại nhưng thiếu cột mới thì tự `ALTER TABLE ADD COLUMN`.

Schema mới đã verify trên Docker Postgres:

```text
conversations.customer_account_id
customer_accounts.phone
customer_accounts.chat_limit
leads.customer_account_id
```

### 2. Customer auth

Files:

- `src/api/customer_auth.py`
- `src/api/routes.py`
- `src/api/dependencies.py`
- `src/services/security.py`
- `src/models/schemas.py`

Endpoints mới:

```text
POST /api/v1/customer/register
POST /api/v1/customer/login
GET  /api/v1/customer/me
```

Thiết kế token:

- Admin/sale token có `type=admin`.
- Customer token có `type=customer`.
- Admin endpoints từ chối customer token.

### 3. Chat behavior mới

Files:

- `src/api/agent_routes.py`
- `src/services/guest_chat_store.py`
- `src/api/lead_routes.py`

Guest/vãng lai:

- Không tạo row trong `conversations`.
- Không tạo row trong `messages`.
- Có rate limit tạm 5 tin/60 giây theo session id.
- Có transcript tạm in-memory để nếu guest submit lead ngay trong phiên thì vẫn có context ngắn cho lead scoring.
- Transcript này không phải CRM database và sẽ mất khi backend restart.

Customer đã đăng nhập:

- Request có customer token mới tạo/lưu conversation.
- Conversation gắn `customer_account_id`.
- Messages user/AI được lưu vào DB.
- Nếu AI trigger handover, backend tạo/cập nhật lead từ customer profile, không bắt nhập lại phone.
- Nếu customer gõ phone trong chat, lead cũng được gắn về `customer_account_id`.

### 4. Admin CRM

Files:

- `src/api/admin.py`
- `FE/src/app/admin/(dashboard)/leads/page.tsx`

Thay đổi:

- Lead list/detail preload customer account.
- Thêm endpoint:

```text
GET /api/v1/admin/leads/{lead_id}/conversations
```

- Trang Khách hàng:
  - click lead;
  - hiển thị danh sách phiên chat của lead/customer;
  - click phiên chat;
  - hiển thị messages của phiên đó.

Phân quyền:

- Admin xem toàn bộ.
- Sale chỉ xem lead được assign.
- Vì conversation được truy qua lead/customer đã scope, sale chỉ xem được chat của khách được phân công.

### 5. Admin users/RBAC UI

Files:

- `src/api/auth.py`
- `FE/src/components/admin-shell.tsx`
- `FE/src/app/admin/(dashboard)/users/page.tsx`
- `FE/src/app/admin.css`

Thay đổi:

- Thêm endpoint:

```text
PATCH /api/v1/auth/users/{user_id}/status
```

- Admin có thể khóa/mở user nội bộ.
- Không hard delete user.
- Sale không thấy menu “Nhân sự”.

### 6. Customer frontend

Files:

- `FE/src/lib/customer-auth.ts`
- `FE/src/app/dang-nhap/page.tsx`
- `FE/src/app/dang-ky/page.tsx`
- `FE/src/components/chat-widget.tsx`
- `FE/src/components/header.tsx`
- `FE/src/app/globals.css`

Thay đổi:

- Thêm trang `/dang-nhap`.
- Thêm trang `/dang-ky`.
- Login/register thành công:
  - lưu `customer_token`;
  - tạo `session_id` mới;
  - clear messages cũ trên browser.
- Logout trong chat:
  - xóa `customer_token`;
  - xóa `session_id`;
  - xóa local messages;
  - không gọi API xóa DB.
- Chat widget:
  - guest hiển thị số tin dùng thử còn lại;
  - customer hiển thị tên đang tư vấn;
  - guest không gửi Authorization;
  - customer gửi Authorization để backend lưu DB.

## Kết quả kiểm thử

### Full backend tests

```bash
.\.venv\Scripts\python.exe -m pytest -q
```

Kết quả:

```text
149 passed in 91.66s
```

### API/agent/db focused tests

```bash
.\.venv\Scripts\python.exe -m pytest tests\test_api tests\test_agents tests\test_db\test_migrations.py -q
```

Kết quả:

```text
58 passed
```

### Ruff

```bash
.\.venv\Scripts\ruff.exe check src tests migrations
```

Kết quả:

```text
All checks passed!
```

### Frontend build

```bash
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
Generated static pages successfully
```

### Docker backend/migration

```bash
docker compose up -d --build backend
```

Kết quả:

- backend image build thành công;
- migration mới chạy;
- Postgres có bảng/cột mới.

## Cách test thủ công

### 1. Guest chat không lưu DB

1. Mở website khi chưa đăng nhập customer.
2. Chat 1-2 tin.
3. Vào admin conversations/CRM.
4. Kỳ vọng:
   - không thấy conversation guest.

### 2. Guest limit

1. Chưa đăng nhập.
2. Chat 5 tin.
3. Tin tiếp theo sẽ được FE nhắc đăng nhập/đăng ký.

### 3. Customer login tạo session mới

1. Vào `/dang-ky`.
2. Đăng ký bằng họ tên/số điện thoại/mật khẩu.
3. Chat 1-2 tin.
4. Logout trong chat.
5. Login lại ở `/dang-nhap`.
6. Chat tiếp.
7. Vào admin lead/customer detail.
8. Kỳ vọng:
   - cùng customer có nhiều phiên chat.

### 4. Admin/sale xem chat theo khách

1. Admin mở `/admin/leads`.
2. Click một lead/customer.
3. Xem section “Phiên trò chuyện”.
4. Click từng phiên để xem messages.
5. Login bằng sale được assign lead.
6. Kỳ vọng:
   - sale chỉ thấy lead/chat được phân công.

### 5. Nhân sự/RBAC

1. Login admin.
2. Thấy menu “Nhân sự”.
3. Khóa một sale account.
4. Sale bị khóa không login được.
5. Mở lại sale account.
6. Login sale.
7. Kỳ vọng:
   - sale không thấy menu “Nhân sự”.

## Ghi chú triển khai staging/production

Sau khi merge/push:

1. Chờ GitHub Actions build image mới.
2. Trên VPS chạy deploy staging/production như quy trình hiện tại.
3. Backend startup sẽ chạy:

```bash
python -m alembic upgrade head
```

4. Kiểm tra migration đã lên revision `20260627_03`.

Không cần xóa volume/database. Migration là additive, không xóa dữ liệu cũ.

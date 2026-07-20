# Kế hoạch version 0.9.3 — Customer Auth, Multi-session Chat, CRM Conversation View

Ngày lập kế hoạch: 2026-06-27

Trạng thái: Chờ duyệt trước khi triển khai

## 1. Bối cảnh hiện tại

Dự án đã có:

- Admin/sale login cho dashboard nội bộ.
- Lead/contact form.
- Chat AI có `session_id`, lưu được lịch sử theo browser localStorage và backend database.
- Admin có quản lý leads, conversations, fallback rules, users nội bộ.
- Sale đã được giới hạn chỉ thấy lead/conversation được phân công ở backend.

Nhưng hiện tại còn các vấn đề:

1. Chat đã lưu phiên nhưng phiên browser đang giữ quá lâu.
2. Guest/localStorage không định danh khách hàng thật sự.
3. Khi quay lại website, hệ thống biết `session_id` nhưng chưa biết chắc người chat là ai.
4. Admin CRM chưa gom lịch sử chat theo đúng khách hàng rồi chia thành từng phiên chat.
5. Menu “Nhân sự” cần ẩn với tài khoản không phải admin.
6. Admin cần có thao tác khóa/mở tài khoản nội bộ.
7. Cần cơ chế phân quyền rõ:
   - admin xem toàn bộ;
   - sale chỉ xem khách được phân công;
   - customer chỉ thao tác với phiên chat/tài khoản của chính họ.

## 2. Thay đổi quan trọng so với bản kế hoạch ban đầu

Bản kế hoạch ban đầu đề xuất nút “Bắt đầu phiên mới”.

Sau khi review lại theo yêu cầu sản phẩm, hướng mới là:

- Không thêm nút “Bắt đầu phiên mới”.
- Tin nhắn của khách vãng lai/guest không lưu vào database.
- Khi customer đăng xuất:
  - xóa `customer_token` trên browser;
  - xóa `session_id` hiện tại trên browser;
  - xóa messages localStorage của phiên hiện tại nếu frontend đang cache;
  - không xóa conversation/messages trong database.
- Khi customer đăng nhập:
  - tạo `session_id` mới trên browser;
  - khi gửi chat đầu tiên, backend tạo conversation mới trong database;
  - conversation mới vẫn gắn với đúng `customer_account_id`.
- Một customer có thể có nhiều phiên chat.
- Chỉ customer đã đăng nhập mới có conversation/messages trong CRM.
- Admin/sale xem theo cấu trúc:

```text
Customer/Lead
  -> Danh sách phiên chat
      -> Messages của từng phiên
```

Đây là thiết kế được chọn cho version 0.9.3.

## 3. Mục tiêu version 0.9.3

Version này tập trung vào 4 mục tiêu.

### Mục tiêu A — Customer account

Thêm cơ chế đăng ký/đăng nhập cho khách hàng ngoài website bằng:

- họ tên;
- số điện thoại;
- mật khẩu.

Sau khi đăng nhập:

- chat sẽ gắn với tài khoản customer;
- lead sẽ gắn với customer;
- không cần hỏi lại tên/số điện thoại nếu customer đã đăng nhập.

### Mục tiêu B — Guest chat tạm thời và multi-session chat cho customer

Khách vãng lai vẫn có thể chat thử, nhưng tin nhắn guest chỉ tồn tại tạm trên browser và không ghi vào database.

Luồng guest/vãng lai:

```text
Guest mở chat
  -> Frontend tạo session tạm trên browser
  -> Messages chỉ lưu localStorage/sessionStorage
  -> Backend trả lời AI nhưng không tạo conversation/messages trong DB
  -> Guest tối đa 5 tin
  -> Nếu muốn tiếp tục: đăng ký/đăng nhập
```

Mỗi lần customer đăng nhập sẽ bắt đầu một phiên chat browser mới. Chỉ các phiên chat của customer đã đăng nhập mới được lưu vào database.

Luồng chuẩn:

```text
Customer login
  -> Frontend tạo session_id mới
  -> Chat message đầu tiên gửi kèm customer token + session_id
  -> Backend tạo conversation mới gắn customer_account_id
  -> Messages được lưu vào conversation đó

Customer logout
  -> Frontend xóa customer_token
  -> Frontend xóa session_id trên browser
  -> Frontend xóa cache messages localStorage
  -> Database vẫn giữ conversation/messages cũ
```

Ý nghĩa:

- Browser không bị dính mãi một phiên chat.
- Database vẫn giữ đầy đủ lịch sử tư vấn.
- Một customer có nhiều conversation theo thời gian.
- Sale/admin xem được timeline tư vấn rõ ràng.
- CRM không bị nhiễu bởi các đoạn chat vô danh.

### Mục tiêu C — CRM: xem chat theo khách hàng và theo phiên

Trong admin “Quản lý khách hàng”:

- click một khách hàng/lead sẽ thấy:
  - thông tin khách;
  - nhu cầu/tóm tắt;
  - trạng thái;
  - sale phụ trách;
  - notes chăm sóc;
  - danh sách các phiên chat của khách đó.
- click một phiên chat sẽ thấy messages của đúng phiên đó.

Phân quyền:

- admin xem tất cả khách và tất cả phiên chat;
- sale chỉ xem khách được phân công và các phiên chat của khách đó.

### Mục tiêu D — Admin UX/RBAC

Trong dashboard nội bộ:

- tài khoản không phải admin sẽ không thấy menu “Nhân sự”;
- admin có thể khóa/mở lại tài khoản nội bộ;
- tránh hard delete account để không mất lịch sử note/lead assignment.

## 4. Thiết kế dữ liệu đề xuất

### 4.1. Không trộn customer với bảng `users` hiện tại

Bảng `users` hiện tại đại diện cho nhân sự nội bộ:

- admin;
- sale.

Đề xuất tạo bảng riêng:

```text
customer_accounts
```

Lý do:

- Customer ngoài website có lifecycle khác nhân sự nội bộ.
- Customer không được vào admin dashboard.
- Nếu trộn vào `users`, role/permission/auth flow sẽ dễ rối.

### 4.2. Bảng mới: `customer_accounts`

Field đề xuất:

```text
id
full_name
phone
password_hash
is_active
chat_limit
created_at
updated_at
```

Ghi chú:

- `phone` nên unique.
- `chat_limit` mặc định 100 cho customer đã đăng nhập.
- Guest không có account, dùng giới hạn riêng theo session.

### 4.3. Cập nhật bảng `leads`

Thêm field:

```text
customer_account_id nullable FK -> customer_accounts.id
```

Ý nghĩa:

- Một customer có thể có một hoặc nhiều lead theo thời gian.
- Lead vẫn giữ `assigned_to_id` để xác định sale phụ trách.
- Sale được phân công qua lead, không phân công trực tiếp qua conversation.

### 4.4. Cập nhật bảng `conversations`

Thêm field:

```text
customer_account_id nullable FK -> customer_accounts.id
```

Giữ nguyên:

```text
session_id unique
lead_id nullable
status
started_at
last_message_at
```

Ý nghĩa:

- Guest chat: không tạo conversation/messages trong database ở version này.
- Customer đã login: conversation gắn với customer.
- Mỗi lần login mới có thể tạo một conversation mới.
- Logout chỉ xóa session trên browser, không xóa row trong database.

### 4.5. Quan hệ dữ liệu mong muốn

```text
customer_accounts
  ├── leads[]
  │     └── assigned_to_id -> users.id (sale/admin nội bộ)
  └── conversations[]
        └── messages[]
```

Với dashboard CRM:

```text
Lead/Customer detail
  -> Conversations của customer đó
      -> Messages của conversation được chọn
```

## 5. Thiết kế Backend

### 5.1. Customer auth endpoints

Thêm nhóm endpoint:

```text
POST /api/v1/customer/register
POST /api/v1/customer/login
GET  /api/v1/customer/me
```

Logout không nhất thiết cần backend endpoint ở version đầu.

Lý do:

- Nếu dùng JWT stateless, logout chủ yếu là xóa token ở browser.
- Browser cũng xóa `session_id` hiện tại.
- Database không xóa conversation.

Payload register:

```json
{
  "full_name": "Nguyễn Văn A",
  "phone": "0912345678",
  "password": "secret123"
}
```

Payload login:

```json
{
  "phone": "0912345678",
  "password": "secret123"
}
```

Token:

```text
sub = customer_account_id
type = customer
```

### 5.2. Chat endpoint update

Update `POST /agent/chat`:

- Nếu có customer token:
  - lấy `customer_account_id`;
  - nếu `session_id` chưa có conversation thì tạo conversation mới;
  - gắn conversation với customer;
  - lưu user/AI messages vào database;
  - áp dụng limit customer.
- Nếu không có customer token:
  - xử lý như guest/vãng lai;
  - không tạo conversation;
  - không lưu messages;
  - trả response cho frontend;
  - áp dụng limit guest ở browser/local session.

Giới hạn đề xuất:

```text
guest: 5 user messages / session
customer: 100 user messages / session
```

Lý do chọn:

- Guest không định danh nên không đưa vào CRM.
- Customer đã định danh nên được lưu nhiều phiên để sale/admin theo dõi.
- Customer limit theo session phù hợp với yêu cầu “một customer có nhiều phiên chat”.

### 5.3. Login/logout session behavior

Frontend chịu trách nhiệm:

Khi login thành công:

```text
save customer_token
create new session_id
clear old local chat messages
```

Khi logout:

```text
remove customer_token
remove session_id
remove local chat messages
```

Backend chịu trách nhiệm:

```text
chỉ lưu conversation/messages nếu request có customer token hợp lệ
không xóa conversation
không xóa messages
không xóa lead
```

### 5.4. Lead capture update

Khi customer đã login:

- Nếu AI cần chuyển Sales:
  - không cần hỏi lại tên/số điện thoại;
  - tạo/cập nhật lead từ profile customer.
- Lead tạo ra sẽ có:

```text
customer_account_id = current_customer.id
phone = current_customer.phone
name = current_customer.full_name
source = chat
```

Khi guest để lại phone:

- tạo/cập nhật lead như hiện tại;
- không tự login;
- không cấp quyền xem lịch sử customer account chỉ vì nhập phone.
- không lưu toàn bộ messages guest vào bảng `messages`;
- nếu cần, chỉ lưu một `summary` ngắn trong lead.

### 5.5. Admin lead/customer conversations

Thêm endpoint đề xuất:

```text
GET /api/v1/admin/leads/{lead_id}/conversations
GET /api/v1/admin/conversations/{conversation_id}
```

Endpoint đầu trả danh sách phiên:

```json
[
  {
    "id": 12,
    "session_id": "session-abc",
    "started_at": "...",
    "last_message_at": "...",
    "message_count": 8,
    "status": "active"
  }
]
```

Endpoint thứ hai trả messages của một phiên:

```json
{
  "id": 12,
  "session_id": "session-abc",
  "messages": [
    {
      "sender": "customer",
      "content": "...",
      "created_at": "..."
    },
    {
      "sender": "ai",
      "content": "...",
      "created_at": "..."
    }
  ]
}
```

Phân quyền:

- admin: được xem.
- sale: chỉ được xem nếu lead liên quan có `assigned_to_id == current_user.id`.

### 5.6. Admin users update

Thêm endpoint:

```text
PATCH /api/v1/auth/users/{user_id}/status
```

Payload:

```json
{
  "is_active": false
}
```

Không hard delete ở version này.

Lý do:

- User nội bộ có thể đã tạo notes, được assign lead.
- Xóa vật lý dễ làm mất referential integrity hoặc lịch sử vận hành.

## 6. Thiết kế Frontend

### 6.1. Customer auth UI

Thêm UI ngoài website:

```text
/dang-nhap
/dang-ky
```

Version đầu làm page riêng đơn giản trước.

Sau đó có thể tối ưu thành modal trong ChatWidget nếu cần.

### 6.2. ChatWidget update

Thay đổi:

- Không thêm nút “Bắt đầu phiên mới”.
- Hiển thị trạng thái:
  - Khách vãng lai;
  - Đã đăng nhập: tên customer.
- Nếu guest gần hết 5 tin:
  - gợi ý đăng ký/đăng nhập để tiếp tục.
- Khi customer login:
  - tạo `session_id` mới;
  - clear cache messages cũ.
- Khi customer logout:
  - xóa `customer_token`;
  - xóa `session_id`;
  - clear cache messages localStorage;
  - không gọi API xóa conversation.

### 6.3. Admin sidebar RBAC

Update sidebar:

- Nếu `currentUser.role !== "admin"`:
  - ẩn menu “Nhân sự”.

Backend vẫn phải giữ guard admin-only cho endpoint users.

### 6.4. Admin user management

Trong trang Nhân sự:

- hiển thị trạng thái active/inactive;
- admin có nút:
  - “Khóa”;
  - “Mở lại”.

Không làm nút “Xóa vĩnh viễn” ở version này.

### 6.5. Admin lead detail: show sessions then messages

Trong trang Khách hàng:

- click lead/customer;
- panel detail thêm section “Phiên trò chuyện”;
- hiển thị danh sách conversations của customer/lead đó;
- click conversation để xem messages của phiên đó.

Với sale:

- vì backend filter lead theo assignment, sale chỉ thấy chat của khách được phân công.

## 7. Phạm vi triển khai version 0.9.3

### Nên làm trong version này

- Tạo bảng `customer_accounts`.
- Thêm customer register/login/me.
- Chat gắn customer khi có token.
- Guest chat không lưu DB.
- Login tạo session mới trên browser.
- Logout xóa session/token/messages trên browser.
- Database giữ nguyên conversation/messages.
- Guest/customer chat limit cơ bản.
- Admin/sale xem conversations theo lead/customer rồi xem messages theo phiên.
- Ẩn menu Nhân sự với sale.
- Admin khóa/mở tài khoản nội bộ.
- Report hướng dẫn test.

### Chưa nên làm trong version này

- Social login.
- OTP SMS.
- Forgot password.
- Email verification.
- Payment/booking thật.
- Customer dashboard riêng đầy đủ.
- Vector DB/Supabase migration.
- Hard delete tài khoản nội bộ.
- Xem lại toàn bộ lịch sử chat phía customer sau login.

## 8. Migration và rủi ro

### Migration cần có

Nếu dự án đang dùng Alembic:

- tạo migration thêm bảng `customer_accounts`;
- thêm FK nullable vào `leads`;
- thêm FK nullable vào `conversations`.

Nếu chưa dùng migration ổn định:

- update SQLAlchemy models;
- `create_all` chỉ tạo bảng mới nhưng không luôn thêm cột vào bảng Postgres đã tồn tại;
- staging/prod nên dùng Alembic migration.

### Rủi ro

1. Nếu tự động link phone guest vào customer account, có thể sai nếu người nhập nhầm số.
   - Giải pháp: chỉ link account khi customer thật sự login.

2. Nếu hard delete internal user sẽ ảnh hưởng lead/note.
   - Giải pháp: dùng `is_active=false`.

3. Nếu chat limit chỉ theo localStorage, user có thể clear browser để vượt limit.
   - Giải pháp: chấp nhận ở version đầu vì guest không lưu CRM; khi muốn nghiêm hơn có thể dùng anonymous signed session/cookie.

4. Nếu customer auth và admin auth dùng chung localStorage key sẽ gây lỗi.
   - Giải pháp: tách key:

```text
admin_token
customer_token
chat_session_id
```

5. Nếu logout xóa nhầm dữ liệu database sẽ mất lịch sử tư vấn.
   - Giải pháp: logout chỉ clear browser state, tuyệt đối không delete conversation/messages.

6. Nếu guest chat không lưu DB, sale không xem lại được nội dung guest đã hỏi trước khi đăng ký.
   - Giải pháp: khi guest đăng ký/login, bắt đầu phiên mới sạch; nếu cần chuyển ngữ cảnh, frontend có thể gửi tin nhắn cuối cùng làm câu hỏi đầu tiên sau login ở version sau.

## 9. Test plan

### Backend tests

Test cần thêm:

1. Customer register thành công.
2. Không cho trùng phone.
3. Customer login đúng/sai password.
4. `/customer/me` trả đúng customer.
5. Guest chat bị chặn sau 5 tin/session.
6. Customer chat có limit cao hơn guest.
7. Guest chat không tạo conversation/messages trong DB.
8. Chat có customer token tạo conversation gắn `customer_account_id`.
9. Mỗi lần login mới có thể tạo một `session_id`/conversation mới.
10. Logout không xóa conversation/messages trong database.
11. Lead tạo từ customer login có `customer_account_id`.
12. Sale không đọc được lead/conversation không được assign.
13. Admin đọc được toàn bộ.
14. Admin khóa/mở user nội bộ.

### Frontend tests/manual checklist

1. Guest chat 5 tin, sau đó thấy gợi ý login/register.
2. Guest chat không xuất hiện trong admin conversations/CRM.
3. Customer đăng ký bằng tên/số điện thoại/mật khẩu.
4. Customer login, browser sinh `session_id` mới.
5. Customer chat, backend tạo conversation gắn với customer.
6. Customer logout, browser xóa token/session/messages local.
7. Customer login lại, browser sinh `session_id` mới.
8. Admin mở khách hàng đó và thấy nhiều phiên chat.
9. Click từng phiên chat thấy đúng messages của phiên đó.
10. Admin thấy menu Nhân sự.
11. Sale không thấy menu Nhân sự.
12. Admin khóa một sale account.
13. Sale bị khóa không login được.
14. Admin mở lại sale account.
15. Sale chỉ xem được chat của lead/customer được assign.

## 10. Quyết định cần duyệt trước khi làm

Mình đề xuất các quyết định sau:

1. Tạo bảng customer riêng: `customer_accounts`.
2. Customer đăng ký bằng:
   - họ tên;
   - số điện thoại;
   - mật khẩu.
3. Phone customer là unique.
4. Guest giới hạn 5 tin / session.
5. Customer giới hạn 100 tin / session.
6. Guest/vãng lai không lưu conversation/messages vào database.
7. Không thêm nút “Bắt đầu phiên mới”.
8. Login tạo `session_id` mới trên browser.
9. Logout xóa `customer_token`, `session_id`, local messages trên browser.
10. Logout không xóa conversation/messages trong database.
11. Một customer có nhiều conversations.
12. Admin/sale xem theo luồng: customer/lead -> conversations -> messages.
13. Admin không hard delete user nội bộ, chỉ khóa/mở bằng `is_active`.

Nếu bạn duyệt các quyết định trên, mình sẽ triển khai version 0.9.3 theo kế hoạch này.

## 11. Kết quả mong đợi sau version 0.9.3

Sau khi hoàn thành:

- Guest vẫn chat được nhưng có giới hạn.
- Guest không tạo dữ liệu chat trong CRM/database.
- Customer có thể đăng ký/login để chat dài hơn và giữ định danh.
- Mỗi lần login có thể bắt đầu một phiên chat mới.
- Logout chỉ clear browser, database vẫn giữ lịch sử tư vấn.
- Một customer có nhiều phiên chat.
- Admin/sale xem được từng phiên chat của khách.
- Sale chỉ xem đúng khách được phân công.
- Admin quản lý nhân sự an toàn hơn bằng khóa/mở tài khoản.

Đây là nền CRM/chat tốt hơn trước khi tiếp tục nâng AI Agent, scoring, recommendation và workflow chăm sóc khách hàng.

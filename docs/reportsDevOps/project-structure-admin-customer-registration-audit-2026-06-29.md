# Báo cáo rà soát cấu trúc dự án và lỗi đăng ký khách hàng không hiện trong Admin

Ngày tạo: 2026-06-29  
Trạng thái: Chờ duyệt trước khi sửa code  
Phạm vi: Backend, Frontend, Database, Admin CRM, Customer registration, Chat/Lead flow  

## 1. Mục tiêu rà soát

Hiện tại production/staging đã chạy được, nhưng phát sinh vấn đề:

```text
Khi người dùng mới đăng ký tài khoản khách hàng,
Admin -> Khách hàng không hiển thị khách hàng đó.
```

Mục tiêu báo cáo này:

- Rà lại cấu trúc source code hiện tại.
- Xác định luồng dữ liệu của khách hàng đăng ký, lead, conversation.
- Giải thích vì sao đăng ký user mới không hiện trong Admin/Khách hàng.
- Đưa ra phương án khắc phục để duyệt trước khi triển khai.

## 2. Tổng quan cấu trúc dự án hiện tại

### 2.1 Backend

Backend dùng FastAPI.

Các file chính:

```text
src/main.py
src/api/routes.py
src/api/customer_auth.py
src/api/admin.py
src/api/agent_routes.py
src/api/lead_routes.py
src/models/entities.py
src/models/schemas.py
src/db/session.py
src/db/seed.py
src/db/seed_admin.py
```

`src/main.py` đăng ký các router:

```py
app.include_router(router, prefix="/api/v1")
app.include_router(lead_router, prefix="/api/v1")
app.include_router(zone_router, prefix="/api/v1")
app.include_router(agent_router)
```

Trong đó:

- `/api/v1/customer/register` nằm trong `customer_auth.py`.
- `/api/v1/admin/leads` nằm trong `admin.py`.
- `/agent/chat` nằm trong `agent_routes.py`.

### 2.2 Frontend

Frontend dùng Next.js.

Các phần liên quan:

```text
FE/src/app/dang-ky/page.tsx
FE/src/app/dang-nhap/page.tsx
FE/src/app/admin/(dashboard)/leads/page.tsx
FE/src/app/admin/(dashboard)/conversations/page.tsx
FE/src/components/chat-widget.tsx
FE/src/lib/customer-auth.ts
FE/src/lib/auth-context.tsx
FE/src/lib/auth.ts
FE/src/lib/api.ts
```

Luồng đăng ký khách hàng hiện tại:

```text
FE /dang-ky
  -> POST /api/v1/customer/register
  -> lưu customer token vào localStorage
  -> tạo chat session mới trên browser
  -> redirect về trang chủ
```

Luồng admin khách hàng:

```text
FE /admin/leads
  -> GET /api/v1/admin/leads
  -> render danh sách Lead
```

Điểm quan trọng:

```text
Trang Admin -> Khách hàng hiện đang đọc bảng Lead,
không đọc trực tiếp bảng CustomerAccount.
```

## 3. Cấu trúc database liên quan

Trong `src/models/entities.py`, hiện có các bảng chính:

### 3.1 `customer_accounts`

Model:

```py
class CustomerAccount:
    id
    full_name
    phone
    password_hash
    is_active
    chat_limit
```

Ý nghĩa:

```text
Đây là tài khoản đăng nhập của khách hàng ngoài website.
```

Khi user đăng ký ở `/dang-ky`, backend tạo record ở bảng này.

### 3.2 `leads`

Model:

```py
class Lead:
    id
    name
    phone
    email
    budget_min
    budget_max
    preferred_bedrooms
    customer_type
    status
    source
    summary
    assigned_to_id
    customer_account_id
```

Ý nghĩa:

```text
Đây là khách hàng/lead trong CRM Admin.
```

Trang `/admin/leads` hiện đọc bảng này.

### 3.3 `conversations`

Model:

```py
class Conversation:
    id
    session_id
    lead_id
    customer_account_id
    subdivision_id
    status
    started_at
    last_message_at
```

Ý nghĩa:

```text
Đây là phiên chat của khách hàng đã đăng nhập.
```

Một customer account có thể có nhiều conversation.

### 3.4 `messages`

Model:

```py
class Message:
    id
    conversation_id
    sender
    content
    created_at
```

Ý nghĩa:

```text
Lưu nội dung tin nhắn theo từng conversation.
```

## 4. Luồng đăng ký user hiện tại

Frontend:

```text
FE/src/app/dang-ky/page.tsx
```

Gửi request:

```ts
POST `${API_URL}/customer/register`
```

Backend:

```text
src/api/customer_auth.py
```

Hàm:

```py
register_customer()
```

Logic hiện tại:

```py
if phone đã tồn tại trong CustomerAccount:
    báo lỗi 409

tạo CustomerAccount(
    full_name=request.full_name,
    phone=request.phone,
    password_hash=...
)

return access_token
```

Kết quả:

```text
Đăng ký user mới chỉ tạo record trong customer_accounts.
Không tạo Lead.
Không tạo Conversation.
Không hiện trong Admin -> Khách hàng.
```

## 5. Luồng Admin -> Khách hàng hiện tại

Frontend:

```text
FE/src/app/admin/(dashboard)/leads/page.tsx
```

Gọi API:

```ts
adminFetch("/admin/leads")
```

Backend:

```text
src/api/admin.py
```

Hàm:

```py
list_leads()
```

Logic:

```py
select(Lead)
```

Kết quả:

```text
Admin -> Khách hàng chỉ hiện record trong bảng leads.
Tài khoản trong customer_accounts không tự hiện.
```

## 6. Khi nào một CustomerAccount trở thành Lead?

Hiện tại có 3 tình huống tạo Lead:

### 6.1 Khách gửi contact form

Frontend `ContactForm` gọi:

```text
POST /api/v1/contact
```

Tuy nhiên cần kiểm tra kỹ endpoint hiện tại đang đi vào route nào:

- `src/api/routes.py` có legacy `/contact` chỉ log và return.
- `src/api/leads.py` hoặc route khác có thể có logic lưu lead thật.

Nếu `/contact` bị match vào legacy route không lưu DB thì contact form có thể không tạo lead.

### 6.2 Khách vãng lai để lại số điện thoại trong chat

Trong `src/api/agent_routes.py`, nếu customer chưa đăng nhập mà nhắn số điện thoại:

```py
if customer is None and captured_phone:
    tạo hoặc cập nhật Lead(source="chat_guest")
```

### 6.3 Khách đã đăng nhập chat và trigger handover / để lại phone

Trong `src/api/agent_routes.py`, nếu customer đã đăng nhập:

```py
conversation = get_or_create Conversation(customer_account_id=customer.id)
```

Nếu AI trigger handover:

```py
lead = _get_or_create_customer_lead(db, customer, summary)
conversation.lead_id = lead.id
```

Nếu khách để lại phone trong chat:

```py
lead = Lead(..., customer_account_id=customer.id)
conversation.lead_id = lead.id
```

Nghĩa là customer đã đăng ký **chỉ thành Lead sau khi chat tạo nhu cầu/trigger handover hoặc để lại thông tin trong chat**, không phải ngay lúc đăng ký.

## 7. Nguyên nhân lỗi hiện tại

Đây không phải lỗi deploy.

Nguyên nhân chính là thiết kế dữ liệu hiện tại đang tách:

```text
CustomerAccount = tài khoản đăng nhập
Lead = khách hàng CRM trong admin
```

Khi user đăng ký:

```text
/api/v1/customer/register
  -> INSERT customer_accounts
  -> KHÔNG INSERT leads
```

Trong khi Admin -> Khách hàng:

```text
/api/v1/admin/leads
  -> SELECT leads
```

Vì vậy admin không thấy user mới đăng ký là hành vi đúng theo code hiện tại, nhưng không đúng với kỳ vọng sản phẩm của bạn.

## 8. Vấn đề thiết kế cần quyết định

Cần quyết định rõ:

```text
Một người đăng ký tài khoản có được coi là "Khách hàng/Lead" ngay lập tức không?
```

Theo yêu cầu mới của bạn:

```text
Có. Khi user đăng ký bằng tên + số điện thoại + mật khẩu,
admin cần nhìn thấy người đó trong quản lý khách hàng.
```

Vậy cần điều chỉnh thiết kế:

```text
CustomerAccount sau khi đăng ký phải có Lead tương ứng.
```

## 9. Phương án khắc phục đề xuất

### Phương án A - Tạo Lead ngay khi đăng ký CustomerAccount

Khi user đăng ký thành công:

```text
INSERT customer_accounts
INSERT leads nếu chưa có lead cùng phone
link leads.customer_account_id = customer_accounts.id
```

Lead mặc định:

```py
Lead(
    name=customer.full_name,
    phone=customer.phone,
    source="customer_register",
    status="new",
    customer_type="registered",
    summary="Khách hàng đã đăng ký tài khoản nhưng chưa phát sinh nhu cầu cụ thể.",
    customer_account_id=customer.id,
)
```

Nếu đã có Lead cùng phone:

```text
Không tạo trùng.
Cập nhật lead.customer_account_id nếu đang null.
Cập nhật name nếu lead chưa có name.
Cập nhật source/summary nhẹ nếu phù hợp.
```

Ưu điểm:

- Admin thấy khách ngay sau đăng ký.
- Đúng kỳ vọng hiện tại.
- Không cần tạo màn customer accounts riêng ngay.
- Các phiên chat sau này vẫn link được vào Lead qua `customer_account_id`.

Nhược điểm:

- CRM sẽ có cả khách mới đăng ký nhưng chưa có nhu cầu rõ.
- Cần phân biệt source/status để sale biết đây là account mới, chưa hẳn lead nóng.

### Phương án B - Tạo tab Admin riêng: Tài khoản khách hàng

Giữ nguyên logic hiện tại:

```text
Đăng ký chỉ tạo CustomerAccount.
Lead chỉ tạo khi có nhu cầu/chat/contact.
```

Thêm Admin page:

```text
/admin/customers
```

API:

```text
GET /api/v1/admin/customers
GET /api/v1/admin/customers/{id}
```

Ưu điểm:

- Phân tách đúng nghiệp vụ:
  - Account là account.
  - Lead là lead.
- CRM ít bị nhiễu.

Nhược điểm:

- Không đúng mong muốn hiện tại nếu bạn muốn Admin -> Khách hàng hiển thị ngay.
- Cần thêm UI/API mới.
- Sale phải xem thêm một tab.

### Phương án C - Admin Khách hàng hiển thị hợp nhất Lead + CustomerAccount

Sửa `/admin/leads` hoặc frontend để hiển thị:

```text
Lead records
+ CustomerAccount chưa có Lead
```

Ưu điểm:

- Không cần tạo Lead ngay khi đăng ký.
- Admin vẫn thấy toàn bộ người đăng ký.

Nhược điểm:

- API phức tạp hơn.
- Frontend phải xử lý hai loại record khác nhau.
- Các thao tác status/assignment/note sẽ khó vì CustomerAccount chưa có Lead id.

## 10. Phương án khuyến nghị

Mình đề xuất chọn **Phương án A**:

```text
Tạo hoặc link Lead ngay khi CustomerAccount đăng ký.
```

Lý do:

- Phù hợp kỳ vọng của bạn: đăng ký xong admin phải thấy khách.
- Ít thay đổi UI nhất.
- Không phá cấu trúc hiện tại.
- Vẫn giữ được quan hệ:

```text
CustomerAccount 1 - n Conversation
CustomerAccount 1 - n/1 Lead thông qua customer_account_id
Lead 1 - n Conversation thông qua lead_id hoặc customer_account_id
```

Để tránh nhiễu CRM, Lead tạo từ đăng ký sẽ có source rõ:

```text
source = customer_register
status = new
customer_type = registered
summary = Khách hàng đã đăng ký tài khoản nhưng chưa phát sinh nhu cầu cụ thể.
```

## 11. Kế hoạch triển khai nếu được duyệt

### Bước 1 - Sửa backend đăng ký customer

File:

```text
src/api/customer_auth.py
```

Trong `register_customer()`, sau khi tạo `CustomerAccount`, thêm logic:

```text
find Lead by phone
if not exists:
    create Lead from CustomerAccount
else:
    link existing Lead to CustomerAccount
```

Cần import thêm:

```py
Lead
```

### Bước 2 - Đảm bảo không tạo duplicate lead

Rule:

```text
Một phone chỉ nên có một lead active chính.
```

Vì bảng `leads.phone` hiện chỉ index, chưa unique, nên ở logic code cần query:

```py
db.query(Lead).filter(Lead.phone == customer.phone).order_by(Lead.created_at.desc()).first()
```

Không nên thêm unique constraint ngay vì production DB có thể đã có dữ liệu trùng.

### Bước 3 - Cập nhật summary/source rõ ràng

Lead đăng ký mới:

```text
source=customer_register
customer_type=registered
status=new
summary=Khách hàng đã đăng ký tài khoản nhưng chưa phát sinh nhu cầu cụ thể.
```

Nếu sau này khách chat, `agent_routes.py` sẽ cập nhật summary và link conversation.

### Bước 4 - Bổ sung test backend

Thêm test cho:

```text
POST /api/v1/customer/register tạo CustomerAccount
POST /api/v1/customer/register tạo Lead tương ứng
Đăng ký trùng phone trả 409
Nếu đã có Lead cùng phone thì không tạo duplicate, chỉ link customer_account_id
```

Vị trí test có thể là:

```text
tests/test_api/test_customer_registration.py
```

### Bước 5 - Test frontend/admin

Manual test:

1. Mở production/staging.
2. Đăng ký user mới bằng số điện thoại chưa tồn tại.
3. Login admin.
4. Vào:

```text
/admin/leads
```

5. Kỳ vọng thấy khách mới với:

```text
name = full_name đăng ký
phone = phone đăng ký
source = customer_register
status = new
summary = chưa phát sinh nhu cầu cụ thể
```

### Bước 6 - Deploy staging trước

Quy trình:

```text
fix trên branch TranMinhQuang
PR -> dev
CI pass
deploy staging
test đăng ký khách
```

### Bước 7 - Sau khi staging ổn mới lên production

Quy trình:

```text
PR dev -> main
CI pass
deploy production image :main
test production
```

## 12. Rủi ro và lưu ý

### 12.1 Có thể xuất hiện nhiều lead cùng phone trong dữ liệu cũ

Vì hiện tại `Lead.phone` chưa unique, trước khi ép unique cần audit data.

Ở bản sửa đầu tiên, chỉ xử lý logic không tạo thêm duplicate.

### 12.2 Sale account chỉ thấy lead được phân công

Trong `src/api/admin.py`:

```py
if user.role == "sale":
    query.where(Lead.assigned_to_id == user.id)
```

Vì lead đăng ký mới mặc định `assigned_to_id = null`, sale thường sẽ không thấy.

Admin role sẽ thấy.

Nếu muốn sale thấy lead chưa phân công, cần đổi rule phân quyền riêng, nhưng không nên gộp vào bản fix này nếu chưa duyệt.

### 12.3 Tên "Khách hàng" trong Admin đang thực chất là Lead CRM

UI đang gọi là:

```text
Khách hàng
```

nhưng backend là:

```text
Lead
```

Sau bản fix, đăng ký account sẽ tự tạo Lead nên UI hiện tại có thể giữ nguyên.

## 13. Quyết định cần duyệt

Mình đề xuất duyệt phương án:

```text
Phương án A: Khi khách đăng ký tài khoản, backend tự tạo/link Lead tương ứng.
```

Phạm vi sửa:

```text
src/api/customer_auth.py
tests/test_api/test_customer_registration.py
```

Không sửa UI nếu chưa cần.

Không đổi database schema ở bước đầu.

Không đổi phân quyền sale/admin ở bước đầu.

## 14. Kết luận

Lỗi "đăng ký người dùng mới nhưng Admin không hiện khách hàng" là do thiết kế hiện tại:

```text
Đăng ký tạo CustomerAccount.
Admin Khách hàng đọc Lead.
CustomerAccount không tự sinh Lead.
```

Đây là mismatch giữa kỳ vọng sản phẩm và logic hiện tại, không phải lỗi deploy.

Phương án tối ưu hiện tại là:

```text
Đăng ký CustomerAccount xong thì tạo/link Lead với source=customer_register.
```

Sau khi bạn duyệt, mình sẽ triển khai bản fix theo kế hoạch trên.


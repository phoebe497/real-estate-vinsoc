# Báo cáo sửa luồng Customer → AI → Lead → CRM Admin

Ngày thực hiện: 2026-06-30  
Phạm vi: Customer registration, AI handover intent, Admin lead/chat UI, tests  
Trạng thái: Đã implement và test local thành công  

## 1. Kiến trúc hiện tại sau khi sửa

Luồng dữ liệu sau khi sửa:

```text
Customer Register
  -> CustomerAccount
  -> tạo/link Lead với source=customer_register
  -> Admin CRM nhìn thấy ngay trong /admin/leads

Customer Login
  -> tạo session_id mới trên browser

Customer Chat
  -> Conversation(customer_account_id)
  -> Message
  -> nếu có tín hiệu handover rõ ràng hoặc khách để lại phone
     -> tạo/link Lead
     -> link Conversation với Lead

Admin CRM
  -> /admin/leads: chỉ danh sách khách hàng/lead
  -> /admin/leads/[id]: thông tin khách + danh sách conversation + messages
```

Điểm thống nhất nghiệp vụ mới:

```text
CustomerAccount là tài khoản đăng nhập.
Lead là record CRM.
Khi có CustomerAccount mới, hệ thống đảm bảo có Lead CRM tương ứng.
```

## 2. File đã thay đổi

Backend:

```text
src/api/customer_auth.py
src/agents/nodes/intent_node.py
src/api/admin.py
src/models/schemas.py
```

Frontend:

```text
FE/src/components/admin-shell.tsx
FE/src/app/admin/(dashboard)/leads/page.tsx
FE/src/app/admin/(dashboard)/leads/[id]/page.tsx
FE/src/app/admin.css
```

Tests:

```text
tests/test_api/test_customer_registration.py
tests/test_agents/test_graph.py
```

Docs liên quan được thêm trước đó và hiện vẫn untracked:

```text
docs/reportsDevOps/final-staging-production-deployment-runbook-2026-06-29.md
docs/reportsDevOps/project-structure-admin-customer-registration-audit-2026-06-29.md
```

## 3. API đã thay đổi

### 3.1 `POST /api/v1/customer/register`

Trước đây:

```text
Chỉ tạo CustomerAccount.
```

Sau khi sửa:

```text
Tạo CustomerAccount.
Tìm Lead theo phone.
Nếu chưa có Lead -> tạo Lead mới.
Nếu đã có Lead -> không tạo duplicate, chỉ link customer_account_id và cập nhật name nếu thiếu.
```

Lead mặc định khi đăng ký:

```text
name = customer.full_name
phone = customer.phone
source = customer_register
status = new
customer_type = registered
summary = Khách hàng đã đăng ký tài khoản nhưng chưa phát sinh nhu cầu cụ thể.
customer_account_id = customer.id
```

### 3.2 `GET /api/v1/admin/leads/{id}/conversations`

Bổ sung field trong response:

```text
last_message_content
```

Mục đích:

```text
Trang chi tiết khách hàng hiển thị danh sách conversation có tin nhắn cuối.
```

### 3.3 `GET /api/v1/admin/conversations`

Cũng bổ sung:

```text
last_message_content
```

API cũ vẫn giữ nguyên, không xóa.

## 4. Migration

Không có migration.

Không thay đổi schema database.

Không thêm unique constraint cho `Lead.phone` để tránh rủi ro với dữ liệu production đã tồn tại.

Logic chống duplicate được xử lý ở tầng application:

```text
query Lead theo phone
chỉ tạo mới nếu chưa có
```

## 5. Test đã thêm/cập nhật

### 5.1 Customer registration tests

File:

```text
tests/test_api/test_customer_registration.py
```

Các case:

```text
Đăng ký tạo CustomerAccount.
Đăng ký tạo Lead tương ứng.
Đăng ký trùng phone trả 409.
Nếu đã có Lead cùng phone thì không tạo duplicate.
customer_account_id được link vào Lead cũ.
```

### 5.2 AI handover tests

File:

```text
tests/test_agents/test_graph.py
```

Các case thêm:

```text
"Tôi cần căn 2PN khu Zenpark." -> không handover.
"Tôi muốn gặp sale." -> handover.
```

## 6. Nguyên nhân từng lỗi

### 6.1 Đăng ký user mới nhưng Admin không hiện khách

Nguyên nhân:

```text
/customer/register chỉ tạo CustomerAccount.
/admin/leads chỉ đọc bảng Lead.
Không có bước tự tạo/link Lead sau đăng ký.
```

File liên quan:

```text
src/api/customer_auth.py
src/api/admin.py
src/models/entities.py
FE/src/app/admin/(dashboard)/leads/page.tsx
```

Logic cũ:

```text
CustomerAccount và Lead tách rời hoàn toàn ở thời điểm đăng ký.
```

Logic mới:

```text
Đăng ký customer xong đảm bảo có Lead CRM tương ứng.
```

### 6.2 AI handover quá sớm

Nguyên nhân:

```text
src/agents/nodes/intent_node.py có các handover regex quá rộng.
```

Các pattern cũ gây rủi ro:

```text
tầng \d+
căn \d+
căn hộ \d+
phòng \d+
```

Những pattern này dễ hiểu nhầm nhu cầu tư vấn thông thường là yêu cầu căn cụ thể.

File tạo response xin số:

```text
src/agents/nodes/llm_node.py
```

Nhưng nguyên nhân trigger nằm ở:

```text
src/agents/nodes/intent_node.py
```

Logic mới:

```text
Chỉ handover khi có tín hiệu rõ:
- muốn gặp sale
- muốn liên hệ
- muốn xem nhà
- muốn đặt cọc
- muốn giữ chỗ
- muốn chốt căn
- hỏi quỹ căn/căn còn/giá chốt
- đưa mã căn cụ thể kiểu R1.01
```

Các câu tư vấn chung như:

```text
Tôi cần căn 2PN khu Zenpark.
```

sẽ tiếp tục tư vấn, không xin số điện thoại.

### 6.3 Admin chat UI khó đọc

Nguyên nhân:

```text
/admin/leads cũ vừa hiển thị list lead, vừa detail, vừa conversations, vừa messages trên cùng một màn.
```

Logic mới:

```text
/admin/leads: chỉ danh sách khách hàng.
/admin/leads/[id]: chi tiết khách hàng + split layout conversation/messages.
```

### 6.4 Menu Hội thoại riêng không còn cần thiết

Nguyên nhân:

```text
Conversation nên được xem theo từng khách hàng.
Trang quản lý Hội thoại riêng làm rối flow CRM.
```

Đã xử lý:

```text
Ẩn menu Hội thoại trong AdminShell.
Không xóa route/API/table Conversation.
```

## 7. Giải pháp đã áp dụng

### 7.1 Backend registration

Thêm helper:

```py
_link_or_create_registered_lead()
```

Đảm bảo:

```text
Không duplicate Lead.
Lead cũ được link customer_account_id.
Lead thiếu name sẽ được cập nhật.
```

### 7.2 AI handover

Thu hẹp `_HANDOVER_PATTERNS`.

Loại bỏ pattern quá rộng với:

```text
căn \d+
căn hộ \d+
phòng \d+
tầng \d+
```

Bổ sung các trigger rõ ràng hơn:

```text
gặp sale
liên hệ
xem nhà
đặt cọc
giữ chỗ
chốt căn
giá chốt
quỹ căn
```

### 7.3 Admin UI

Tách màn hình:

```text
List page: /admin/leads
Detail page: /admin/leads/[id]
```

Detail page gồm:

```text
Thông tin khách hàng
Danh sách conversation bên trái
Messages của conversation bên phải
Ghi chú chăm sóc bên dưới
```

### 7.4 API conversation summary

Bổ sung:

```text
last_message_content
```

để UI conversation list dễ đọc hơn.

## 8. Kết quả test local

Backend:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Kết quả:

```text
154 passed in 71.39s
```

Frontend:

```powershell
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
Route /admin/leads/[id] generated as dynamic route
```

## 9. Rủi ro còn tồn tại

### 9.1 Dữ liệu cũ có thể đã có nhiều Lead cùng phone

Vì chưa có unique constraint, dữ liệu cũ có thể trùng.

Hiện tại logic chỉ chọn Lead mới nhất cùng phone để link.

Nếu muốn chuẩn hóa lâu dài, cần audit dữ liệu trước khi thêm unique constraint.

### 9.2 Sale role chưa thấy Lead chưa phân công

Hiện tại rule phân quyền:

```text
sale chỉ thấy Lead assigned_to_id == sale.id
```

Lead tạo từ đăng ký mặc định chưa phân công, nên sale thường không thấy; admin sẽ thấy.

Nếu muốn sale thấy lead chưa phân công, cần đổi rule nghiệp vụ riêng.

### 9.3 `/admin/conversations` route vẫn tồn tại

Menu đã ẩn, nhưng file/API vẫn giữ để không phá backward compatibility.

Nếu muốn xóa hẳn route UI sau này thì làm ở version riêng.

### 9.4 Production đang dùng image `:main`

Sau khi merge vào main và GitHub Actions build image mới, cần pull lại production:

```bash
cd /opt/ocean-park-production
git pull origin main
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml pull
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml up -d
```

## 10. Hướng test thủ công sau deploy staging

1. Đăng ký user mới bằng số điện thoại chưa tồn tại.
2. Login admin.
3. Vào:

```text
/admin/leads
```

4. Kỳ vọng thấy khách mới ngay.
5. Click khách hàng.
6. Kỳ vọng chuyển sang:

```text
/admin/leads/{id}
```

7. Chat bằng account đó.
8. Reload detail page.
9. Kỳ vọng conversation/message hiện trong split layout.
10. Hỏi:

```text
Tôi cần căn 2PN khu Zenpark.
```

Kỳ vọng:

```text
AI tư vấn tiếp, không xin số điện thoại.
```

11. Hỏi:

```text
Tôi muốn gặp sale.
```

Kỳ vọng:

```text
AI handover.
```


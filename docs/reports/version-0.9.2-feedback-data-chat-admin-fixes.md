# Version 0.9.2 — Feedback fixes: data sync, chat UX, lead capture, fallback rules, RBAC

Ngày thực hiện: 2026-06-27

## Mục tiêu

Xử lý nhóm feedback vận hành hiện tại:

- Dữ liệu phân khu hiển thị chưa bám `cleaned_data` mới.
- Chat AI lặp lại các câu hỏi cũ, format khó đọc, mất lịch sử khi chuyển trang.
- Card đề xuất phân khu dưới chat không còn phù hợp.
- Khách để lại số điện thoại trong chat nhưng dashboard không sinh lead.
- Fallback rules trong admin chưa được áp dụng vào luồng chat.
- Sale account đang xem được quá nhiều lead/conversation.
- Danh sách khách hàng chưa có phân trang và contact form cho phép trùng lead.

## Những thay đổi đã làm

### 1. Đồng bộ database catalog với `cleaned_data`

File liên quan:

- `src/db/seed.py`

Thay đổi:

- Chuyển seed catalog từ kiểu “có dữ liệu rồi thì bỏ qua” sang kiểu sync/upsert.
- Mỗi lần backend start, hệ thống sẽ:
  - upsert `subdivisions` theo slug;
  - cập nhật `name`, `introduction`, `location`, `handover_status`, `display_order`, `is_published`;
  - xóa và tạo lại child rows của phân khu trong `apartment_specs`, `amenities`, `sales_policies`;
  - không xóa users, leads, conversations.

Lý do:

- `cleaned_data` là nguồn dữ liệu đã review mới nhất.
- Nếu DB đã seed từ bản cũ mà seed bỏ qua, UI/API/AI sẽ tiếp tục đọc dữ liệu stale.

Kết quả kiểm tra runtime Docker:

```text
subdivisions    = 12
apartment_specs = 84
amenities       = 175
sales_policies  = 89
```

Một số mẫu đối chiếu:

```text
the-bayfront      | Lumiere Orient Pearl | Dự kiến bàn giao Quý 3/2027
the-senique-hanoi | The Senique Hanoi    | Đang thi công / Dự kiến bàn giao 2026
the-zenpark       | The Zenpark          | Đã bàn giao

the-bayfront 2PN      | 58,8 - 63,3m2 | 5,7 - 7,2 tỷ
the-senique-hanoi 2PN | 54 - 81m2     | Đang cập nhật / Liên hệ CĐT
the-zenpark 2PN       | 64 - 70m2     | 3,0 - 3,5 tỷ
```

### 2. Sửa luồng chat không lặp lại toàn bộ câu hỏi cũ

File liên quan:

- `FE/src/components/chat-widget.tsx`
- `src/agents/nodes/llm_node.py`

Thay đổi:

- Frontend chỉ gửi tin nhắn mới nhất lên `/agent/chat`.
- Backend vẫn lưu và load lịch sử từ database để phục vụ context/profile.
- LLM node chỉ đưa câu hỏi mới nhất vào bước sinh câu trả lời cuối cùng.
- Prompt được bổ sung quy tắc: chỉ trả lời câu hỏi mới nhất, không tự lặp toàn bộ câu hỏi cũ.

Lý do:

- Trước đó frontend gửi toàn bộ lịch sử, backend lại load toàn bộ lịch sử từ DB, LLM node thêm toàn bộ user messages vào prompt. Vì vậy mỗi lượt mới AI có xu hướng trả lời lại các câu trước.

### 3. Cải thiện chat UX

File liên quan:

- `FE/src/components/chat-widget.tsx`

Thay đổi:

- Lưu `session_id` và `messages` vào `localStorage`.
- Khi user chuyển sang trang phân khu rồi quay lại, lịch sử chat vẫn còn.
- Bỏ phần render card “Phân khu phù hợp” bên dưới đoạn chat.
- Chỉ giữ đề xuất phân khu trong nội dung text của AI.
- Render response theo paragraph/list cơ bản và hỗ trợ `**bold**` để dễ đọc hơn.
- Sửa các text hardcoded trong widget về UTF-8 tiếng Việt chuẩn.

### 4. Tạo/cập nhật lead khi khách để lại số điện thoại trong chat

File liên quan:

- `src/api/agent_routes.py`

Thay đổi:

- Khi message mới nhất có số điện thoại Việt Nam, backend sẽ:
  - normalize phone;
  - tìm lead theo phone;
  - nếu chưa có thì tạo lead mới với `source="chat"`;
  - nếu đã có thì cập nhật summary/name khi phù hợp;
  - gắn `conversation.lead_id` vào lead;
  - trả lời xác nhận đã ghi nhận thông tin và chuyển Sales.

Lý do:

- Trước đó AI chỉ nói “vui lòng để lại thông tin” nhưng không có bridge nào từ chat sang bảng `leads`.

### 5. Áp dụng fallback rules vào luồng chat

File liên quan:

- `src/api/agent_routes.py`
- `src/api/admin.py`

Thay đổi:

- Sau khi lưu tin nhắn user, backend kiểm tra active fallback rules theo keyword.
- Rule có priority cao hơn được ưu tiên trước.
- Nếu match, trả `response_message` từ rule và lưu vào conversation như một message AI.

Lý do:

- Trước đó admin có CRUD fallback rule nhưng chat pipeline không dùng rule đó.

### 6. Siết quyền sale trong admin

File liên quan:

- `src/api/admin.py`

Thay đổi:

- Admin vẫn xem toàn bộ dashboard/leads/conversations.
- Sale chỉ xem được:
  - lead có `assigned_to_id == current_user.id`;
  - conversation đã gắn với lead được assign cho sale đó.
- Sale không được đổi `assigned_to_id` sang người khác.

Lý do:

- Phân quyền phải enforce ở backend, không chỉ ẩn bằng frontend.

### 7. Chống trùng lead từ contact form

File liên quan:

- `src/api/leads.py`

Thay đổi:

- Normalize số điện thoại.
- Nếu phone đã tồn tại, API cập nhật lead hiện có thay vì tạo dòng mới.
- Nếu phone chưa tồn tại, API tạo lead mới như trước.

### 8. Thêm phân trang cho admin leads

File liên quan:

- `FE/src/app/admin/(dashboard)/leads/page.tsx`
- `FE/src/app/admin.css`

Thay đổi:

- Trang leads dùng `limit=20` và `offset`.
- Thêm nút “Trang trước / Trang sau”.
- Search reset về trang đầu.

## Cách test

### Backend/API/Agent tests

```bash
.\.venv\Scripts\python.exe -m pytest tests\test_api tests\test_agents -q
```

Kết quả:

```text
54 passed in 38.99s
```

### Frontend build

```bash
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
Finished TypeScript
Generated static pages successfully
```

### Docker database sync

```bash
docker compose up -d --build backend
docker compose exec -T database psql -U ocean_app -d ocean_park -c "select 'subdivisions' as table_name, count(*) from subdivisions union all select 'apartment_specs', count(*) from apartment_specs union all select 'amenities', count(*) from amenities union all select 'sales_policies', count(*) from sales_policies;"
```

Kỳ vọng:

```text
subdivisions    | 12
apartment_specs | 84
amenities       | 175
sales_policies  | 89
```

### Manual test checklist

1. Vào trang `/phan-khu`, kiểm tra danh sách phân khu.
2. Mở chi tiết `the-bayfront`, `the-zenpark`, `the-senique-hanoi`, kiểm tra tên/trạng thái/giá 2PN.
3. Mở chat, hỏi 2-3 câu liên tiếp:
   - AI chỉ trả lời câu mới nhất, không lặp toàn bộ câu trước.
4. Chuyển sang trang phân khu rồi quay lại:
   - lịch sử chat vẫn còn.
5. Hỏi câu match fallback keyword đã tạo trong admin:
   - AI trả nội dung rule.
6. Gõ số điện thoại trong chat:
   - dashboard có lead mới hoặc cập nhật lead cũ;
   - conversation được gắn với lead.
7. Đăng nhập sale:
   - chỉ thấy lead/conversation được assign.
8. Submit contact form nhiều lần cùng số điện thoại:
   - không tạo nhiều lead trùng.

## Phần chưa triển khai trong version này

Các feedback sau là feature lớn, cần tách thành version riêng để không phá kiến trúc:

1. Đăng ký/đăng nhập cho user/client.
2. Dùng profile user để bỏ bước nhập tên/số điện thoại thủ công.
3. Phân quota chat theo loại user:
   - guest tối đa 5 tin;
   - registered tối đa 100 tin;
   - admin có thể mở giới hạn trong quản lý khách hàng.
4. Màn hình admin quản lý quota/tier của từng customer.
5. Migration/unique constraint chính thức cho lead phone sau khi đã xử lý dữ liệu trùng cũ.

Đề xuất version tiếp theo: `0.9.3-customer-auth-chat-quota`.

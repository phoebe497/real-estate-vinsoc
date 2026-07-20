# Report: Chuẩn hóa font, phân loại khách hàng và nâng cấp Dashboard Admin

Ngày thực hiện: 2026-06-30  
Phạm vi: Frontend Admin/Public font, CRM customer list, Dashboard analytics, Admin API.

---

## 1. Mục tiêu

Thực hiện các yêu cầu:

1. Đồng nhất font chữ toàn bộ frontend.
2. Phân loại khách hàng thành hai nhóm:
   - Đã đăng ký.
   - Khách vãng lai.
3. Bỏ cột `Nhu cầu` khỏi màn hình Khách hàng.
4. Thêm filter theo trạng thái lead.
5. Nâng cấp Dashboard Admin có khu vực analytics.
6. Bổ sung backend dashboard API hỗ trợ `range`, `start_date`, `end_date`, `group_by`.
7. Cập nhật Project Map cho AI Agent sau.

---

## 2. Phương án áp dụng

### 2.1 Font

Chọn font chuẩn toàn dự án:

```text
Roboto, Arial, Helvetica, sans-serif
```

Cách làm:

- Giữ Google Font Roboto trong `FE/src/app/layout.tsx`.
- Chuẩn hóa các khai báo CSS cũ đang dùng Georgia/Times/Arial rời rạc.
- Thêm block global typography ở cuối `FE/src/app/public-vinhomes.css` vì file này được import sau cùng trong layout.
- Ép các thành phần public, admin, chat, form, table, button, card dùng cùng font qua biến:

```css
--app-font: Roboto, Arial, Helvetica, sans-serif;
```

### 2.2 Phân loại khách hàng

Không tạo bảng mới.

Logic phân loại:

```text
Lead.customer_account_id != null => Đã đăng ký
Lead.customer_account_id == null => Khách vãng lai
```

Backend thêm query param cho API hiện có:

```http
GET /api/v1/admin/leads?customer_segment=registered
GET /api/v1/admin/leads?customer_segment=guest
GET /api/v1/admin/leads?customer_segment=all
```

Filter này hoạt động đồng thời với:

- `status`
- `search`
- `limit`
- `offset`

### 2.3 Bỏ cột Nhu cầu

Đã bỏ khỏi table list khách hàng:

- Không còn cột `Nhu cầu`.
- Không còn hiển thị `preferred_bedrooms` trong list/detail khách hàng.
- `summary` vẫn được giữ làm nguồn mô tả nhu cầu chính trong detail.

API response vẫn giữ field cũ để tránh phá backward compatibility, nhưng frontend không còn dùng.

### 2.4 Dashboard analytics

Mở rộng endpoint cũ:

```http
GET /api/v1/admin/dashboard?range=month&group_by=day
```

Không tạo nhiều endpoint mới.

Dashboard frontend render analytics bằng CSS thuần, không thêm chart library.

Các thống kê đã bổ sung:

- Lead mới theo thời gian.
- Khách đăng ký theo thời gian.
- Nguồn khách hàng.
- Trạng thái lead.
- Top sale được phân công nhiều lead nhất.
- Số conversation.
- Số message.
- Conversion funnel:
  - Customer Register
  - Lead
  - Đã liên hệ
  - Đã chốt

---

## 3. File đã sửa

Backend:

- `src/api/admin.py`
  - Thêm analytics cho `/admin/dashboard`.
  - Thêm filter `customer_segment` cho `/admin/leads`.
  - Giữ sale scope cho lead; top sale cũng được giới hạn theo role sale.
- `src/models/schemas.py`
  - Mở rộng `DashboardStatsResponse`.

Frontend:

- `FE/src/app/admin/(dashboard)/page.tsx`
  - Thay Dashboard cũ bằng dashboard KPI + analytics.
- `FE/src/app/admin/(dashboard)/leads/page.tsx`
  - Thêm tabs phân loại khách.
  - Thêm filter trạng thái.
  - Bỏ cột `Nhu cầu`.
- `FE/src/app/admin/(dashboard)/leads/[id]/page.tsx`
  - Dọn type không còn dùng `preferred_bedrooms`.
- `FE/src/app/public-vinhomes.css`
  - Thêm global font normalization.
  - Thêm CSS cho lead filter/tabs và dashboard charts.
- `FE/src/app/globals.css`
- `FE/src/app/admin.css`
- `FE/src/app/admin-extra.css`
- `FE/src/app/conversation.css`
  - Chuẩn hóa các khai báo font cũ về Roboto stack.

Tests:

- `tests/test_api/test_admin.py`
  - Bổ sung test filter khách đăng ký/khách vãng lai.
  - Bổ sung test dashboard analytics response.

Docs:

- `docs/PROJECT_MAP_FOR_AI_AGENTS.md`
  - Cập nhật tiến độ và thay đổi mới.
- `docs/reportsDevOps/admin-font-customer-filter-dashboard-analytics-report-2026-06-30.md`
  - Report hiện tại.

Dependency/local:

- Chạy `npm install` trong `FE/` để khôi phục dependency local bị thiếu `react-markdown` theo `package-lock.json`.

---

## 4. API đã thêm/thay đổi

### 4.1 `GET /api/v1/admin/leads`

Thêm query param:

```http
customer_segment=all|registered|guest
```

Ví dụ:

```http
GET /api/v1/admin/leads?customer_segment=registered&status=contacted&search=Quang
```

Ý nghĩa:

- `all`: tất cả lead.
- `registered`: chỉ lead có `customer_account_id`.
- `guest`: chỉ lead chưa có `customer_account_id`.

### 4.2 `GET /api/v1/admin/dashboard`

Thêm query params:

```http
range=day|week|month|year
group_by=day|week|month|year
start_date=YYYY-MM-DD
end_date=YYYY-MM-DD
```

Response vẫn giữ các field cũ:

- `total_leads`
- `new_leads`
- `contacted_leads`
- `qualified_leads`
- `active_fallback_rules`

Bổ sung các field analytics:

- `customer_accounts`
- `conversations`
- `messages`
- `closed_leads`
- `lead_trend`
- `customer_registration_trend`
- `source_breakdown`
- `status_breakdown`
- `top_sales`
- `conversion_funnel`

---

## 5. Ảnh hưởng database

Không có migration.

Không tạo bảng mới.

Không thay đổi schema hiện tại.

Logic mới sử dụng field đã có:

```text
Lead.customer_account_id
Lead.status
Lead.source
Lead.created_at
CustomerAccount.created_at
Conversation
Message
```

---

## 6. Cách test

### 6.1 Backend admin tests

Đã chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_api\test_admin.py -q
```

Kết quả:

```text
7 passed
```

### 6.2 Frontend build

Đã chạy:

```powershell
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
```

### 6.3 Manual test đề xuất

Local:

```powershell
docker compose up -d --build
```

Mở:

```text
http://localhost:3000/admin
```

Kiểm tra:

1. Login admin.
2. Vào Dashboard:
   - KPI vẫn hiển thị.
   - Chọn Ngày/Tuần/Tháng/Năm không reload toàn trang.
   - Charts không dùng dữ liệu giả.
3. Vào Khách hàng:
   - Tabs `Tất cả`, `Đã đăng ký`, `Khách vãng lai` hoạt động.
   - Filter trạng thái hoạt động.
   - Search kết hợp được với tabs và trạng thái.
   - Không còn cột `Nhu cầu`.
4. Vào chi tiết khách:
   - Vẫn thấy summary.
   - Vẫn xem được phiên chat/messages.
5. Kiểm tra font:
   - Dashboard.
   - Khách hàng.
   - Chi tiết khách hàng.
   - Chat.
   - Login/Register.
   - Sidebar/Header/Card/Form/Button/Table.

---

## 7. Kết quả kiểm tra font

Đã search các font cũ:

```powershell
rg "Georgia|Times New Roman|font-family: Arial|font: .*Arial" FE\src\app FE\src\components FE\src\lib
```

Kết quả không còn Georgia/Times. Các dòng còn lại đều dùng Roboto stack.

---

## 8. Vấn đề còn tồn tại

Khi chạy toàn bộ test:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Hiện đang dừng ở lỗi import cũ:

```text
ImportError: cannot import name 'search_knowledge_chunks' from 'src.services.vinhomes_data'
```

Lỗi này nằm ở `tests/test_agents/test_rag_scenario2.py`, không phát sinh từ thay đổi font/customer/dashboard lần này.

Đề xuất xử lý riêng ở phiên sau:

- Kiểm tra test RAG cũ còn phù hợp không.
- Hoặc khôi phục/export `search_knowledge_chunks`.
- Hoặc cập nhật test theo retrieval service hiện tại.

---

## 9. Đề xuất cải tiến tiếp theo

1. Chuẩn hóa enum status lead ở backend để tránh mỗi nơi tự dùng string.
2. Thêm tổng count thật cho pagination khách hàng thay vì dựa vào số item page hiện tại.
3. Nếu dữ liệu tăng lớn, chuyển dashboard aggregation từ Python-side sang SQL aggregation tối ưu theo PostgreSQL.
4. Thêm e2e test cho Admin:
   - login;
   - filter khách đăng ký;
   - mở chi tiết khách;
   - xem conversation.
5. Tách chart component nhỏ hơn nếu Dashboard tiếp tục mở rộng.

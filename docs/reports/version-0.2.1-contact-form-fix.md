# Báo cáo phiên bản v0.2.1 — Sửa lỗi form nhận tư vấn

**Ngày hoàn thành:** 22/06/2026  
**Loại phiên bản:** Patch/Bugfix  
**Phụ thuộc:** `v0.2.0`

## 1. Mô tả lỗi

Khách hàng nhập thông tin và nhấn **Nhận tư vấn**. Frontend hiển thị:

```text
Chưa thể gửi thông tin. Vui lòng kiểm tra lại số điện thoại.
```

Tuy nhiên Lead vẫn xuất hiện trong Sales Dashboard.

## 2. Quá trình xác định nguyên nhân

Log Backend cho thấy request thực tế thành công:

```text
POST /api/v1/contact HTTP/1.1 201 Created
```

Điều này chứng minh:

- Số điện thoại đã vượt qua validation.
- Database đã lưu Lead.
- Backend đã trả response thành công.
- Lỗi xảy ra ở Client sau khi nhận response.

Trong event handler cũ:

```tsx
const response = await fetch(...);
setState(response.ok ? "success" : "error");
if (response.ok) event.currentTarget.reset();
```

Sau một thao tác bất đồng bộ `await`, `event.currentTarget` của React event không còn được đảm bảo giữ tham chiếu tới form. Khi gọi `reset()`, Client phát sinh exception và đi vào `catch`, làm trạng thái bị đổi thành `error` dù API đã trả HTTP 201.

## 3. Phương án áp dụng

Lưu tham chiếu form trước khi bắt đầu request:

```tsx
const formElement = event.currentTarget;
const form = new FormData(formElement);
```

Sau đó tách rõ ba trường hợp:

1. HTTP không thành công: hiển thị lỗi và kết thúc.
2. HTTP thành công: reset form bằng tham chiếu đã lưu rồi hiển thị thành công.
3. Lỗi kết nối hoặc exception thực sự: đi vào `catch`.

Luồng mới:

```tsx
if (!response.ok) {
  setState("error");
  return;
}
formElement.reset();
setState("success");
```

## 4. File thay đổi

- `FE/src/components/contact-form.tsx`
- `FE/package.json`
- `pyproject.toml`
- `src/config.py`
- `src/main.py`

Version Backend và Frontend được đồng bộ thành `0.2.1`.

## 5. Hướng dẫn áp dụng

Nếu chạy Docker:

```powershell
docker compose build frontend
docker compose up -d frontend
```

Nếu chạy Frontend local:

```powershell
cd FE
npm run dev
```

Sau khi cập nhật container, tải lại trang bằng `Ctrl + F5` để tránh JavaScript bundle cũ trong cache.

## 6. Hướng dẫn kiểm thử

### 6.1. Production build

```powershell
cd FE
npm run build
```

Build phải hoàn tất mà không có TypeScript error.

### 6.2. Kiểm thử thủ công

1. Mở `http://localhost:3000/lien-he`.
2. Nhập số điện thoại hợp lệ, ví dụ `0912345678`.
3. Nhấn **Nhận tư vấn**.
4. Xác nhận form được xóa nội dung.
5. Xác nhận hiển thị thông báo:

```text
Đã ghi nhận thông tin. Sale sẽ liên hệ Anh/Chị sớm.
```

6. Đăng nhập Dashboard và xác nhận Lead xuất hiện đúng một lần.

Kiểm tra trường hợp lỗi:

1. Nhập số điện thoại không đủ 10 chữ số.
2. Nhấn **Nhận tư vấn**.
3. Xác nhận form không bị reset và hiển thị thông báo lỗi.

### 6.3. Kiểm tra Backend log

```powershell
docker compose logs --tail 50 backend
```

Request hợp lệ phải có:

```text
POST /api/v1/contact HTTP/1.1 201 Created
```

## 7. Kết quả mong đợi

- Lead hợp lệ được lưu một lần.
- Client hiển thị trạng thái thành công.
- Form được reset sau HTTP 201.
- Lỗi validation vẫn giữ dữ liệu để khách sửa.
- Không thay đổi schema Database hoặc API contract.

## 8. Kết quả xác minh

- Backend log xác nhận form hợp lệ trả HTTP `201 Created`.
- Backend test suite: **14 tests passed**.
- Next.js `0.2.1` production build thành công, không có TypeScript error.
- Backend, Frontend và PostgreSQL containers khởi động thành công sau khi cập nhật.
- Kiểm thử trình duyệt tự động không thực hiện được do kết nối browser của môi trường phát triển bị từ chối; cần thực hiện checklist thủ công tại mục 6.2 để xác nhận trạng thái hiển thị cuối cùng.

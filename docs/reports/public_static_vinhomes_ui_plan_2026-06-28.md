# Kế hoạch triển khai Public Static UI giống vinhomeoceanpark.com.vn

Ngày tạo: 2026-06-28  
Mục tiêu: xây dựng giao diện public cho khách nhìn giống `https://vinhomeoceanpark.com.vn/`, trong khi vẫn giữ nguyên backend, database, AI Agent, dashboard, đăng ký/đăng nhập và quy trình deploy hiện tại.

---

## 1. Bối cảnh và yêu cầu

Mentor yêu cầu giao diện public phải giống trang `vinhomeoceanpark.com.vn`. Vì vậy phần khách nhìn thấy có thể là giao diện tĩnh, ưu tiên giống về visual/layout.

Tuy nhiên, các phần lõi của dự án không được phá:

- Backend/API hiện tại.
- Database và cleaned data.
- AI Agent/chat.
- Dashboard admin/sale.
- Đăng ký/đăng nhập khách hàng.
- Lead/contact flow.
- Docker, staging, production deploy.

Kết luận kỹ thuật: yêu cầu này khả thi nếu triển khai theo hướng **static public UI có kiểm soát**, không copy nguyên hệ thống WordPress vào app.

---

## 2. Hiện trạng đã kiểm tra

Ảnh đã được tải về local trong:

```txt
FE/public/media_files
```

Thống kê hiện tại:

```txt
Số lượng file: 774
Tổng dung lượng: khoảng 244MB
```

Cấu trúc thư mục media hiện có:

```txt
FE/public/media_files
├─ building
├─ project
├─ subzone
└─ zone
```

Vì ảnh nằm trong `FE/public`, sau khi deploy online có thể truy cập bằng URL dạng:

```txt
/media_files/...
```

Ví dụ:

```tsx
<img src="/media_files/project/vinhomes-ocean-park-gia-lam/ten-anh.jpg" />
```

Điều này phù hợp với Next.js/Docker deploy.

---

## 3. Nguyên tắc triển khai

### 3.1. Chỉ thay public UI

Chỉ chỉnh các phần public như:

- Trang chủ `/`
- Trang `/chung-cu`
- Trang `/phan-khu/...`
- Header public
- Footer public
- Section hotline/contact
- Style public

Không chỉnh các phần:

- `src/` backend.
- Database models/migrations.
- AI Agent routes/services.
- Admin dashboard logic.
- Customer auth logic.
- Docker/deploy workflow, trừ khi cần build static asset.

---

### 3.2. Giao diện giống mẫu, nhưng code phải là của app mình

Không nên giữ nguyên toàn bộ HTML WordPress dạng `dangerouslySetInnerHTML` lâu dài.

Hướng tốt hơn:

- Dùng ảnh đã tải về trong `FE/public/media_files`.
- Dùng React components để dựng lại section giống website mẫu.
- Dùng CSS riêng cho public UI.
- Giữ lại cảm giác visual của trang mẫu: hero lớn, màu xanh navy/vàng, bảng giá, card phân khu, CTA, hotline floating.

Nói ngắn gọn: **copy visual, không copy runtime WordPress**.

---

### 3.3. CSS public phải cô lập

Public style phải có namespace riêng để không ảnh hưởng:

- Admin dashboard.
- Login/register.
- ChatWidget.
- Form React.
- Table/button/input trong hệ thống quản trị.

Quy ước đề xuất:

```css
.public-vinhomes-page { ... }
.public-vinhomes-page .hero { ... }
.public-vinhomes-page .price-table { ... }
.public-vinhomes-page .contact-section { ... }
```

Tránh selector toàn cục kiểu:

```css
body {}
a {}
input {}
button {}
h1 {}
```

Nếu bắt buộc dùng CSS port từ website mẫu, cần bọc vào namespace hoặc tách riêng để chỉ public pages load.

---

### 3.4. Form nhìn giống mẫu nhưng submit vào backend thật

Form public có thể nhìn giống Contact Form 7 của website mẫu, nhưng không dùng:

```html
<form action="/#wpcf7..." />
```

Thay vào đó, form phải gọi API hiện tại của dự án để lưu lead.

Luồng đúng:

```txt
Khách nhập form public
→ FE validate số điện thoại
→ gọi API lead/contact hiện tại
→ lưu vào database
→ dashboard admin/sale nhìn thấy
```

Như vậy mentor nhìn thấy giao diện giống mẫu, còn hệ thống vẫn hoạt động thật.

---

### 3.5. ChatWidget giữ nguyên logic

Chat AI vẫn là hệ thống của dự án.

Public UI chỉ thay phần nền/trang/section xung quanh. Không thay logic:

- session chat.
- customer auth.
- lead capture từ chat.
- AI Agent.
- fallback rule.
- conversation dashboard.

Nếu CSS public làm ảnh hưởng ChatWidget thì phải fix bằng namespace/z-index riêng.

---

### 3.6. Route public phải được kiểm soát

Hiện có cả route động:

```txt
FE/src/app/phan-khu/[slug]/page.tsx
```

và nhiều route tĩnh:

```txt
FE/src/app/phan-khu/the-zenpark/page.tsx
FE/src/app/phan-khu/the-zurich/page.tsx
...
```

Với mục tiêu static UI giống mẫu, route tĩnh có thể dùng cho demo/public marketing. Tuy nhiên cần kiểm soát để không làm lệch dữ liệu.

Đề xuất:

- Public marketing page có thể tĩnh.
- Các CTA, form, chat vẫn gọi hệ thống thật.
- Nếu một page tĩnh có thông tin giá/chính sách, cần ghi nhận rằng đây là nội dung marketing tĩnh.
- Sau này nếu cần production nghiêm túc, chuyển dần về route động/data-driven.

---

## 4. Kiến trúc FE đề xuất

### 4.1. Public layout

Giữ mô hình:

```txt
PublicLayoutWrapper
├─ PublicHeader
├─ children
├─ PublicFooter
└─ ChatWidget
```

Admin route `/admin` không load public layout.

---

### 4.2. Component public nên tạo

Đề xuất tạo nhóm component:

```txt
FE/src/components/public/
├─ public-header.tsx
├─ public-footer.tsx
├─ hero-slider.tsx
├─ project-overview.tsx
├─ price-table-static.tsx
├─ subdivision-card-grid.tsx
├─ utility-section.tsx
├─ contact-cta.tsx
├─ floating-contact-buttons.tsx
└─ public-contact-form.tsx
```

Các component này chỉ phục vụ public marketing UI.

---

### 4.3. Data tĩnh cho public page

Để tránh nhồi HTML khổng lồ trong TSX, nên đưa dữ liệu public tĩnh vào file riêng:

```txt
FE/src/data/public-vinhomes.ts
```

Ví dụ:

```ts
export const publicHomeSlides = [
  {
    title: "VINHOMES OCEAN PARK",
    subtitle: "Đại đô thị biển hồ giữa lòng Hà Nội",
    image: "/media_files/project/...",
    href: "/chung-cu",
  },
];
```

Lợi ích:

- Dễ sửa nội dung.
- Dễ thay ảnh.
- Không làm page TSX quá lớn.
- Dễ review khi commit.

---

### 4.4. CSS public

Tạo file:

```txt
FE/src/app/public-vinhomes.css
```

hoặc:

```txt
FE/src/styles/public-vinhomes.css
```

Nguyên tắc:

- Chỉ import ở public layout hoặc public pages.
- Tất cả selector bọc trong `.public-vinhomes-page`.
- Không import vào admin.

---

## 5. Kế hoạch thực hiện theo phiên bản

## Version UI-Static 1.0 — Làm sạch nền public UI

Mục tiêu:

- Giữ hệ thống hiện tại ổn định.
- Cô lập public layout khỏi admin.
- Chuẩn bị nền để build UI giống mẫu.

Công việc:

1. Kiểm tra lại `PublicLayoutWrapper`.
2. Đảm bảo `/admin` không bị public CSS ảnh hưởng.
3. Sửa lỗi encoding tiếng Việt ở Header public.
4. Xác nhận ChatWidget vẫn hiển thị trên public page.
5. Xác nhận login/register/admin vẫn không bị đổi logic.

Test:

```bash
cd FE
npm run build
```

Kiểm tra thủ công:

- `/`
- `/chung-cu`
- `/phan-khu/the-zenpark`
- `/dang-nhap`
- `/dang-ky`
- `/admin`

---

## Version UI-Static 1.1 — Rebuild trang chủ giống mẫu

Mục tiêu:

- Trang chủ nhìn giống `vinhomeoceanpark.com.vn`.
- Dùng ảnh local trong `/media_files`.
- Không dùng form WordPress raw.

Công việc:

1. Tạo component hero/slider.
2. Tạo section giới thiệu dự án.
3. Tạo section bảng giá/loại hình.
4. Tạo section phân khu nổi bật.
5. Tạo CTA/hotline floating.
6. Dùng ảnh từ `FE/public/media_files/project/...`.

Test:

- Build FE pass.
- Trang `/` load ảnh từ local.
- Tắt mạng ngoài vẫn không mất ảnh chính.
- ChatWidget vẫn hoạt động.
- Không có link ngoài không kiểm soát.

---

## Version UI-Static 1.2 — Rebuild `/chung-cu`

Mục tiêu:

- Trang chung cư giống layout website mẫu.
- Nội dung marketing có thể tĩnh.
- CTA/form vẫn dùng hệ thống lead thật.

Công việc:

1. Hero chung cư.
2. Section mô tả.
3. Bảng diện tích/giá tham khảo.
4. Gallery ảnh.
5. PublicContactForm hoặc CTA gọi `ContactForm`.

Test:

- `/chung-cu` load đúng.
- Form gửi lead vào dashboard.
- Không submit về route `wpcf7`.

---

## Version UI-Static 1.3 — Rebuild các trang phân khu static

Mục tiêu:

- Các trang phân khu nhìn giống website mẫu.
- Ảnh lấy local.
- Route public phục vụ mentor/demo tốt.

Danh sách route ưu tiên:

```txt
/phan-khu/the-zenpark
/phan-khu/the-zurich
/phan-khu/the-beverly
/phan-khu/masteri-waterfront
/phan-khu/the-pavilion
/phan-khu/the-sapphire
/phan-khu/the-ocean-view
/phan-khu/the-london
/phan-khu/the-paris
/phan-khu/masteri-lakeside
/phan-khu/the-senique-hanoi
```

Công việc:

1. Tạo template `PublicSubdivisionStaticPage`.
2. Tạo data config theo từng slug.
3. Map ảnh local từ `media_files/zone`, `media_files/subzone`, `media_files/building`.
4. Thay HTML raw bằng component.
5. Gắn CTA/contact thật.

Test:

- Build pass.
- Từng route load không 404.
- Ảnh hiển thị online/local.
- Chat vẫn hoạt động.
- Form lưu lead.

---

## Version UI-Static 1.4 — Kiểm tra deploy/Docker

Mục tiêu:

- Đảm bảo static media không làm hỏng Docker/staging.

Công việc:

1. Kiểm tra Docker build frontend.
2. Kiểm tra image size tăng bao nhiêu do 244MB media.
3. Nếu image quá lớn, cân nhắc:
   - nén ảnh,
   - dùng WebP,
   - đưa ảnh lên CDN/Cloudflare R2 sau này,
   - chỉ ship ảnh thật sự dùng.

Test:

```bash
docker compose up -d --build
```

Trên staging:

```bash
bash scripts/deploy/verify_single_ec2.sh
```

Kiểm tra:

- `/`
- `/chung-cu`
- `/phan-khu/the-zenpark`
- `/admin`
- `/dang-nhap`
- Chat AI
- Lead form

---

## 6. Rủi ro và cách kiểm soát

| Rủi ro | Mức độ | Cách kiểm soát |
|---|---:|---|
| UI giống mẫu nhưng form không lưu lead | Cao | Form public phải gọi API backend thật |
| CSS public phá dashboard/chat | Cao | Namespace `.public-vinhomes-page`, admin không load public CSS |
| Ảnh quá nặng làm Docker image lớn | Trung bình/cao | Nén ảnh, chỉ dùng ảnh cần thiết, cân nhắc CDN sau |
| Route tĩnh lệch dữ liệu AI/database | Trung bình | Chấp nhận cho demo, sau đó đồng bộ data hoặc chuyển data-driven |
| HTML raw khó bảo trì | Cao | Chuyển sang React component + data config |
| Link ngoài làm khách rời app | Trung bình | Audit link, đổi sang route nội bộ hoặc CTA thật |

---

## 7. Tiêu chí hoàn thành

Một phiên bản được coi là đạt khi:

1. Giao diện public nhìn giống website mẫu ở các phần chính.
2. `npm run build` pass.
3. Docker build/deploy không lỗi.
4. Admin dashboard không bị ảnh hưởng.
5. Login/register không bị ảnh hưởng.
6. ChatWidget/AI vẫn hoạt động.
7. Form tư vấn lưu lead vào dashboard.
8. Ảnh load từ local `/media_files/...`, không phụ thuộc website ngoài cho ảnh chính.

---

## 8. Kết luận

Phương án này khả thi và phù hợp với yêu cầu mentor.

Ta có thể để public UI giống `vinhomeoceanpark.com.vn` phục vụ khách/mentor, nhưng vẫn giữ nguyên kiến trúc lõi của dự án. Điểm quan trọng là không để WordPress HTML/CSS raw kiểm soát toàn app. Public UI nên được rebuild thành React components, dùng ảnh local, CSS cô lập và form/chat nối vào hệ thống thật.

Hướng triển khai đề xuất: bắt đầu từ Version UI-Static 1.0 để làm sạch nền và tránh ảnh hưởng deploy, sau đó dựng lại trang chủ, `/chung-cu`, rồi các trang phân khu theo template.

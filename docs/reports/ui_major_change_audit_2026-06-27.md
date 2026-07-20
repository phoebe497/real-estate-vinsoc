# Báo cáo rà soát sau thay đổi lớn giao diện

Ngày tạo: 2026-06-27  
Phạm vi: Frontend public UI, layout, route, liên kết với backend/database/chat/lead hiện tại.  
Mục tiêu: phân tích thay đổi UI mới ảnh hưởng thế nào tới kiến trúc dự án, dữ liệu, trải nghiệm người dùng và khả năng deploy.

---

## 1. Tóm tắt kết luận

Dự án hiện tại **vẫn build frontend thành công**, nghĩa là thay đổi giao diện chưa làm vỡ production build ở mức TypeScript/Next.js.

Tuy nhiên, thay đổi UI mới đang đi theo hướng **copy/port HTML + CSS từ WordPress/Enfold vào Next.js** bằng `dangerouslySetInnerHTML`, thay vì rebuild thành component React/data-driven. Đây là thay đổi lớn, có thể giúp giao diện nhìn giống website mẫu rất nhanh, nhưng tạo ra một số rủi ro quan trọng:

- Nhiều trang public mới đang dùng dữ liệu hardcode, không lấy từ database/API.
- Các route tĩnh `/phan-khu/<slug>` mới có thể đè lên route động `/phan-khu/[slug]`, làm mất trang chi tiết lấy dữ liệu từ backend với cùng slug.
- Form liên hệ trong HTML WordPress không dùng API lead hiện tại nên có khả năng không lưu khách hàng.
- Nội dung, giá bán, chính sách và link ngoài có thể lệch với cleaned_data/database/AI Agent.
- CSS/HTML rất lớn, khó bảo trì, khó review và có rủi ro bảo mật/performance.

Đánh giá tổng quan: giao diện public đã được nâng cấp mạnh về mặt trình bày, nhưng hiện chưa đồng nhất với kiến trúc sản phẩm đã xây trước đó. Nếu giữ hướng này, cần có bước chuẩn hóa lại để UI mới vẫn lấy dữ liệu từ backend và không làm lệch AI/database.

---

## 2. Những thay đổi chính phát hiện được

### 2.1. Layout gốc đã đổi cách bọc toàn bộ app

File liên quan:

- `FE/src/app/layout.tsx`
- `FE/src/components/public-layout.tsx`
- `FE/src/components/header.tsx`
- `FE/src/app/public-styles.tsx`

Hiện `layout.tsx` bọc app bằng:

- `AuthProvider`
- `PublicLayoutWrapper`

`PublicLayoutWrapper` kiểm tra pathname:

- Nếu là `/admin`, trả về children trực tiếp.
- Nếu là public route, render thêm `PublicStyles`, `Header`, `Footer`, `ChatWidget`.

Điểm tích cực:

- Admin được tách khỏi public layout tương đối rõ.
- Chat widget vẫn xuất hiện trên public pages.
- Customer auth context vẫn dùng chung toàn app.

Điểm cần chú ý:

- Public CSS được inject qua `dangerouslySetInnerHTML`, không phải import CSS chuẩn.
- Header hiện có một số text bị lỗi encoding tiếng Việt như `Trang chá»§`, `ÄÄƒng nháº­p`, `ÄÄƒng xuáº¥t`.
- Public layout có thể ảnh hưởng đến toàn bộ public pages, bao gồm chat widget.

---

### 2.2. Nhiều trang public mới dùng HTML WordPress nhúng trực tiếp

Các file có `dangerouslySetInnerHTML`:

- `FE/src/app/page.tsx`
- `FE/src/app/chung-cu/page.tsx`
- `FE/src/app/public-styles.tsx`
- `FE/src/app/phan-khu/masteri-lakeside/page.tsx`
- `FE/src/app/phan-khu/masteri-waterfront/page.tsx`
- `FE/src/app/phan-khu/the-beverly/page.tsx`
- `FE/src/app/phan-khu/the-london/page.tsx`
- `FE/src/app/phan-khu/the-ocean-view/page.tsx`
- `FE/src/app/phan-khu/the-paris/page.tsx`
- `FE/src/app/phan-khu/the-pavilion/page.tsx`
- `FE/src/app/phan-khu/the-sapphire/page.tsx`
- `FE/src/app/phan-khu/the-senique-hanoi/page.tsx`
- `FE/src/app/phan-khu/the-zenpark/page.tsx`
- `FE/src/app/phan-khu/the-zurich/page.tsx`

Nhận xét:

- Nội dung HTML chứa class/markup của WordPress, Enfold, Contact Form 7, Popup Maker.
- Có nhiều link ảnh và CSS trỏ tới `https://vinhomeoceanpark.com.vn/...`.
- Có form `wpcf7`, popup `pum-*`, field name kiểu `text-833`, `tel-239`, `textarea-332`.
- Có nhiều link tuyệt đối sang website ngoài.

Tác động:

- Các trang này hiển thị theo HTML tĩnh, không tự động đồng bộ với database.
- Các form trong HTML gần như chắc chắn không gọi API lead hiện tại nếu không có JS adapter riêng.
- Các popup/slider WordPress có thể không hoạt động đúng vì thiếu JavaScript runtime/plugin của WordPress.

---

## 3. Route và dữ liệu: điểm rủi ro lớn nhất

Hiện frontend có cả:

- Route động: `FE/src/app/phan-khu/[slug]/page.tsx`
- Route tĩnh mới:
  - `/phan-khu/the-zenpark`
  - `/phan-khu/the-zurich`
  - `/phan-khu/the-beverly`
  - `/phan-khu/masteri-waterfront`
  - `/phan-khu/the-pavilion`
  - `/phan-khu/the-sapphire`
  - `/phan-khu/the-ocean-view`
  - `/phan-khu/the-london`
  - `/phan-khu/the-paris`
  - `/phan-khu/masteri-lakeside`
  - `/phan-khu/the-senique-hanoi`

Kết quả `npm run build` xác nhận Next.js tạo route như sau:

```text
○ /phan-khu/masteri-lakeside
○ /phan-khu/masteri-waterfront
○ /phan-khu/the-beverly
○ /phan-khu/the-london
○ /phan-khu/the-ocean-view
○ /phan-khu/the-paris
○ /phan-khu/the-pavilion
○ /phan-khu/the-sapphire
○ /phan-khu/the-senique-hanoi
○ /phan-khu/the-zenpark
○ /phan-khu/the-zurich
ƒ /phan-khu/[slug]
```

Điều này có nghĩa:

- Với slug đã có route tĩnh, Next.js sẽ dùng page tĩnh.
- Route động `/phan-khu/[slug]` chỉ còn dùng cho các slug chưa có page tĩnh.
- Các page tĩnh không gọi `getSubdivision(slug)`, không dùng API `/subdivisions/{slug}` và không dùng `ContactForm`.

Đây là điểm lệch quan trọng so với thiết kế ban đầu: UI chi tiết phân khu trước đây là data-driven, còn UI mới đang là content-driven/hardcoded.

---

## 4. Đối chiếu với backend/database hiện tại

Backend hiện vẫn có các phần liên quan:

- API catalog/database:
  - `src/api/catalog.py`
  - `src/api/routes.py`
  - `src/db/seed.py`
  - `src/services/vinhomes_data.py`
- FE API client:
  - `FE/src/lib/api.ts`
  - `getSubdivisions()`
  - `getSubdivision(slug)`
- FE component data-driven:
  - `FE/src/components/subdivision-grid.tsx`
  - `FE/src/components/contact-form.tsx`
  - `FE/src/app/phan-khu/[slug]/page.tsx`

Nhận xét:

- Backend/database vẫn coi catalog/subdivision là nguồn dữ liệu quan trọng.
- AI Agent/recommender cũng đang dựa vào cleaned data, slug, knowledge chunks và rule matching.
- UI mới lại đưa nhiều nội dung phân khu/giá/chính sách vào HTML tĩnh.

Rủi ro:

- Người dùng đọc thông tin ở page tĩnh, nhưng AI trả lời theo cleaned_data/database. Hai nguồn này có thể không giống nhau.
- Admin/database cập nhật nhưng page public không thay đổi.
- Nếu cleaned_data đã được cập nhật mới, UI tĩnh vẫn có thể hiển thị dữ liệu cũ.

---

## 5. Lead/contact form

Hệ thống hiện có `ContactForm` React dùng API backend để tạo lead.

Tuy nhiên các page public mới có nhiều form WordPress dạng:

```html
<form action="/...#wpcf7-..." method="post" class="wpcf7-form init">
```

Các form này:

- Không gọi `POST /api/v1/leads/contact` hoặc endpoint lead hiện tại.
- Không map field sang schema backend.
- Không có xử lý success/error theo app hiện tại.
- Có khả năng submit về route Next hiện tại và không tạo lead.

Tác động trực tiếp:

- Khách điền form trên page tĩnh có thể không xuất hiện trong dashboard.
- Dashboard/lead pipeline sẽ không đầy đủ nếu user dùng form WordPress thay vì chat/contact-form React.

Khuyến nghị:

- Không dùng form WordPress raw trong production.
- Thay toàn bộ form HTML bằng component React `ContactForm`.
- Nếu muốn giữ UI form giống mẫu, chỉ giữ style, còn submit phải qua API backend hiện tại.

---

## 6. Chat widget và session

Điểm tốt:

- `ChatWidget` vẫn được render trong `PublicLayoutWrapper`, nên public pages vẫn có chat.
- Hệ thống backend hiện có logic customer auth/session/conversation/lead khá đầy đủ.

Rủi ro:

- CSS WordPress/Enfold rất rộng, có thể override style của chat widget.
- Các page tĩnh có thể đưa khách sang link ngoài hoặc route không tồn tại, làm đứt luồng chat trong app.
- Nội dung phân khu hardcode có thể khác AI Agent, khiến khách thấy UI nói một kiểu, AI trả lời một kiểu.

---

## 7. External assets, performance và deploy

Phát hiện:

- Có 1 file local trong `FE/public/css/vinhomes-style.css`, dung lượng khoảng `1,111,129 bytes`.
- `public-styles.tsx` vẫn inject nhiều CSS/link/style theo dạng raw HTML.
- Nhiều ảnh vẫn tải từ `https://vinhomeoceanpark.com.vn/wp-content/uploads/...`.

Rủi ro:

- Website phụ thuộc vào domain ngoài. Nếu domain ngoài chậm/chặn/down, UI của app bị ảnh hưởng.
- Không tận dụng tốt Next Image optimization.
- Bundle/page HTML có thể rất nặng vì mỗi page chứa nguyên khối HTML dài.
- Caching/CDN khó kiểm soát hơn.

Khuyến nghị:

- Chuyển asset quan trọng về `FE/public`.
- Tách CSS thật sự cần dùng, bỏ phần CSS không liên quan.
- Dùng component React + data JSON thay vì string HTML cực lớn.

---

## 8. SEO, accessibility và encoding

Phát hiện:

- Một số text trong Header bị lỗi encoding tiếng Việt.
- HTML WordPress có nhiều `aria-hidden`, duplicated attributes, popup `aria-modal="false"`.
- Có thể có nhiều heading/schema/metadata không còn khớp dự án hiện tại.
- Trang chủ có nội dung/link về Ocean Park 2/3, Masteri Grand Coast, Masteri Era Landmark... trong khi scope dự án/data hiện tại có thể không bao phủ đầy đủ.

Tác động:

- UX tiếng Việt bị giảm chất lượng ở menu.
- SEO có thể bị nhiễu nếu nội dung không đúng phạm vi sản phẩm.
- Accessibility chưa đảm bảo.

---

## 9. Source hygiene

Các file untracked/tiện ích mới phát hiện trong FE:

- `FE/analyze_css.py`
- `FE/convert.py`
- `FE/extract_css.py`
- `FE/fetch_css.py`
- `FE/test_css.py`
- `temp.json`
- `FE/public/css/vinhomes-style.css`

Nhận xét:

- Đây có vẻ là script hỗ trợ chuyển đổi/crawl CSS/HTML.
- Nếu cần giữ, nên đưa vào folder `tools/` hoặc `scripts/` và viết README ngắn.
- Nếu không cần trong production, nên loại khỏi commit để tránh repo phình và gây nhiễu.

---

## 10. Kết quả kiểm thử đã chạy

### Frontend build

Lệnh:

```bash
cd FE
npm run build
```

Kết quả:

```text
✓ Compiled successfully
✓ Finished TypeScript
✓ Generating static pages (25/25)
```

Kết luận:

- Build FE pass.
- Thay đổi UI không gây lỗi compile.
- Route output xác nhận tồn tại song song route tĩnh và route động `/phan-khu/[slug]`.

### Git status

Có một lần kiểm tra `git status` sau đó báo lỗi:

```text
fatal: detected dubious ownership in repository
```

Đây là vấn đề môi trường sandbox Git, không phải lỗi code. Tôi không tự chỉnh `git config --global safe.directory` vì không cần thiết cho audit và không nên thay đổi global config khi chưa cần.

---

## 11. Đánh giá mức độ ảnh hưởng

| Hạng mục | Mức độ | Đánh giá |
|---|---:|---|
| Build frontend | Thấp | Đã pass build |
| Giao diện public | Trung bình/tốt về visual | UI có thể đẹp hơn nhanh, nhưng phụ thuộc HTML/CSS raw |
| Đồng bộ database | Cao | Page tĩnh không lấy dữ liệu từ DB/API |
| Lead form | Cao | Form WordPress không lưu lead theo backend hiện tại |
| AI consistency | Cao | UI hardcode có thể lệch cleaned_data/AI Agent |
| Admin | Thấp/trung bình | Admin được tách layout, nhưng cần kiểm tra CSS global thêm |
| Maintainability | Cao | HTML string khổng lồ rất khó bảo trì |
| Security/CSP | Trung bình/cao | `dangerouslySetInnerHTML`, link/style raw, external assets |
| Performance | Trung bình/cao | HTML/CSS lớn, nhiều remote assets |

---

## 12. Đề xuất hướng xử lý tiếp theo

### Giai đoạn 1: Khóa rủi ro ngay

1. Sửa lỗi encoding tiếng Việt trong `Header`.
2. Audit toàn bộ link nội bộ/ngoài:
   - Link nào giữ trong app.
   - Link nào sang ngoài.
   - Link nào đang 404 như `/biet-thu`.
3. Thay form WordPress bằng `ContactForm` React hoặc viết adapter submit về API backend.
4. Quyết định rõ source of truth:
   - Nếu DB/cleaned_data là nguồn chuẩn, page public phải đọc từ đó.
   - Nếu HTML tĩnh là nguồn chuẩn, cần cập nhật AI/database theo HTML, nhưng hướng này không bền.

### Giai đoạn 2: Chuẩn hóa route phân khu

Có 2 phương án:

#### Phương án A: Giữ page tĩnh tạm thời

- Giữ các route tĩnh để demo visual.
- Gắn warning nội bộ rằng thông tin chưa đồng bộ DB.
- Ưu tiên sửa form và link.

Phù hợp khi cần show mentor nhanh.

#### Phương án B: Rebuild đúng kiến trúc

- Chuyển từng page tĩnh thành React component/data-driven.
- Page `/phan-khu/[slug]` vẫn là route chính.
- Dùng template UI mới nhưng dữ liệu lấy từ API/database.
- Nội dung dài như mô tả, bảng giá, tiện ích có thể đưa vào DB/JSON seed.

Phù hợp để đi production/staging nghiêm túc.

Khuyến nghị của tôi: đi theo Phương án B, nhưng có thể chia nhỏ để không mất tốc độ demo.

### Giai đoạn 3: Đồng bộ với AI Agent

1. So sánh slug UI với slug trong cleaned_data.
2. Đảm bảo AI trả lời cùng thông tin với page public.
3. Nếu có trường thông tin mới từ UI như chính sách, bảng giá, tiện ích, mặt bằng, nên đưa vào knowledge/data source.
4. Tránh để AI dùng một bộ data, UI dùng một bộ data khác.

### Giai đoạn 4: Tối ưu deploy

1. Localize ảnh/CSS quan trọng.
2. Loại CSS WordPress không dùng.
3. Kiểm tra Lighthouse/performance sau khi chuyển component.
4. Kiểm tra CSP nếu vẫn dùng HTML raw.

---

## 13. Kết luận cuối

Thay đổi giao diện hiện tại **đạt mục tiêu visual nhanh**, nhưng chưa đạt mục tiêu kiến trúc lâu dài của dự án.

Điểm đáng mừng là build FE vẫn pass và admin/public layout chưa vỡ rõ ràng. Nhưng nếu đi tiếp tới staging/production, cần ưu tiên xử lý các vấn đề:

1. Không để route tĩnh đè route data-driven nếu muốn database là nguồn chuẩn.
2. Không dùng form WordPress raw cho lead.
3. Không để UI hardcode lệch với AI/database.
4. Chuyển dần HTML khổng lồ thành React component có dữ liệu chuẩn.

Nói ngắn gọn: UI mới là một “bản áo đẹp”, nhưng phần xương sống dữ liệu của dự án đang bị đi vòng qua. Bước tiếp theo nên là giữ tinh thần thiết kế mới, nhưng nối nó lại với database/API/AI Agent một cách sạch và có kiểm soát.

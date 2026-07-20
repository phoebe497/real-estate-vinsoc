# Kế hoạch revised: dựng public UI bám sát raw_pages

Ngày tạo: 2026-06-28  
Nguồn chuẩn mới: thư mục `raw_pages` và ảnh local trong `FE/public/media_files`.

---

## 1. Mục tiêu revised

Sau khi có thêm `raw_pages`, mục tiêu không chỉ là dựng giao diện public giống phong cách `vinhomeoceanpark.com.vn`, mà còn phải:

1. Đọc các HTML raw page đã lưu.
2. Lấy lại cấu trúc nội dung chính: title, H1, H2, hero/caption, các section quan trọng.
3. Map ảnh trong raw page sang ảnh local trong `FE/public/media_files`.
4. Mở rộng route public để phủ đủ các page raw đã có.
5. Vẫn giữ nguyên backend, database, AI Agent, dashboard và auth.
6. Không quay lại dùng raw WordPress HTML trực tiếp trong React.

---

## 2. Phạm vi raw_pages đã phát hiện

Tổng số file HTML:

```txt
18
```

Danh sách chính:

```txt
home
chung-cu
masteri-lakeside
masteri-waterfront
the-bayfront
the-beverly
the-london
the-ocean-view
the-palma
the-paris
the-pavilion
the-sapphire
the-senique-1
the-senique-2
the-senique-hanoi
the-zenpark
the-zurich
toa-s2-17-the-s-vista
```

---

## 3. Phương án thực hiện

### 3.1. Không dùng lại raw HTML trực tiếp

Không đưa nguyên HTML WordPress vào `dangerouslySetInnerHTML`.

Lý do:

- Dễ phá dashboard/chat/form.
- Form WordPress không lưu lead vào backend.
- Popup/slider WordPress cần runtime riêng.
- Deploy khó kiểm soát.

Thay vào đó:

- Dùng raw page để lấy cấu trúc/nội dung/ảnh.
- Dựng lại bằng React template.
- Form/chat vẫn dùng logic app.

---

### 3.2. Bổ sung metadata từ raw page vào data config

Mở rộng `PublicPageData`:

```ts
sourcePage?: string;
rawHeadings?: string[];
rawImages?: PublicCard[];
```

Ý nghĩa:

- `sourcePage`: biết page này lấy cấu trúc từ raw file nào.
- `rawHeadings`: hiển thị outline H2/H1 section theo raw page.
- `rawImages`: bổ sung ảnh map từ raw page.

---

### 3.3. Mở rộng route public theo raw_pages

Ngoài 11 page phân khu cũ, bổ sung:

```txt
/phan-khu/the-bayfront
/phan-khu/the-palma
/phan-khu/the-senique-1
/phan-khu/the-senique-2
/phan-khu/toa-s2-17-the-s-vista
```

---

### 3.4. Kiểm soát ảnh local

Toàn bộ ảnh được tham chiếu trong `public-vinhomes.ts` phải tồn tại trong:

```txt
FE/public/media_files
```

Kiểm tra bằng script Node:

```txt
checked 75, missing 0
```

---

## 4. Tiêu chí đánh giá sau thực hiện

1. `npm run build` pass.
2. `docker compose build frontend` pass.
3. Không còn `dangerouslySetInnerHTML`, `wpcf7`, `pum-*`, external `vinhomeoceanpark.com.vn` trong `FE/src`.
4. 18 raw pages được phân tích, ít nhất các route public tương ứng quan trọng được phủ.
5. Các route mới build thành static pages.
6. Ảnh local được copy vào Docker image.
7. BE/DB/AI/dashboard/auth không bị thay đổi.

---

## 5. Rủi ro còn lại

- Một số ảnh hero remote trong raw page không match exact 100% với media_files theo basename; khi không match, dùng ảnh local gần nhất cùng folder/chủ đề để đảm bảo deploy không vỡ ảnh.
- UI vẫn là React recreation, không phải WordPress runtime 1:1 tuyệt đối.
- Nếu mentor yêu cầu pixel-perfect tuyệt đối, cần bước tiếp theo là port CSS/section chi tiết hơn từ từng raw page, nhưng vẫn nên tránh raw form/script.

---

## 6. Kết luận kế hoạch

Kế hoạch revised tập trung vào “bám raw_pages sâu hơn” nhưng vẫn giữ kiến trúc deploy an toàn. Đây là hướng cân bằng giữa yêu cầu visual giống site mẫu và yêu cầu hệ thống AI/dashboard/backend ổn định.

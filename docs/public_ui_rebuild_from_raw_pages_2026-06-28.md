# Báo cáo rebuild giao diện client theo 3 HTML mẫu

Ngày thực hiện: 2026-06-28  
Phạm vi: Frontend public/client  
Không thay đổi: Backend, Database, AI Agent/RAG/LLM, Admin dashboard

## 1. Mục tiêu

Rebuild giao diện public theo 3 file HTML mẫu:

- `raw_pages/home-17e16fc1.html`
- `raw_pages/chung-cu-869871e7.html`
- `raw_pages/the-zenpark-596b6b21.html`

Yêu cầu chính:

- Giao diện giống tinh thần website mẫu Vinhomes Ocean Park.
- Không bê WordPress runtime, plugin, jQuery, tracking script.
- Chỉ dùng ảnh local trong `FE/public/media_files`.
- Giữ nguyên logic API hiện tại cho login/register/contact/chat.
- Không ảnh hưởng admin dashboard.

## 2. Công việc đã thực hiện

### 2.1. Rebuild data public cho 3 trang trọng tâm

File đã chỉnh:

- `FE/src/data/public-vinhomes.ts`

Đã tạo lại dữ liệu sạch cho:

- Trang chủ `/`
- Trang chung cư `/chung-cu`
- Trang The Zenpark `/phan-khu/the-zenpark`

Data mới gồm:

- Hero.
- Hero cards/mở bán.
- Stats.
- Section nội dung theo thứ tự chính của raw HTML.
- Bảng giá tham khảo.
- Cards phân khu/sản phẩm.
- Gallery.
- Amenities.
- Contact image.
- Danh sách ảnh gốc chưa map được chính xác.

### 2.2. Rebuild component public page

File đã chỉnh:

- `FE/src/components/public/static-vinhomes-page.tsx`

Đã chuyển public page thành template React sạch:

- `PublicHero`
- `PublicStats`
- `PriceTable`
- `PublicCardGrid`
- `StaticVinhomesPage`
- `FloatingContactButtons`

Component không dùng script WordPress, không gọi ảnh online, không thay đổi backend/API.

### 2.3. Rebuild các route public chính

File đã chỉnh:

- `FE/src/app/page.tsx`
- `FE/src/app/chung-cu/page.tsx`
- `FE/src/app/phan-khu/the-zenpark/page.tsx`

Kết quả:

- `/` render theo `homePageData`.
- `/chung-cu` render theo `apartmentPageData`.
- `/phan-khu/the-zenpark` render theo `zenparkPageData`.

### 2.4. Giữ ổn định các route phân khu cũ

File đã chỉnh:

- `FE/src/data/public-vinhomes.ts`
- `FE/src/app/phan-khu/page.tsx`

Repo đang có nhiều route tĩnh khác như:

- `/phan-khu/the-zurich`
- `/phan-khu/the-paris`
- `/phan-khu/the-london`
- `/phan-khu/masteri-waterfront`
- `/phan-khu/the-senique-hanoi`
- ...

Nếu xóa data của các route này, build Next.js có thể fail hoặc người dùng gặp trang lỗi. Vì vậy, tôi thêm fallback data tối giản cho các route cũ để:

- Không vỡ build.
- Không làm mất route.
- Không ảnh hưởng deploy.

Lưu ý: 3 trang được rebuild sâu theo raw HTML là `/`, `/chung-cu`, `/phan-khu/the-zenpark`. Các route còn lại hiện là fallback ổn định, có thể làm sâu ở version sau.

### 2.5. Rebuild header/footer public

File đã chỉnh:

- `FE/src/components/header.tsx`
- `FE/src/components/footer.tsx`

Header mới:

- Trang chủ
- Chung cư
- Đăng nhập
- Đăng ký

Khi khách hàng đã đăng nhập, header thay `Đăng nhập/Đăng ký` bằng:

- Tên khách hàng
- Đăng xuất

Admin dashboard không bị bọc header/footer public vì `PublicLayoutWrapper` vẫn loại trừ route `/admin`.

### 2.6. Rebuild CSS public

File đã chỉnh:

- `FE/src/app/public-vinhomes.css`

Đã tạo style public mới theo tinh thần landing page Vinhomes:

- Hero lớn phủ ảnh.
- Màu xanh/gold.
- Stats bar.
- Section split text/image.
- Card grid.
- Bảng giá.
- Contact band.
- Floating contact buttons.
- Auth page style đồng bộ.

CSS public dùng prefix `vh-` để giảm nguy cơ ảnh hưởng dashboard admin.

### 2.7. Đồng bộ giao diện login/register

File đã chỉnh:

- `FE/src/app/dang-nhap/page.tsx`
- `FE/src/app/dang-ky/page.tsx`

Đã giữ nguyên logic:

- Login gọi `POST ${API_URL}/customer/login`
- Register gọi `POST ${API_URL}/customer/register`
- Lưu `CUSTOMER_TOKEN_KEY`
- Gọi `startCustomerSession()`
- Dispatch `auth-change`
- Redirect về `/`

Chỉ thay phần giao diện và sửa text tiếng Việt bị lỗi mã hóa.

### 2.8. Thêm alias route tiếng Anh

File đã thêm:

- `FE/src/app/login/page.tsx`
- `FE/src/app/register/page.tsx`

Mục đích:

- `/login` redirect về `/dang-nhap`
- `/register` redirect về `/dang-ky`

Điều này giúp mentor/user gõ route kiểu tiếng Anh vẫn không bị 404.

### 2.9. Sửa contact form public

File đã chỉnh:

- `FE/src/components/contact-form.tsx`

Đã sửa text tiếng Việt bị lỗi mã hóa, giữ nguyên endpoint:

- `POST ${API_URL}/contact`

Form vẫn lưu lead vào backend/dashboard như trước.

## 3. Mapping ảnh local

Toàn bộ ảnh đang dùng đều nằm trong:

- `FE/public/media_files/project/vinhomes-ocean-park-gia-lam`
- `FE/public/media_files/subzone/...`

Đã kiểm tra 59 reference ảnh trong data public: tất cả file đều tồn tại.

Một số ảnh trong HTML WordPress gốc chưa có file local trùng tuyệt đối, ví dụ:

- `vinhomes-ocean-park-slide-1.jpg`
- `masteri-grand-coast-bg-homepage.jpg`
- `masteri-era-landmark-background-2.jpg`
- `background-blue.jpg`
- `chung-cu-vinhomes-ocean-park-thuc-te.jpg`
- `phan-khu-london-vinhomes-ocean-park-background.jpg`
- `the-paris-background.jpg`
- `the-zenpark-slide.jpg`
- `can-ho-the-zenpark.jpg`

Phương án áp dụng:

- Không gọi ảnh online.
- Không dùng placeholder ngoài dự án.
- Dùng ảnh local tương ứng gần nhất khi có trong `media_files`.
- Ghi chú các ảnh gốc chưa map chính xác trong data/report.

## 4. Kết quả kiểm thử

Đã chạy:

```bash
cd FE
npm run build
```

Kết quả:

- Build Next.js thành công.
- TypeScript pass.
- Static pages generated thành công.
- Các route public/admin vẫn được nhận diện.

Các route build thành công gồm:

- `/`
- `/chung-cu`
- `/dang-nhap`
- `/dang-ky`
- `/login`
- `/register`
- `/phan-khu`
- `/phan-khu/the-zenpark`
- Các route phân khu tĩnh cũ
- `/admin`
- `/admin/login`
- `/admin/leads`
- `/admin/users`
- `/admin/conversations`
- `/admin/fallback-rules`

## 5. Cách test local

### 5.1. Build frontend

```bash
cd FE
npm run build
```

Kỳ vọng:

- Không lỗi TypeScript.
- Không lỗi pre-render route.

### 5.2. Chạy app bằng Docker

Từ root project:

```bash
docker compose up -d --build
```

Sau đó mở:

- `http://127.0.0.1:3000/`
- `http://127.0.0.1:3000/chung-cu`
- `http://127.0.0.1:3000/phan-khu/the-zenpark`
- `http://127.0.0.1:3000/dang-nhap`
- `http://127.0.0.1:3000/dang-ky`
- `http://127.0.0.1:3000/admin`

### 5.3. Test public UI

Kiểm tra:

- Header chỉ có các mục public chính.
- Ảnh hiển thị, không 404.
- Không có lỗi console liên quan ảnh online.
- Trang responsive ở desktop/mobile.
- Floating contact buttons hoạt động.

### 5.4. Test contact form

Trên `/`, `/chung-cu` hoặc `/phan-khu/the-zenpark`:

1. Nhập số điện thoại.
2. Bấm `Nhận tư vấn`.
3. Kiểm tra dashboard admin/leads có lead mới.

### 5.5. Test login/register

Kiểm tra:

- `/dang-nhap`
- `/dang-ky`
- `/login`
- `/register`

Kỳ vọng:

- `/login` redirect về `/dang-nhap`.
- `/register` redirect về `/dang-ky`.
- Login/register vẫn gọi API cũ.
- Sau login, header hiển thị tên khách hàng và nút đăng xuất.

### 5.6. Test admin dashboard

Mở:

- `/admin`
- `/admin/login`
- `/admin/leads`
- `/admin/users`

Kỳ vọng:

- Admin không bị header/footer public bọc vào.
- Dashboard không bị đổi logic.

## 6. Ghi chú kỹ thuật

Khi kiểm tra git bằng sandbox có thể gặp:

```text
fatal: detected dubious ownership in repository
```

Đây là do sandbox chạy bằng user khác với owner repository trên Windows, không phải lỗi code. Nếu cần dùng git trong terminal thật của bạn, bạn có thể chạy bằng user Windows hiện tại hoặc cấu hình safe directory theo hướng dẫn của Git.

## 7. Đề xuất version tiếp theo

Sau version này, nên làm tiếp theo thứ tự:

1. So sánh trực quan 3 trang mới với raw HTML/screenshot mentor yêu cầu.
2. Làm sâu thêm các route phân khu còn lại nếu mentor muốn nhiều hơn 3 trang.
3. Kiểm tra lại mobile UI bằng browser thực tế.
4. Deploy staging, kiểm tra ảnh static trong container.
5. Test lại chat AI và dashboard sau deploy để xác nhận public UI không ảnh hưởng hệ thống nghiệp vụ.


# Kế hoạch nối domain staging tới VPS

Ngày lập kế hoạch: 2026-06-28  
Trạng thái: Chờ duyệt trước khi thực hiện  
Domain gốc: `quangtm.site`  
Subdomain staging dự kiến: `stagging.c2-app-005.quangtm.site`

## 1. Mục tiêu

Thiết lập domain online đàng hoàng cho môi trường staging để có thể nộp/demo mentor:

```text
https://stagging.c2-app-005.quangtm.site
```

Ứng dụng sau khi hoàn tất cần đạt:

- Người dùng truy cập bằng domain, không dùng IP VPS trực tiếp.
- Frontend chạy qua domain HTTPS.
- Backend API đi qua cùng domain.
- Chat AI đi qua cùng domain.
- Không còn frontend gọi `localhost:8000` khi deploy online.
- Database không expose ra internet.
- Kiến trúc vẫn đúng với thiết kế DevOps trước đó: Cloudflare/DNS → VPS → reverse proxy → Docker services.

## 2. Kiến trúc đề xuất

```text
User/Mentor
  ↓
https://stagging.c2-app-005.quangtm.site
  ↓
DNS / Cloudflare
  ↓
VPS public IP
  ↓
Reverse proxy trên VPS
  ├── /          → frontend container:3000
  ├── /api/v1    → backend container:8000
  ├── /agent     → backend container:8000
  ├── /docs      → backend container:8000, nếu cần
  └── /health    → backend container:8000, nếu cần
```

Database chỉ nằm trong Docker network nội bộ:

```text
database container:5432
```

Không public PostgreSQL ra ngoài.

## 3. Xác nhận tên domain

Với domain gốc:

```text
quangtm.site
```

Nếu tên cần nộp là:

```text
stagging.c2-app-005
```

Thì full domain sẽ là:

```text
stagging.c2-app-005.quangtm.site
```

Tên này hợp lệ về mặt DNS.

Lưu ý:

- Từ đúng tiếng Anh là `staging`.
- Nhưng nếu yêu cầu nộp là `stagging`, ta sẽ dùng đúng `stagging`.

## 4. Các thay đổi dự kiến sau khi được duyệt

### 4.1. DNS

Tạo DNS record:

```text
Type: A
Name: stagging.c2-app-005
Value: <VPS_PUBLIC_IP>
TTL: Auto
Proxy: tùy chiến lược Cloudflare
```

Nếu dùng Cloudflare:

- Giai đoạn đầu nên để `DNS only` để debug dễ.
- Sau khi HTTPS/reverse proxy ổn, có thể bật proxy màu cam.

### 4.2. Reverse proxy

Cần chọn một trong hai phương án:

#### Phương án A: Nginx + Certbot

Ưu điểm:

- Phổ biến.
- Dễ kiểm soát config.
- Phù hợp production thật.

Nhược điểm:

- Cần tự chạy Certbot để cấp/chạy lại SSL.

#### Phương án B: Caddy

Ưu điểm:

- HTTPS tự động.
- Config ngắn.
- Rất tiện cho staging/demo.

Nhược điểm:

- Nếu team/mentor quen Nginx hơn thì cần giải thích thêm.

Đề xuất của tôi:

- Nếu mục tiêu là học quy trình production-like: dùng Nginx + Certbot.
- Nếu mục tiêu là nhanh có HTTPS ổn định để demo: dùng Caddy.

Vì dự án đang học CI/CD + Docker + VPS + Cloudflare, tôi đề xuất dùng **Nginx + Certbot** để sát quy trình triển khai thực tế hơn.

### 4.3. Docker/Compose

Hiện tại app đã chạy bằng Docker Compose. Sau khi có reverse proxy, nên điều chỉnh hướng vận hành:

- Frontend container vẫn chạy port `3000`.
- Backend container vẫn chạy port `8000`.
- Reverse proxy đứng trước.
- Có thể giữ port mapping trong giai đoạn debug.
- Khi ổn định hơn, chỉ expose `80/443` ra ngoài.

Mục tiêu cuối:

```text
Internet chỉ vào 80/443
Frontend/backend/database chỉ dùng nội bộ VPS/Docker network
```

### 4.4. Environment staging

Frontend staging cần dùng domain thật:

```env
NEXT_PUBLIC_API_URL=https://stagging.c2-app-005.quangtm.site/api/v1
```

Backend cần cho phép origin staging:

```env
BACKEND_CORS_ORIGINS=https://stagging.c2-app-005.quangtm.site
```

Tên biến thực tế sẽ cần rà lại trong source/config hiện tại trước khi sửa.

Mục tiêu:

- Frontend không gọi `http://localhost:8000`.
- Không gặp CORS khi login/chat/contact.
- Chat AI gọi đúng:

```text
https://stagging.c2-app-005.quangtm.site/agent/chat
```

### 4.5. Firewall VPS

Cần mở:

```text
80/tcp
443/tcp
```

Nên hạn chế public:

```text
3000/tcp
8000/tcp
5432/tcp
```

Trong giai đoạn debug có thể tạm mở `3000/8000`, nhưng sau khi proxy ổn thì nên đóng.

## 5. Các bước thực hiện dự kiến

### Bước 1: Xác nhận thông tin

Cần xác nhận:

1. VPS public IP.
2. Domain `quangtm.site` đang quản lý ở đâu: Cloudflare hay nhà cung cấp khác.
3. Dùng chính xác `stagging` hay đổi thành `staging`.
4. VPS hiện đã cài Nginx chưa.
5. App staging hiện chạy bằng compose file nào.

### Bước 2: Tạo DNS record

Tạo:

```text
stagging.c2-app-005.quangtm.site → <VPS_PUBLIC_IP>
```

Kiểm tra:

```bash
nslookup stagging.c2-app-005.quangtm.site
```

Hoặc:

```bash
dig stagging.c2-app-005.quangtm.site
```

### Bước 3: Cấu hình reverse proxy

Tạo config proxy cho domain:

```text
/       → frontend:3000
/api/v1 → backend:8000
/agent  → backend:8000
```

Nếu dùng Nginx, file dự kiến:

```text
/etc/nginx/sites-available/stagging.c2-app-005.quangtm.site
```

Enable sang:

```text
/etc/nginx/sites-enabled/
```

### Bước 4: Cấp HTTPS

Nếu dùng Nginx + Certbot:

```bash
sudo certbot --nginx -d stagging.c2-app-005.quangtm.site
```

Nếu dùng Cloudflare proxy:

- SSL/TLS mode nên là `Full` hoặc `Full strict`.
- Không dùng `Flexible` vì dễ gây redirect loop hoặc sai scheme.

### Bước 5: Cập nhật env staging

Cập nhật:

```env
NEXT_PUBLIC_API_URL=https://stagging.c2-app-005.quangtm.site/api/v1
```

Cập nhật CORS backend cho domain mới.

Sau đó redeploy:

```bash
bash scripts/deploy/staging_deploy.sh
```

Tên script có thể thay đổi tùy version hiện tại trên VPS.

### Bước 6: Kiểm thử

Kiểm tra frontend:

```bash
curl -I https://stagging.c2-app-005.quangtm.site
```

Kiểm tra API:

```bash
curl https://stagging.c2-app-005.quangtm.site/api/v1/health
```

Hoặc endpoint readiness thực tế của backend.

Kiểm tra browser:

- Mở homepage.
- Mở `/chung-cu`.
- Mở `/phan-khu/the-zenpark`.
- Test login/register.
- Test contact form.
- Test chat AI.
- Mở admin dashboard.

### Bước 7: Đóng port public không cần thiết

Sau khi domain/proxy ổn:

- Không dùng `http://IP:3000` nữa.
- Không dùng `http://IP:8000` nữa.
- Chỉ public `80/443`.

## 6. Rủi ro và cách xử lý

### Rủi ro 1: DNS chưa propagate

Dấu hiệu:

- `nslookup` chưa ra IP VPS.
- Browser báo không tìm thấy domain.

Xử lý:

- Chờ DNS cập nhật.
- Kiểm tra record đúng chưa.
- Nếu dùng Cloudflare, kiểm tra nameserver domain đã trỏ về Cloudflare chưa.

### Rủi ro 2: HTTPS lỗi

Dấu hiệu:

- Certbot fail.
- Browser báo certificate invalid.

Xử lý:

- Đảm bảo DNS đã trỏ đúng VPS.
- Port 80/443 mở.
- Nginx config không lỗi.

### Rủi ro 3: Frontend vẫn gọi localhost

Dấu hiệu:

- Console báo gọi `http://localhost:8000`.
- Login/chat/contact lỗi CORS.

Xử lý:

- Kiểm tra `NEXT_PUBLIC_API_URL` khi build frontend.
- Redeploy frontend image/container sau khi đổi env.

### Rủi ro 4: CORS

Dấu hiệu:

- API trả được bằng curl nhưng browser bị CORS.

Xử lý:

- Thêm `https://stagging.c2-app-005.quangtm.site` vào CORS backend.
- Kiểm tra preflight OPTIONS.

### Rủi ro 5: Cloudflare SSL mode sai

Dấu hiệu:

- Redirect loop.
- Lỗi mixed content.

Xử lý:

- Không dùng `Flexible`.
- Dùng `Full` hoặc `Full strict`.

## 7. Tiêu chí hoàn thành

Hoàn thành khi:

- `https://stagging.c2-app-005.quangtm.site` mở được trên browser.
- Homepage hiển thị đúng.
- API không còn gọi localhost.
- Login/register hoạt động.
- Contact form lưu lead.
- Chat AI gọi được backend.
- Admin dashboard vẫn vào được.
- HTTPS hợp lệ.
- Không cần truy cập bằng `IP:3000`.

## 8. Việc user cần tự làm trên nền tảng ngoài

Những việc tôi không thể tự làm nếu không có quyền tài khoản/domain:

1. Đăng nhập nơi quản lý domain `quangtm.site`.
2. Tạo DNS record cho `stagging.c2-app-005`.
3. Nếu dùng Cloudflare, kiểm tra nameserver và SSL/TLS mode.
4. Cung cấp VPS public IP.
5. SSH vào VPS hoặc cho biết trạng thái hiện tại của VPS.

## 9. Quyết định cần duyệt

Trước khi thực hiện, cần bạn xác nhận:

1. Dùng domain chính xác là:

```text
stagging.c2-app-005.quangtm.site
```

2. Chọn reverse proxy:

```text
Nginx + Certbot
```

hay:

```text
Caddy
```

3. Có cho phép cập nhật env staging để frontend/backend dùng domain mới không.

Sau khi bạn duyệt, tôi sẽ bắt đầu tạo/sửa các file cấu hình cần thiết trong project và viết hướng dẫn thao tác VPS cụ thể.


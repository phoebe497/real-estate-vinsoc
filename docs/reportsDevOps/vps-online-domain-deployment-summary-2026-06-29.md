# Tổng hợp triển khai VPS online với domain staging

Ngày tổng hợp: 2026-06-29  
Domain staging: `https://staging.c2-app-005.quangtm.site`  
VPS IP: `103.149.87.83`  
Môi trường: Staging  
Stack: Docker Compose + Nginx + Certbot + GitHub Container Registry

## 1. Mục tiêu

Mục tiêu của phần này là đưa dự án từ trạng thái chạy bằng IP/port trực tiếp:

```text
http://103.149.87.83:3000
```

sang domain online có HTTPS:

```text
https://staging.c2-app-005.quangtm.site
```

Yêu cầu sau triển khai:

- Người dùng/mentor truy cập bằng domain thật.
- HTTPS hoạt động.
- Frontend không gọi `localhost` hoặc `IP:8000`.
- API đi qua cùng domain:

```text
https://staging.c2-app-005.quangtm.site/api/v1
```

- Chat AI đi qua:

```text
https://staging.c2-app-005.quangtm.site/agent/chat
```

- Database không expose ra internet.
- Laptop cá nhân tắt thì website vẫn chạy vì app chạy trên VPS.

## 2. Kiến trúc hiện tại

```text
User / Mentor
  ↓
https://staging.c2-app-005.quangtm.site
  ↓
DNS A Record
  ↓
VPS 103.149.87.83
  ↓
Nginx reverse proxy
  ├── /        → frontend container:3000
  ├── /api/v1  → backend container:8000/api/v1
  ├── /agent   → backend container:8000/agent
  ├── /docs    → backend container:8000/docs
  └── /openapi.json → backend container:8000/openapi.json
```

Docker services:

```text
ocean-park-staging-frontend-1  → Next.js frontend
ocean-park-staging-backend-1   → FastAPI backend
ocean-park-staging-database-1  → PostgreSQL
```

## 3. DNS đã cấu hình

Record đã tạo:

```text
Type: A
Name: staging.c2-app-005
Value: 103.149.87.83
```

Full domain:

```text
staging.c2-app-005.quangtm.site
```

Đã kiểm tra:

```bash
nslookup staging.c2-app-005.quangtm.site
```

Kết quả:

```text
Name: staging.c2-app-005.quangtm.site
Address: 103.149.87.83
```

Kết luận:

```text
DNS OK
```

## 4. Nginx reverse proxy

VPS đã có Nginx:

```bash
nginx -v
```

Kết quả:

```text
nginx/1.18.0 (Ubuntu)
```

Nginx được dùng để nhận request HTTP/HTTPS từ domain và proxy vào container nội bộ.

Mapping cần có:

```nginx
location /api/v1/ {
    proxy_pass http://127.0.0.1:8000/api/v1/;
}

location /agent/ {
    proxy_pass http://127.0.0.1:8000/agent/;
}

location /docs {
    proxy_pass http://127.0.0.1:8000/docs;
}

location /openapi.json {
    proxy_pass http://127.0.0.1:8000/openapi.json;
}

location / {
    proxy_pass http://127.0.0.1:3000;
}
```

Sau khi cấu hình, đã test:

```bash
curl -I http://staging.c2-app-005.quangtm.site
```

Kết quả:

```text
HTTP/1.1 200 OK
X-Powered-By: Next.js
```

Backend docs cũng hoạt động:

```bash
curl http://staging.c2-app-005.quangtm.site/docs
```

Kết luận:

```text
Nginx HTTP reverse proxy OK
```

## 5. HTTPS bằng Certbot

Ban đầu VPS chưa có Certbot:

```text
sudo: certbot: command not found
```

Cài Certbot:

```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
```

Cấp SSL:

```bash
sudo certbot --nginx -d staging.c2-app-005.quangtm.site
```

Khi Certbot hỏi email:

```text
quangminhgdev204@gmail.com
```

Khi hỏi điều khoản:

```text
Y
```

Khi hỏi chia sẻ email:

```text
N
```

Nếu hỏi redirect HTTP sang HTTPS:

```text
Chọn redirect
```

Sau khi cấp SSL, test:

```bash
curl -I https://staging.c2-app-005.quangtm.site
```

Kết quả:

```text
HTTP/1.1 200 OK
Server: nginx/1.18.0 (Ubuntu)
X-Powered-By: Next.js
```

Kết luận:

```text
HTTPS OK
```

## 6. File `.env` staging cần đúng như thế nào

Script deploy staging đang dùng:

```bash
ENV_FILE="${ENV_FILE:-.env}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.registry.yml}"
PROJECT_NAME="${PROJECT_NAME:-ocean-park-staging}"
```

Vì vậy file quan trọng trên VPS là:

```text
/opt/ocean-park-advisor/.env
```

Các biến domain/API nên là:

```env
CORS_ORIGINS=https://staging.c2-app-005.quangtm.site
NEXT_PUBLIC_API_URL=https://staging.c2-app-005.quangtm.site/api/v1
FRONTEND_PORT=3000
BACKEND_PORT=8000
PROJECT_NAME=ocean-park-staging
BACKEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-backend:dev
FRONTEND_IMAGE=ghcr.io/ai20k-build-cohort-2/c2-app-005-frontend:dev
FRONTEND_DOMAIN=staging.c2-app-005.quangtm.site
API_DOMAIN=staging.c2-app-005.quangtm.site
OPENROUTER_SITE_URL=https://staging.c2-app-005.quangtm.site
```

Không nên để:

```env
NEXT_PUBLIC_API_URL=https://staging.c2-app-005.quangtm.site:8000/api/v1
```

Không nên để:

```env
API_DOMAIN=api-staging.c2-app-005.quangtm.site
```

vì hiện tại chưa cấu hình DNS/Nginx cho API subdomain riêng. Backend đang đi chung domain theo path `/api/v1`.

## 7. Lỗi `ERR_SSL_PROTOCOL_ERROR` sau khi lên HTTPS

Lỗi đã gặp:

```text
POST https://staging.c2-app-005.quangtm.site:8000/api/v1/customer/login
net::ERR_SSL_PROTOCOL_ERROR
```

Nguyên nhân:

- HTTPS chỉ chạy ở Nginx port `443`.
- Backend port `8000` chỉ chạy HTTP nội bộ, không có SSL.
- Frontend image cũ tự ghép API thành `https://domain:8000/api/v1`.

HTTP trước đó vẫn chạy vì:

```text
http://domain:8000 → backend HTTP → OK
```

Nhưng HTTPS bị lỗi vì:

```text
https://domain:8000 → backend không hiểu SSL → ERR_SSL_PROTOCOL_ERROR
```

Đường đúng phải là:

```text
https://staging.c2-app-005.quangtm.site/api/v1/customer/login
```

Không có `:8000`.

## 8. Fix frontend API resolver

File đã sửa:

```text
FE/src/lib/api.ts
```

Logic cần đúng:

```ts
return `${window.location.origin}/api/v1`;
```

Mục đích:

- Nếu Docker image lỡ build với `localhost`, khi chạy trên domain thật frontend vẫn gọi same-origin.
- Không gọi `:8000` từ browser.
- Phù hợp kiến trúc reverse proxy.

Sau khi sửa source cần:

```bash
git add FE/src/lib/api.ts
git commit -m "fix: use same-origin API behind reverse proxy"
git push
```

Sau đó chờ GitHub Actions build/publish frontend image mới.

Trên VPS redeploy:

```bash
bash scripts/deploy/staging_deploy.sh
```

## 9. Admin login và lỗi đổi mật khẩu admin

Tài khoản admin mong muốn:

```text
ADMIN_EMAIL=admin@gmail.com
```

Lưu ý quan trọng:

`.env` chỉ seed admin lần đầu nếu email chưa tồn tại trong DB.

Code seed admin hiện tại:

```py
if session.scalar(select(User.id).where(User.email == email)):
    return False
```

Nghĩa là:

- Nếu user chưa tồn tại → tạo admin theo `.env`.
- Nếu user đã tồn tại → không tự cập nhật mật khẩu.

Đã kiểm tra DB có user:

```text
[(1, 'admin@gmail.com', 'admin', True)]
```

Nếu đăng nhập không được, reset password trực tiếp:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml exec backend python -c "from src.db.session import get_session_factory; from src.models.entities import User; from src.services.security import hash_password; s=get_session_factory()(); u=s.query(User).filter(User.email=='admin@gmail.com').first(); u.password_hash=hash_password('admin123456789Aa@'); u.role='admin'; u.is_active=True; s.commit(); print('updated', u.email, u.role, u.is_active); s.close()"
```

Sau đó đăng nhập:

```text
Email: admin@gmail.com
Password: admin123456789Aa@
```

## 10. Lỗi backend unhealthy khi đổi admin password

Lỗi đã gặp:

```text
Unsafe deployment configuration:
ADMIN_PASSWORD must contain at least 12 characters
```

Nguyên nhân:

- Backend có validation cho staging/production.
- `ADMIN_PASSWORD` phải dài ít nhất 12 ký tự.

Sửa:

```env
ADMIN_PASSWORD=<mật khẩu ít nhất 12 ký tự>
```

Ngoài ra cần kiểm tra dòng JWT không bị dính:

Sai:

```env
AUTO_SEED_CATALOG=true JWT_SECRET_KEY=...
```

Đúng:

```env
AUTO_SEED_CATALOG=true
JWT_SECRET_KEY=...
```

## 11. Kiểm tra container trên VPS

Kiểm tra trạng thái:

```bash
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml ps
```

Kỳ vọng:

```text
database  healthy
backend   healthy
frontend  up
```

Kiểm tra backend local:

```bash
curl http://localhost:8000/ready
```

Kiểm tra frontend domain:

```bash
curl -I https://staging.c2-app-005.quangtm.site
```

Kiểm tra backend qua domain:

```bash
curl https://staging.c2-app-005.quangtm.site/docs
curl https://staging.c2-app-005.quangtm.site/openapi.json | head
```

## 12. Checklist test trên browser

Mở:

```text
https://staging.c2-app-005.quangtm.site
```

Test:

1. Homepage hiển thị.
2. `/chung-cu` hiển thị.
3. `/phan-khu/the-zenpark` hiển thị.
4. Login user.
5. Register user.
6. Contact form lưu lead.
7. Chat AI gọi được backend.
8. Admin login:

```text
https://staging.c2-app-005.quangtm.site/admin/login
```

Trong DevTools → Network, request đúng phải là:

```text
https://staging.c2-app-005.quangtm.site/api/v1/...
https://staging.c2-app-005.quangtm.site/agent/chat
```

Không được còn:

```text
localhost:8000
103.149.87.83:8000
staging.c2-app-005.quangtm.site:8000
```

## 13. Website có chạy khi tắt laptop không?

Có.

Lý do:

```text
Laptop cá nhân
  - dùng để code/dev/push/SSH
  - Docker Desktop local tắt cũng không ảnh hưởng staging

VPS
  - chạy Docker Engine thật
  - chạy frontend/backend/database containers
  - chạy Nginx + HTTPS
  - domain trỏ về VPS
```

Website vẫn chạy nếu:

- VPS còn bật.
- Docker containers trên VPS còn chạy.
- Nginx còn chạy.
- DNS còn trỏ đúng VPS.
- SSL certificate còn hạn.

Test độc lập:

1. Tắt Docker Desktop trên laptop.
2. Dùng điện thoại 4G mở:

```text
https://staging.c2-app-005.quangtm.site
```

Nếu mở được, website đang chạy độc lập trên VPS.

## 14. Bảo mật cần làm sau khi ổn định

Trong quá trình debug, một số secret đã từng được paste ra ngoài. Sau khi staging ổn, nên rotate:

- `OPENROUTER_API_KEY`
- `JWT_SECRET_KEY`
- `ADMIN_PASSWORD`
- `POSTGRES_PASSWORD`, nếu cần

Sau khi rotate:

```bash
bash scripts/deploy/staging_deploy.sh
```

Và reset lại admin password trong DB nếu cần.

## 15. Trạng thái hoàn thành mong muốn

Hoàn thành khi:

- `https://staging.c2-app-005.quangtm.site` mở được.
- HTTPS hợp lệ.
- Login/register không gọi `:8000`.
- Admin login được.
- Contact form lưu lead.
- Chat AI hoạt động.
- Docker services healthy.
- Website vẫn chạy khi tắt laptop.


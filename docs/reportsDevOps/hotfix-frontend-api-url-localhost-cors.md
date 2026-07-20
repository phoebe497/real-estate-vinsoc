# Hotfix: frontend calls localhost API on VPS staging

## Bối cảnh

Khi mở staging bằng IP VPS:

```text
http://103.149.87.83:3000
```

và đăng nhập admin, browser báo:

```text
Access to fetch at 'http://localhost:8000/api/v1/auth/login'
from origin 'http://103.149.87.83:3000' has been blocked by CORS policy
```

Request thực tế:

```text
POST http://localhost:8000/api/v1/auth/login
```

## Nguyên nhân

Frontend image được build với:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Trong Next.js, biến `NEXT_PUBLIC_*` được bake vào client bundle ở thời điểm build image.

Khi user mở web từ máy cá nhân:

```text
http://103.149.87.83:3000
```

thì `localhost` trong browser là máy cá nhân của user, không phải VPS. Vì vậy browser cố gọi:

```text
http://localhost:8000
```

thay vì:

```text
http://103.149.87.83:8000
```

Chrome cũng chặn kiểu request này vì trang public IP đang gọi vào địa chỉ private/loopback.

## Phương án đã áp dụng

Cập nhật helper frontend:

```text
FE/src/lib/api.ts
```

Logic mới:

- Nếu `NEXT_PUBLIC_API_URL` là localhost/127.0.0.1 và browser đang chạy trên host thật.
- Frontend sẽ tự đổi API URL sang cùng hostname hiện tại, port `8000`.

Ví dụ:

```text
http://103.149.87.83:3000
```

sẽ gọi API:

```text
http://103.149.87.83:8000/api/v1
```

Chat widget cũng được chuyển sang dùng chung `API_URL` từ:

```text
FE/src/lib/api.ts
```

để tránh lệch cấu hình.

## Điều kiện backend

Trong `.env` trên VPS, cần có:

```env
CORS_ORIGINS=http://103.149.87.83:3000
NEXT_PUBLIC_API_URL=http://103.149.87.83:8000/api/v1
```

Nếu sau này dùng domain/HTTPS:

```env
CORS_ORIGINS=https://staging.your-domain.com
NEXT_PUBLIC_API_URL=https://api-staging.your-domain.com/api/v1
```

## Cách test local

```bash
cd FE
npm run build
```

## Cách deploy lại staging

Commit/push vào branch `dev`, chờ GitHub Actions publish frontend image mới, sau đó trên VPS:

```bash
cd /opt/ocean-park-advisor
git pull origin dev
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml pull frontend
docker compose --env-file .env -p ocean-park-staging -f docker-compose.registry.yml up -d --force-recreate frontend
```

Hard refresh browser:

```text
Ctrl + F5
```

Test login admin lại tại:

```text
http://103.149.87.83:3000/admin/login
```


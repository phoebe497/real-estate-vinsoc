# DevOps v0.5.0 - CI and container registry

## Mục tiêu

Thiết lập nền CI/CD để dự án có thể:

- Tự kiểm tra backend bằng Ruff và Pytest.
- Tự build frontend bằng `npm ci` và `npm run build`.
- Build Docker image cho backend/frontend.
- Push image lên GitHub Container Registry, viết tắt là GHCR.
- Chuẩn bị flow VPS pull image thay vì build trực tiếp từ source.

## Công việc đã làm

### 1. Cập nhật GitHub Actions workflow

File chính:

```text
.github/workflows/ci.yml
```

Workflow hiện có 3 job:

1. `backend-checks`
   - Cài Python 3.11.
   - Cài dependencies bằng:

   ```bash
   python -m pip install -e ".[dev]"
   ```

   - Chạy:

   ```bash
   ruff check src tests
   pytest tests -v --tb=short
   ```

2. `frontend-build`
   - Cài Node.js 22.
   - Cài dependencies bằng:

   ```bash
   npm ci
   ```

   - Build frontend:

   ```bash
   npm run build
   ```

3. `docker-images`
   - Chỉ chạy khi push branch/tag, không chạy trên pull request.
   - Login GHCR bằng `GITHUB_TOKEN`.
   - Build và push:
     - backend image
     - frontend image

Image tags được tạo theo:

- branch, ví dụ `dev`, `main`
- git tag, ví dụ `v0.5.0`
- commit SHA, ví dụ `sha-xxxxxxx`

### 2. Thêm compose runtime dùng image registry

File mới:

```text
docker-compose.registry.yml
```

File này khác với `docker-compose.deploy.yml`:

- `docker-compose.deploy.yml`: build trực tiếp trên VPS từ source code.
- `docker-compose.registry.yml`: không build trên VPS, chỉ pull image đã được CI build.

Đây là hướng tốt hơn cho staging/production lâu dài.

### 3. Cập nhật environment templates

Cập nhật:

```text
.env.staging.example
.env.production.example
```

Thêm biến:

```env
BACKEND_IMAGE=ghcr.io/your-github-user-or-org/your-repo-backend:dev
FRONTEND_IMAGE=ghcr.io/your-github-user-or-org/your-repo-frontend:dev
```

Khi deploy thật, thay `your-github-user-or-org/your-repo` bằng repo thật.

Ví dụ nếu repo là:

```text
github.com/minhquang/ocean-park-advisor
```

thì staging có thể dùng:

```env
BACKEND_IMAGE=ghcr.io/minhquang/ocean-park-advisor-backend:dev
FRONTEND_IMAGE=ghcr.io/minhquang/ocean-park-advisor-frontend:dev
```

Production nên dùng tag version:

```env
BACKEND_IMAGE=ghcr.io/minhquang/ocean-park-advisor-backend:v0.5.0
FRONTEND_IMAGE=ghcr.io/minhquang/ocean-park-advisor-frontend:v0.5.0
```

### 4. Siết Docker build context

Cập nhật:

```text
.dockerignore
FE/.dockerignore
```

Để tránh copy các file không cần thiết hoặc nhạy cảm vào image:

- `.env`
- `.env.*`
- `.ai-log`
- `.github`
- thư mục cấu hình local của agent/editor
- cache/test/build artifacts

## Phương án áp dụng

Giai đoạn này dùng 2 flow song song:

### Flow học/demo ban đầu

VPS build trực tiếp từ source:

```bash
docker compose -f docker-compose.deploy.yml up -d --build
```

Ưu điểm: dễ hiểu, dễ debug.

### Flow staging/production chuẩn hơn

CI build image, VPS chỉ pull image:

```bash
docker compose -f docker-compose.registry.yml pull
docker compose -f docker-compose.registry.yml up -d
```

Ưu điểm:

- deploy nhanh hơn
- rollback dễ hơn
- VPS không cần build source
- image đã đi qua test/build ở CI

## Cách dùng GitHub Actions

### 1. Push lên `dev`

```bash
git push origin dev
```

Kết quả mong đợi:

- backend checks pass
- frontend build pass
- GHCR có image tag `dev` và `sha-...`

### 2. Tạo release tag production

```bash
git tag v0.5.0
git push origin v0.5.0
```

Kết quả mong đợi:

- GHCR có image tag `v0.5.0`

### 3. Dùng image trên VPS

Trên VPS:

```bash
cp .env.staging.example .env
nano .env
docker compose -f docker-compose.registry.yml pull
docker compose -f docker-compose.registry.yml up -d
```

Kiểm tra:

```bash
docker compose -f docker-compose.registry.yml ps
curl http://localhost:8000/ready
curl -I http://localhost:3000
```

## Cách test đã thực hiện local

Backend tests:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Kết quả:

```text
23 passed
```

Ruff:

```powershell
.\.venv\Scripts\python.exe -m ruff check src tests
```

Kết quả:

```text
All checks passed!
```

Frontend build:

```powershell
cd FE
npm run build
```

Kết quả:

```text
Compiled successfully
```

Compose registry staging:

```powershell
docker compose --env-file .env.staging.example -f docker-compose.registry.yml config --quiet
```

Kết quả: hợp lệ.

Compose registry production:

```powershell
docker compose --env-file .env.production.example -f docker-compose.registry.yml config --quiet
```

Kết quả: hợp lệ.

## Lưu ý khi dùng GHCR

- Repo cần bật GitHub Actions.
- Package GHCR có thể cần được đặt visibility phù hợp.
- Nếu image private, VPS cần login GHCR:

```bash
echo "<github-token>" | docker login ghcr.io -u <github-username> --password-stdin
```

Token nên có quyền đọc package. Không ghi token vào repo.

## Bước tiếp theo

DevOps v0.6.0 sẽ tập trung vào VPS staging deployment:

- chuẩn bị user/folder trên VPS
- cài Docker/Compose
- copy `.env`
- chạy `docker-compose.registry.yml`
- kiểm tra health
- chuẩn bị script deploy staging

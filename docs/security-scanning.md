# Hướng dẫn SAST và DAST

Repository dùng các image được pin phiên bản từ Docker Hub:

- `semgrep/semgrep:1.169.0` cho SAST;
- `zaproxy/zap-stable:2.17.0` cho DAST.

Việc pin phiên bản giúp scan có thể tái lập. Chỉ nâng phiên bản sau khi đã đọc
release notes và chạy lại baseline.

## Chạy local

Yêu cầu Docker Engine, Docker Compose v2 và file `.env` hợp lệ khi chạy DAST:

```powershell
Copy-Item .env.example .env
.\scripts\security\scan.ps1 all
```

Linux/macOS:

```bash
cp .env.example .env
bash scripts/security/scan.sh all
```

Có thể thay `all` bằng `sast` hoặc `dast`. Nếu Docker Desktop chưa chạy hoặc
đang ở Windows containers, script dừng sớm với thông báo rõ ràng. ZAP dùng
Compose project và database volume riêng, vô hiệu khóa của LLM provider, rồi
xóa stack sau scan để không ảnh hưởng dữ liệu phát triển.

Raw output nằm trong `security-reports/`:

- `semgrep.json`: Semgrep OWASP Top 10 cho `src/` và `FE/src/`;
- `zap-frontend.json`: ZAP baseline/passive scan frontend;
- `zap-backend.json`: ZAP baseline/passive scan Swagger UI.

Normalized output nằm trong `security-data-lake/`:

- `findings.jsonl`: mỗi dòng là một finding instance với schema chung;
- `summary.json`: manifest nguồn và tổng hợp theo scanner/severity.

Có thể aggregate độc lập:

```powershell
python scripts/security/aggregate_security_reports.py security-reports `
  --output-dir security-data-lake
```

## CI/CD

Workflow `.github/workflows/security.yml` chạy khi push/PR vào `main` hoặc
`dev`, theo lịch hằng tuần và qua `workflow_dispatch`.

1. Job `sast` xuất SARIF từ Semgrep, upload GitHub Code Scanning và artifact.
2. Job `dast` dựng stack cô lập, scan frontend/backend, lưu JSON, chuyển sang
   SARIF rồi upload Code Scanning và artifact.
3. Job `aggregate` tải artifact của hai job, chuẩn hóa vào
   `unified-security-data-lake` và giữ 30 ngày.

GitHub Code Scanning trên private repository cần GitHub Code Security. Nếu gói
GitHub hiện tại không hỗ trợ upload SARIF, JSON/SARIF và data-lake artifact vẫn
là đầu ra có thể tải về, nhưng bước upload Code Scanning có thể thất bại.

## Phạm vi và giới hạn an toàn

ZAP hiện là baseline/passive scan. Backend target là Swagger UI, không phải
active OpenAPI scan và chưa đăng nhập bằng từng role. Cấu hình này tránh tạo
dữ liệu CRM/chat ngoài ý muốn trong CI nhưng chưa kiểm tra đầy đủ authorization,
IDOR và business logic.

Chỉ scan hệ thống thuộc quyền sở hữu hoặc đã được cấp phép. Active scan phải
chạy trên staging cô lập, có snapshot/cleanup và cửa sổ kiểm thử được phê duyệt.


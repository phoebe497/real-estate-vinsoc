# Báo cáo Week 1 — SAST/DAST CI/CD Integration & Baseline Analysis

Ngày chốt báo cáo: 24/07/2026  
Dự án: Vinhomes AI Real Estate Advisor  
Hạ tầng chuẩn: AWS EC2 `52.221.55.193`, miền `vsocintern.online`

## 1. Tóm tắt kết quả

Week 1 đã hoàn thành phần nền tảng ở mức repository và local validation: có
replica development/staging hoạt động trên AWS EC2, pipeline CI/CD dùng image
bất biến, Semgrep SAST, OWASP ZAP DAST, SARIF cho GitHub Code Scanning và lớp
chuẩn hóa JSONL dùng chung.

Ngày 24/07/2026, kiểm tra HTTP độc lập ghi nhận:

| Endpoint | Kết quả |
| --- | --- |
| `https://dev.vsocintern.online` | HTTP 200 |
| `https://api-dev.vsocintern.online/ready` | HTTP 200, database `ok` |
| `https://vsocintern.online` | HTTP 200 |
| `https://api.vsocintern.online/ready` | HTTP 200, database `ok` |

Phần security workflow và data-lake job đang tồn tại trong working tree nhưng
chưa được coi là đã chạy trên GitHub cho đến khi commit/push và có một Actions
run thành công. Đây là bước nghiệm thu còn lại, không phải kết quả đã xác nhận.

## 2. Đối chiếu deliverable

| Yêu cầu Week 1 | Bằng chứng | Trạng thái |
| --- | --- | --- |
| Deploy replica vào staging | `dev.vsocintern.online`, API readiness 200 | Hoàn thành |
| CI build/test và CD staging/production | `ci.yml`, `cd-single-ec2.yml`, OIDC + SSM + digest | Đã triển khai |
| Tích hợp SAST | Semgrep Docker, JSON local, SARIF CI | Hoàn thành ở repo/local; chờ CI run mới |
| Tích hợp DAST | ZAP Docker, stack cô lập, JSON + SARIF | Hoàn thành ở repo/local; chờ CI run mới |
| Aggregate raw outputs | JSONL `findings.jsonl`, `summary.json`, CI artifact | Hoàn thành bản artifact lake |
| Manual attack-surface analysis | `week1-attack-surface-baseline.md` | Hoàn thành baseline |
| Durable enterprise data lake/SIEM | Chưa có S3/OpenSearch/SIEM | Backlog |
| Authenticated active DAST | Chưa thực hiện | Backlog |

## 3. Kiến trúc CI/CD và staging

Luồng application:

```text
push dev/main
  -> backend lint + pytest
  -> frontend npm build
  -> build/push backend + frontend lên GHCR
  -> lưu deployment manifest theo commit và image digest
  -> CD workflow_run
  -> GitHub OIDC nhận AWS credential tạm thời
  -> SSM document cố định
  -> /usr/local/sbin/ocean-park-deploy
  -> health check, ledger và auto rollback
```

`dev` triển khai `ocean-park-dev`; `main` triển khai `ocean-park-prod`. Caddy là
edge duy nhất publish 80/443. Database và application port chỉ nằm trong Docker
network. Production deploy tạo và kiểm tra PostgreSQL dump trước khi đổi image.

Điểm kiểm soát đáng chú ý:

- không lưu AWS access key hoặc SSH private key trong GitHub;
- trust policy OIDC ràng buộc repository/environment;
- SSM chỉ gọi document được giới hạn, không cấp shell tùy ý;
- deploy đúng cặp backend/frontend theo full commit và registry digest;
- host dùng lock để serialize dev/prod và rollback khi readiness thất bại.

## 4. SAST với Semgrep

Pipeline dùng `semgrep/semgrep:1.169.0` và ruleset OWASP Top 10. Local command:

```powershell
.\scripts\security\scan.ps1 sast
```

Baseline gần nhất:

- 84 files;
- 224 rules;
- parse 100%;
- 0 findings;
- 0 errors.

Trong quá trình kiểm chứng, hai đoạn TSX chứa ký tự `&` thô đã được sửa để toàn
bộ source parse thành công. Kết quả 0 findings không thay thế code review,
dependency scan hoặc review authorization/business rules.

CI xuất `semgrep.sarif`, upload GitHub Code Scanning và lưu artifact 30 ngày.

## 5. DAST với OWASP ZAP

Pipeline dùng `zaproxy/zap-stable:2.17.0`. DAST dựng database/backend/frontend
riêng, vô hiệu tích hợp LLM bên ngoài để tránh phát sinh chi phí hoặc gửi payload
scan ra provider. Local command:

```powershell
.\scripts\security\scan.ps1 dast
```

Kết quả baseline local:

| Target | Alert types | Instances |
| --- | ---: | ---: |
| Frontend | 4 | 20 |
| Backend Swagger UI | 6 | 7 |
| Tổng | 10 theo từng report | 27 |

Sau chuẩn hóa severity: 14 medium, 7 low, 6 informational. Các vấn đề chính là
CSP, anti-clickjacking, SRI, cross-domain JavaScript, header leakage và một số
security header. ZAP exit code khác 0 đã được xử lý bằng baseline mode và log
backend/database rõ ràng; script cũng kiểm tra Docker daemon trước khi chạy.

## 6. Unified security data lake

`aggregate_security_reports.py` nhận Semgrep JSON/SARIF và ZAP JSON, chuẩn hóa
vào schema chung:

- scanner, rule ID, title, severity, confidence;
- target và location HTTP/source;
- category, references, source report, ingestion time.

Kết quả local:

```text
security-data-lake/
  findings.jsonl
  summary.json
```

Job `aggregate` tải artifact từ SAST/DAST và xuất
`unified-security-data-lake` với retention 30 ngày. Unit test cho parser/normalizer
đã pass. Đây là data-lake layer ở mức CI artifact; để đạt lưu trữ enterprise dài
hạn cần đẩy JSONL sang S3 versioned/encrypted rồi lập lifecycle, query layer và
SIEM connector.

## 7. Manual attack-surface analysis

Các trust boundary chính:

- Internet → Caddy → Next.js/FastAPI;
- FastAPI → PostgreSQL;
- FastAPI → LLM/embedding provider;
- GitHub Actions → OIDC/IAM → SSM → EC2;
- dev và prod cùng một EC2 host.

Bề mặt rủi ro cao nhất không nằm ở lỗi cú pháp mà ở:

- RBAC/authorization và IDOR cho customer, sales, permissions;
- PII trong CRM/chat và dữ liệu outbound sang LLM;
- prompt injection, citation và fallback behavior;
- public Swagger/OpenAPI;
- dev/prod chia sẻ host/failure domain.

Chi tiết và backlog nằm tại
`docs/security/week1-attack-surface-baseline.md`.

## 8. Liên hệ năng lực S7 và S10

### S7 — CI/CD Pipeline & LLMOps

Đã có:

- automated backend tests, frontend build và immutable container pipeline;
- environment-specific model/provider configuration;
- guardrail test cho prompt injection, input length, fallback và PII log
  sanitization;
- RAG/retrieval regression tests trong pytest;
- security scan tự động và artifact hóa kết quả.

Chưa hoàn thiện:

- prompt registry/version ID độc lập với commit;
- production model-drift telemetry và alert;
- GPU FinOps (hệ thống hiện gọi hosted API, không tự vận hành GPU);
- eval score gate riêng trong CI thay vì chỉ chạy chung trong pytest.

### S10 — Sử dụng AI coding assistant có kiểm soát

AI assistant được dùng để rà soát cấu trúc, dựng automation, debug Docker/ZAP và
chuẩn hóa report. Các quyết định bảo mật vẫn được kiểm tra thủ công: quyền IAM,
SSM scope, endpoint DAST, SARIF location, Docker volume permission, TSX parse và
logic role/business. Ví dụ quan trọng là không tiếp tục active API scan khi nó
có nguy cơ treo hoặc làm thay đổi dữ liệu; baseline scan được chọn và giới hạn
được ghi rõ thay vì coi kết quả AI sinh ra là đúng mặc định.

## 9. Hạn chế và kế hoạch tiếp theo

Ưu tiên nghiệm thu:

1. Commit/push security changes và lưu URL/screenshot Actions run thành công.
2. Xác nhận SARIF xuất hiện trong Code Scanning hoặc ghi nhận giới hạn license.
3. Chạy ZAP passive scan trực tiếp trên `dev.vsocintern.online` để kiểm tra Caddy
   headers, sau khi được phê duyệt phạm vi.
4. Thiết kế authenticated DAST theo role và test IDOR/business logic.
5. Đẩy JSONL vào S3 encrypted/versioned, thêm retention và Athena/OpenSearch.
6. Thêm dependency, container image, secret và IaC scanning.
7. Tách production khỏi development khi cần security/availability boundary.

## 10. Danh mục bằng chứng

- `.github/workflows/ci.yml`
- `.github/workflows/cd-single-ec2.yml`
- `.github/workflows/security.yml`
- `compose.security.yml`, `compose.dast.yml`
- `scripts/security/scan.ps1`, `scripts/security/scan.sh`
- `scripts/security/zap_json_to_sarif.py`
- `scripts/security/aggregate_security_reports.py`
- `tests/security/test_aggregate_security_reports.py`
- `deploy/aws/single-ec2-cicd.yml`
- `docs/deployment/aws-single-ec2-runbook.md`
- `docs/security-scanning.md`
- `docs/security/week1-attack-surface-baseline.md`

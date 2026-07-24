# Chỉ mục tài liệu DevOps hiện hành

Nguồn triển khai chính thức duy nhất là AWS EC2 tại `52.221.55.193` với miền
`vsocintern.online`. Các tài liệu VPS/Nginx/Cloudflare và miền cũ đã được loại
khỏi repository để tránh vận hành nhầm.

| Tài liệu | Mục đích |
| --- | --- |
| [AWS single-EC2 runbook](../deployment/aws-single-ec2-runbook.md) | Bootstrap, GitHub OIDC, AWS SSM, deploy, rollback và backup/restore |
| [SAST/DAST guide](../security-scanning.md) | Chạy Semgrep/ZAP local và trên CI/CD |
| [Week 1 attack-surface baseline](../security/week1-attack-surface-baseline.md) | Bề mặt tấn công và kết quả scan ban đầu |
| [Week 1 report](../reports/week1-sast-dast-cicd-baseline-report.md) | Báo cáo nộp mentor và trạng thái deliverable |
| [LLM provider design](llm-provider-openrouter-openai-design.md) | Cấu hình provider LLM bằng environment |

Workflow hiện hành:

- `.github/workflows/ci.yml`
- `.github/workflows/cd-single-ec2.yml`
- `.github/workflows/security.yml`

# Version 2.0.0 — Rebuild theo BAN_THIET_KE_V2

Ngày: 2026-07-08 · Branch: `TranMinhQuang`
Nguồn thiết kế: `BAN_THIET_KE_V2.md` (source of truth)

## 1. Tóm tắt

Rebuild toàn hệ thống theo thiết kế V2: bỏ đăng nhập khách hàng, gộp
`leads + customer_accounts → customers`, chat gating sau 3 tin, agent 4 node với
rubric chấm điểm lead, RBAC phân quyền chi tiết, CRM admin mới, chat widget mới.

Quyết định vận hành đã chốt với chủ dự án:
- Data production: **migrate giữ dữ liệu** (gộp theo phone, backup trước khi apply).
- FE: giữ pattern CSS hiện có + Chart.js (không đổi sang shadcn/TanStack).
- Notification real-time cho sale: **để sau** (lead nóng hiện qua CRM).
- RAG: **legacy JSON** + embedding nhẹ; pgvector tắt (`RAG_PROVIDER=legacy`).

## 2. Phase 0 — Dọn dẹp (trạng thái trước đó: crash khi import)

- Revert 3 file refactor dở (`admin.py`, `agent_routes.py`, `schemas.py`) về HEAD.
- Xóa lớp async legacy `src/database.py` + model legacy (`lead.py`, `chat.py`,
  `property.py`) + scripts chết (`seed_db.py`, `ingest_knowledge_chunks.py`).
- Xóa migration hỏng `529032eb265a_refactor_customers.py`.
- Sửa JSX lặp ngoài component trong `admin/(dashboard)/page.tsx`.
- **Sửa mojibake nghiêm trọng** trong `src/services/vinhomes_data.py` (23 dòng) và
  `rag_node.py`: marker "đang cập nhật" bị double-encode nên không bao giờ match →
  giá rác lọt vào RAG. Commit gây lỗi: `9851251`.
- Sửa data bẩn: 6 trường giá của The Senique chứa số tầng ("Tầng 2 – 36 đang cập
  nhật!") bị parse thành khoảng giá 2-36 tỷ.
- Recommender: phân khu không rõ giá bị trừ 15 điểm khi khách đưa ngân sách.
- Sửa `.env` local: `RAG_PROVIDER=vector_chunks` (giá trị không hợp lệ) → `legacy`.
- Lưu ý: thay đổi uncommitted trong `cleaned_data/` (rename the-bayfront →
  lumiere-orient-pearl từ lần chạy preprocess 2026-07-08) đã bị revert về HEAD vì
  chứa cùng lỗi parse giá; backup còn tại `cleaned_data/.backup_20260708_*`.
  Nếu cần rename này, chạy lại preprocess sau khi sửa parser.

## 3. Phase 1 — Schema V2 + migration

- `src/models/entities.py` viết lại: `customers` (trung tâm), `customer_notes`,
  `purchase_history`, `sale_awards`, `permissions`, `user_permissions`,
  `user_subdivisions`; `users` thêm phone/title/ca làm việc/ngày vào làm;
  `conversations` thêm `user_message_count`/`is_lead_captured`;
  `messages.sender → role` + cột `meta` JSON.
- Migration `20260708_04_schema_v2_customers`: **giữ dữ liệu** — gộp
  customer_accounts + leads theo phone (lead mới nhất thắng), map status cũ
  (qualified→consulting, closed→won), remap conversations/lead_notes, đếm lại
  user_message_count. Downgrade khôi phục schema cũ (mất password_hash — chấp nhận).
- Đã verify bằng script: seed dữ liệu schema cũ → upgrade → assert gộp đúng →
  downgrade về base sạch (SQLite). **Chưa chạy trên PostgreSQL staging.**
- Seed: `src/db/seed_permissions.py` (9 quyền Mục 10) chạy trong lifespan.

## 4. Phase 2 — Backend core

- RBAC: `require_permission(code)` (`src/api/dependencies.py`) — admin bypass,
  sale cần quyền trong `user_permissions`. `GET /auth/me` trả `{user, permissions}`.
- Router mới: `customers.py` (capture/contact public + CRM đầy đủ), `sales.py`
  (CRUD + awards + subdivisions + permissions matrix), `dashboard.py`, `fallback.py`.
- `agent_routes.py` viết lại: gating 3 tin, rate-limit 5 tin/phút, capture SĐT
  trong chat, fallback rules, lưu meta (intent/citations/detected) vào messages.
- Xóa: `customer_auth.py`, `admin.py`, `conversations.py`, `leads.py`,
  `guest_chat_store.py` (mọi hội thoại giờ lưu DB, khách ẩn danh có conversation
  với customer_id null).

## 5. Phase 3 — AI Agent V2

- `profile_node.py` mới: rubric Mục 6.3 (xem nhà +30, gặp sale +25, đặt cọc +25,
  zone focus +15, để lại SĐT +15, ngân sách +10, so sánh +8, chi tiết +5,
  chung chung −5, off-topic −10); ngưỡng hot ≥ 55 / warm 25-54 / cold < 25;
  phân loại real_need/investor/ghost/unknown rule-based.
  (LLM structured-output classify có thể bổ sung sau — hiện rule-based để không
  tăng latency/chi phí.)
- Graph 4 node: intent → rag → profile → llm.
- `sale_assigner.py`: lead nóng → ưu tiên sale phụ trách phân khu, round-robin
  theo tải; status new → contacted.
- Điểm cộng dồn: khách đã capture đọc từ `customers.lead_score`; khách ẩn danh
  đọc từ meta tin AI gần nhất.

## 6. Phase 4 — Frontend

- `chat-widget.tsx` mới (Tailwind): bubble, cửa sổ 440px, quick actions, nút
  "Tạo đơn tư vấn" cố định, form đầy đủ (phân khu/loại căn/ngân sách/mục đích/
  thời gian liên hệ/consent), tự bung + khóa input khi `require_lead_capture`.
- Xóa trang khách: `dang-ky/`, `dang-nhap/`, `login/`, `register/` +
  `lib/customer-auth.ts`, `lib/auth-context.tsx`.
- Admin: `customers/` (bảng + chi tiết: chat, loại/nhiệt độ/điểm, nhu cầu, lịch sử
  mua, ghi chú, phân công), `sales/` (CRUD + ca làm + phân khu + giải thưởng +
  số căn đã bán), `permissions/` (ma trận tick), `profile/`, dashboard Chart.js
  (doughnut loại khách/nhiệt độ, phễu trạng thái, top phân khu, trend 30 ngày,
  hiệu suất sale), fallback-rules đổi endpoint. Menu theo `permissions`.
- `SubdivisionSummaryResponse` thêm `id` phục vụ gán phân khu phụ trách.

## 7. Kiểm thử

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q   # 226 passed, 1 skipped (live LLM)
.\.venv\Scripts\ruff.exe check src tests          # pass
cd FE; npm run build                              # Compiled successfully
```

Test mới đáng chú ý:
- `tests/test_api/test_customers_crm.py` — gating 3 tin, capture, RBAC visibility,
  permission grant/revoke runtime, notes/purchases, sales CRUD, dashboard, fallback.
- `tests/test_api/test_handover_assignment.py` — hot lead → auto-assign đúng nhóm
  sale phụ trách phân khu; +15 điểm khi capture.
- `tests/test_agents/test_profile_node.py` — từng tín hiệu rubric + ngưỡng nhiệt độ.
- `tests/test_e2e/test_user_journeys.py` — journey đầy đủ browse → chat → gate →
  capture → hot → CRM; điểm cộng dồn qua pipeline thật.

## 8. Deploy notes (CHƯA deploy)

1. **Backup trước**: `bash scripts/deploy/backup_postgres.sh` trên VPS.
2. `alembic upgrade head` — migration sẽ gộp dữ liệu leads/customer_accounts.
3. `.env` staging/production cần thêm (tùy chọn, có default):
   `FREE_MESSAGE_LIMIT=3`, `CHAT_RATE_LIMIT_PER_MINUTE=5`, `RAG_PROVIDER=legacy`.
4. FE build mới bắt buộc deploy cùng backend (API đổi lớn, không tương thích cũ).
5. Sau deploy: kiểm tra `/ready`, `/agent/status`, đăng nhập admin, chat thử 4 tin
   để xác nhận gate, submit form, xem khách trong CRM.

## 9. Việc còn lại / đề xuất tiếp theo

- Chạy migration thử trên bản sao PostgreSQL staging trước khi apply thật.
- Browser QA chat widget (desktop/mobile) khi chạy dev server thật.
- LLM structured-output cho `customer_type` (bổ sung rule-based) nếu muốn tinh hơn.
- Notification real-time cho sale khi có lead nóng (đã thống nhất để sau).
- Report export (`report.export` permission đã seed nhưng chưa có endpoint).

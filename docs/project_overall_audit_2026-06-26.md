# Báo cáo audit tổng thể dự án — 26/06/2026

## 1. Kết luận ngắn gọn

Dự án hiện đã vượt qua giai đoạn “prototype cục bộ” và đang ở mức **staging MVP có thể demo được**:

- Public website chạy được.
- Admin dashboard đăng nhập và quản lý lead được.
- Database PostgreSQL staging chạy được trên VPS.
- CI/CD đã có backend test, frontend build, Docker image publish qua GHCR.
- Staging deploy lên VPS đã thành công.
- AI Agent đã được merge vào codebase, có LangGraph flow, guardrail, RAG đơn giản và endpoint `/agent/chat`.
- Tuy nhiên, ở trạng thái thực tế mới nhất, **AI chưa chat được trên staging**: khi bấm chat, endpoint `/agent/chat` đang trả lỗi HTTP 500.

Tuy nhiên, dự án **chưa nên coi là production-ready**. Điểm rủi ro lớn nhất hiện tại là phần Agent được merge vào nhưng chưa đồng nhất hoàn toàn với kiến trúc database/dashboard đã xây trước đó. Code đang tồn tại hai lớp model/database song song:

```text
src.db.* + src.models.entities      → dashboard, catalog, contact form, admin
src.database + src.models.chat/lead/property → agent, AI lead scoring, async APIs
```

Điều này không làm toàn hệ thống sập ngay, vì test hiện tại vẫn pass, nhưng là rủi ro kiến trúc lớn nếu tiếp tục phát triển AI, lead scoring và CRM.

Đánh giá tổng thể hiện tại sau khi cập nhật tình trạng AI 500:

```text
Mức hoàn thiện so với mục tiêu ban đầu: khoảng 65%
```

Nếu tách theo mục tiêu:

| Mảng | Mức hoàn thiện | Nhận xét |
| --- | ---: | --- |
| Public UI/UX | 80% | Website, phân khu, liên hệ, chat widget đã có; còn thiếu polish/error detail/streaming |
| Backend API nền | 75% | API chính chạy được, auth/dashboard ổn; còn trùng route/model |
| Database | 65% | Có migration, seed và schema `subdivisions` phù hợp hướng hiện tại; còn rủi ro vì có model song song |
| AI Agent | 40% | Có LangGraph/intent/RAG/LLM node trong code, nhưng staging chat hiện trả 500 nên chưa đạt trạng thái usable |
| Lead/Admin CRM | 75% | Login, dashboard, leads, notes, users, fallback rules đã có |
| DevOps/Staging | 78% | GHCR, VPS deploy, Docker, reports tốt; Docker buildx còn không ổn định |
| Production readiness | 45% | Cần domain/HTTPS ổn định, backup/rollback test thật, secrets, monitoring, hardening |
| Testing | 78% | Backend 141 tests pass, FE build pass; thiếu E2E browser/deploy smoke test |

## 2. Evidence đã kiểm tra

### 2.1. Kiểm thử backend

Đã chạy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Kết quả output:

```text
141 passed
```

Ghi chú: ở một lần chạy song song, wrapper command timeout sau khi test đã in kết quả pass. Trước đó và sau đó backend tests đều cho kết quả pass.

### 2.2. Build frontend

Đã chạy:

```powershell
cd FE
npm run build
```

Kết quả:

```text
✓ Compiled successfully
```

Các route build ra:

```text
/
/_not-found
/admin
/admin/conversations
/admin/fallback-rules
/admin/leads
/admin/login
/admin/users
/lien-he
/phan-khu
/phan-khu/[slug]
```

### 2.3. Trạng thái DevOps thực tế

Theo lịch sử làm việc và các report DevOps:

- GHCR đã có backend/frontend package.
- VPS đã clone repo và deploy staging bằng `scripts/deploy/staging_deploy.sh`.
- Backend/database/frontend staging đã từng đạt trạng thái healthy.
- Đã phát sinh và xử lý các lỗi staging:
  - PostgreSQL role/password.
  - Alembic permission.
  - JWT secret quá ngắn.
  - Frontend readiness check quá sớm.
  - `crypto.randomUUID` trên HTTP/IP.
  - frontend gọi nhầm `localhost:8000`.
  - AI chưa cấu hình key/provider.
  - AI chat hiện vẫn trả HTTP 500 khi user bấm chat.

## 3. Dự án đã làm được gì

### 3.1. Public frontend

Đã có:

- Trang chủ.
- Trang danh sách phân khu.
- Trang chi tiết phân khu.
- Trang liên hệ.
- Chat widget dạng floating button.
- Header/footer và layout responsive cơ bản.
- Frontend build production thành công.

Luồng public hiện tại:

```text
User → Website → xem phân khu → gửi form liên hệ hoặc chat với AI
```

Điểm tốt:

- UI khá đồng nhất về visual direction.
- Dữ liệu phân khu đã hiển thị được.
- Form liên hệ đã lưu lead vào dashboard.
- Chat widget đã nối endpoint `/agent/chat`, nhưng hiện endpoint đang lỗi 500 trên staging nên chưa thể coi là AI usable.

Điểm còn thiếu:

- Chat widget chưa stream token.
- Khi API lỗi, UI chỉ hiện thông báo generic, khó debug cho user/tester.
- Session chat hiện tạo bằng state memory, chưa đồng nhất với localStorage conversation layer cũ.
- Chưa có UX rõ ràng khi AI yêu cầu handover để mở form lead ngay trong chat.

### 3.2. Backend nền và API

Đã có:

- FastAPI app.
- CORS theo env.
- `/health`, `/ready`.
- `/api/v1/subdivisions`.
- `/api/v1/contact`.
- `/api/v1/auth/login`, `/auth/me`, `/auth/users`.
- `/api/v1/admin/dashboard`.
- `/api/v1/admin/leads`.
- `/api/v1/admin/conversations`.
- `/agent/chat`, `/agent/recommend`, `/agent/lead-score`, `/agent/status`.

Điểm tốt:

- Có auth JWT cho dashboard.
- Có RBAC `admin`/`sale`.
- Có seed admin.
- Có validation phone.
- Có route AI riêng, không chèn thẳng vào `/api/v1` legacy.

Điểm còn thiếu/rủi ro:

- Một số endpoint bị trùng khái niệm:
  - `/api/v1/contact` trong `src.api.leads`
  - `/api/v1/leads` trong `src.api.lead_routes`
  - `/api/v1/admin/leads` trong `src.api.admin`
- Có cả API lead sync dashboard và async AI lead. Hai nhóm này dùng model khác nhau.
- Chưa có global exception middleware chuẩn hóa lỗi toàn app.
- Chưa có request ID / structured logging.
- Chưa có masking PII trong logs.

### 3.3. Database

Đã có:

- Alembic migration:
  - `20260620_01_initial_schema.py`
  - `20260622_02_auth_and_lead_workflow.py`
- Các bảng dashboard/catalog:
  - `subdivisions`
  - `apartment_specs`
  - `amenities`
  - `sales_policies`
  - `leads`
  - `conversations`
  - `messages`
  - `fallback_rules`
  - `users`
  - `lead_notes`
- Seed từ `cleaned_data/cleaned_apartment_zones.json`.

Điểm tốt:

- Schema đủ cho public website và dashboard cơ bản.
- Có migration, không chỉ dùng auto-create.
- Có seed idempotent cho catalog/admin.

Thiết kế database hiện tại đã được chốt lại theo hướng **không dùng hierarchy `project -> zone -> subzone -> building`**. Schema chính của sản phẩm hiện tại là:

```text
subdivisions -> apartment_specs / amenities / sales_policies
```

Điểm cần lưu ý:

- File `src.models.property` vẫn còn các model `Project`, `Zone`, `Subzone`, `Building`, `KnowledgeChunk`, nhưng hiện không còn là hướng thiết kế được chọn.
- Agent/RAG chủ yếu đọc JSON qua `src.services.vinhomes_data`, chưa dùng trực tiếp dữ liệu seed từ bảng `subdivisions`.
- Có hai bộ model `Conversation`, `Message`, `Lead` khác nhau:
  - `src.models.entities` dùng `id: int`, field `sender`, dashboard.
  - `src.models.chat` dùng `id: uuid string`, field `role`, agent.
  - `src.models.lead` dùng `id: uuid string`, AI lead scoring.

Đây là điểm cần xử lý trước khi mở rộng AI/CRM.

### 3.4. AI Agent

Đã có:

- LangGraph graph:

```text
intent_node → rag_node → llm_node
```

- Intent detection:
  - greeting
  - consult
  - price_query
  - zone_match
  - handover
  - out_of_scope
- Regex guardrail cho prompt injection và out-of-scope.
- Handover response khi hỏi căn cụ thể/đặt cọc/quỹ căn.
- RAG đơn giản bằng JSON data.
- Gợi ý phân khu theo budget/unit/purpose.
- LLM provider layer OpenAI-compatible.
- Cấu hình mới hỗ trợ:
  - OpenRouter
  - OpenAI
  - custom OpenAI-compatible gateway

Điểm tốt:

- Agent có cấu trúc rõ ràng, test được từng node.
- Có fallback static cho greeting/handover/out-of-scope.
- Có disclaimer giá và cảnh báo low-confidence ở mức code.
- Có rate limit/quota theo conversation/session ở `/agent/chat`.

Điểm chưa đạt/thiếu:

- Knowledge verifier chưa phải node riêng sau LLM như trong spec; hiện logic disclaimer/low-confidence nằm trong `llm_node`.
- RAG không dùng vector database/embedding; chỉ score/filter JSON.
- Prompt nói chỉ dùng context, nhưng chưa có validator hậu kiểm mạnh để bắt hallucination ngoài context.
- Chat history của Agent lưu vào bảng async `src.models.chat`, không đồng bộ với conversation dashboard đang đọc `src.models.entities`.
- Frontend chat không dùng conversation API v0.3.0 nữa, mà gọi thẳng `/agent/chat`; điều này làm lịch sử hội thoại admin có thể không hiển thị đúng nếu database/model khác nhau.
- Rate limiting trả HTTP 200 với message thân thiện, trong khi spec acceptance từng nhắc 429. Đây là quyết định sản phẩm có thể chấp nhận, nhưng cần ghi rõ.
- `score_lead` vẫn gọi `get_llm` và fallback rule-based tốt, nhưng chưa dùng provider status rõ như `llm_node`.
- Trên staging hiện tại, `/agent/chat` đang trả HTTP 500 khi user chat, nên ưu tiên đầu tiên là lấy log backend và sửa lỗi runtime trước khi mở rộng feature.

### 3.5. Admin dashboard / CRM

Đã có:

- Login page.
- JWT auth.
- Dashboard stats.
- Lead list/search/detail.
- Update status.
- Assign sale.
- Lead notes.
- Fallback rules.
- User management.
- Conversation admin page.

Điểm tốt:

- Đủ để demo mentor về CRM nội bộ.
- RBAC nằm ở backend.
- Password hash bằng Argon2.

Điểm còn thiếu:

- Login form vẫn có default demo credentials trong UI:

```text
Production demo: https://c2-app-005.quangtm.site/admin/login
admin@gmail.com / admin123456789Aa@
```

Điều này cần bỏ trước production.

- Không có refresh token/logout server-side/revoke token.
- Không có đổi mật khẩu.
- Không có audit log.
- Chưa masking phone/email ở list/log.
- Conversation dashboard có nguy cơ không đọc được hội thoại AI do lệch model/schema.

### 3.6. DevOps

Đã có:

- Dockerfile backend.
- Dockerfile frontend.
- docker-compose local.
- docker-compose registry staging.
- docker-compose HTTPS/Caddy.
- GitHub Actions CI:
  - backend lint/tests.
  - frontend build.
  - Docker build and publish GHCR.
- GHCR images.
- VPS staging deploy script.
- HTTPS/Caddy scripts.
- Backup/restore/rollback scripts.
- Reports DevOps theo version.

Điểm tốt:

- Quy trình staging gần đúng flow thực tế:

```text
dev branch → GitHub Actions → GHCR → VPS pull image → docker compose up
```

- Đã thực chiến sửa nhiều lỗi staging.

Điểm còn thiếu/rủi ro:


- `docker-compose.https.yml` vẫn có `DATABASE_URL` không kèm password, khác với hotfix ở `docker-compose.registry.yml`.
- Production flow chưa được chạy end-to-end thực tế.
- Chưa có monitoring/log aggregation.
- Chưa có secret rotation/runbook cho key bị lộ.
- Chưa có deploy tự động từ GitHub Actions vào VPS; hiện vẫn là manual pull/deploy.

## 4. Tổng quan thiết kế đã đồng nhất chưa?

Kết luận: **chưa đồng nhất hoàn toàn**.

Các phần public UI, dashboard, Docker, CI/CD tương đối đồng nhất. Nhưng phần Agent mới merge đang tạo ra một đường kiến trúc song song.

### 4.1. Điểm đồng nhất

- Frontend dùng `NEXT_PUBLIC_API_URL`/`API_URL` nhất quán hơn sau hotfix.
- Backend có config tập trung qua `src.config.Settings`.
- DevOps dùng `.env` và Docker Compose rõ ràng.
- Admin dashboard dùng JWT/RBAC nhất quán.
- Agent có flow LangGraph tương đối rõ.

### 4.2. Điểm chưa đồng nhất

#### Vấn đề 1: hai database base/session

Hiện có:

```text
src.db.base.Base + src.db.session        → sync SQLAlchemy, dashboard/catalog
src.database.Base + src.database.get_session → async SQLAlchemy, agent/AI routes
```

Rủi ro:

- Migration chỉ theo một phần schema.
- Auto-create có thể tạo bảng ngoài Alembic.
- Dashboard và Agent có thể ghi/đọc khác bảng hoặc khác cấu trúc.
- Khó debug khi staging/production có data thật.

#### Vấn đề 2: hai model Lead/Conversation/Message

Dashboard:

```text
src.models.entities.Lead
src.models.entities.Conversation
src.models.entities.Message
```

Agent:

```text
src.models.lead.Lead
src.models.chat.Conversation
src.models.chat.Message
```

Rủi ro:

- Lead do contact form tạo chưa chắc liên kết với AI lead.
- Conversation do AI tạo chưa chắc hiện đúng trong dashboard.
- Migration schema dùng `sender`, trong khi Agent model dùng `role`.

#### Vấn đề 3: code còn dấu vết của thiết kế hierarchy đã bỏ

Bạn đã quyết định bỏ hướng:

```text
project -> zone -> subzone -> building
```

Vì vậy schema runtime nên tập trung vào:

```text
subdivisions
apartment_specs
amenities
sales_policies
```

Rủi ro hiện tại không phải là “chưa triển khai hierarchy”, mà là code vẫn còn một số dấu vết của hướng cũ như `src.models.property`. Các phần này cần được đánh dấu deprecated hoặc loại khỏi runtime để tránh thành viên khác tiếp tục phát triển nhầm hướng.

#### Vấn đề 4: Agent chưa thật sự nối chặt lead capture

Spec mong muốn:

```text
AI handover → mở form → lưu lead → migrate chat history → sale đọc được
```

Hiện tại:

- AI có `trigger_handover`.
- Frontend chưa tự mở lead form theo `trigger_handover`.
- Contact form lưu lead theo dashboard model.
- AI lead route lưu lead theo async model khác.
- Dashboard đọc lead theo dashboard model.

## 5. Lỗi hoặc thiếu sót hiện tại

### Ưu tiên P0 — cần xử lý trước khi phát triển thêm Agent

1. Sửa lỗi `/agent/chat` HTTP 500 trên staging.
2. Hợp nhất database/model layer.
3. Hợp nhất conversation/lead schema để Agent và Dashboard đọc cùng dữ liệu.
4. Chốt `subdivisions` là schema catalog chính; không tiếp tục phát triển `project -> zone -> subzone -> building`.
5. Sửa `docker-compose.https.yml` cho đồng bộ DATABASE_URL có password.
6. Xác minh OpenRouter model/key trên staging bằng `/agent/status` và `/agent/chat`.

### Ưu tiên P1 — cần xử lý trước production

1. Bỏ credentials demo khỏi login UI.
2. Bổ sung PII masking cho logs.
3. Bổ sung global exception handler.
4. Bổ sung monitoring/logging tối thiểu.
5. Ổn định Docker buildx hoặc đổi chiến lược Docker build CI.
6. Test Cloudflare/HTTPS end-to-end.
7. Test backup/restore trên VPS thật.

### Ưu tiên P2 — cải thiện sản phẩm

1. Chat streaming.
2. Semantic/vector RAG.
3. Knowledge verifier node riêng.
4. Admin UI xem AI score/reason và chat-to-lead linkage.
5. Better UX cho handover.
6. E2E browser tests.

## 6. Các điểm phù hợp với mục tiêu ban đầu

| Mục tiêu ban đầu | Hiện trạng | Đánh giá |
| --- | --- | --- |
| Website tư vấn bất động sản | Đã có | Đạt |
| Hiển thị phân khu, chi tiết, tiện ích, chính sách | Đã có qua cleaned data/subdivisions | Đạt một phần |
| Thu thập lead | Đã có contact form và admin leads | Đạt |
| Admin dashboard | Đã có auth, leads, notes, users, fallback rules | Đạt khá tốt |
| AI Agent LangGraph | Đã có intent/rag/llm graph nhưng staging đang lỗi 500 khi chat | Chưa đạt usable |
| Guardrails | Có regex injection/out-of-scope/handover | Đạt một phần |
| Hallucination prevention | Có prompt/disclaimer, chưa có verifier mạnh | Đạt một phần |
| Persistent chat history | Có, nhưng hai schema song song | Chưa đạt vững |
| Lead scoring | Có LLM + rule fallback | Đạt một phần |
| Rate limit/quota | Có theo session trong `/agent/chat` | Đạt một phần |
| Docker staging | Đã deploy VPS | Đạt |
| CI/CD | Có GitHub Actions/GHCR | Đạt một phần |
| Production | Có runbook/script, chưa chạy thật | Chưa đạt |

## 7. Đánh giá phần Agent do member khác merge

Phần Agent có nền tảng tốt:

- LangGraph flow rõ.
- Intent node có guardrail.
- RAG node có scoring logic.
- LLM node có prompt an toàn.
- Endpoint contract rõ.
- Test có một số case guardrail/handover/out-of-scope.

Nhưng chưa phù hợp hoàn toàn với thiết kế đã xây trước đó vì:

1. Tự đưa vào async DB base/session riêng.
2. Tự định nghĩa lại `Lead`, `Conversation`, `Message`.
3. Không reuse conversation layer v0.3.0.
4. Không lưu AI messages vào dashboard conversation schema.
5. RAG vẫn đọc JSON, chưa tận dụng catalog `subdivisions` hiện tại.
6. Agent status/config mới cần kiểm chứng thật với OpenRouter.
7. Quan trọng nhất: `/agent/chat` hiện trả HTTP 500 trên staging, nên Agent chưa đạt mức demo được.

Kết luận: Agent có thể giữ làm nền, nhưng cần một sprint “integration hardening” trước khi build thêm feature AI.

## 8. Khuyến nghị quyết định kiến trúc

Mình khuyến nghị chọn hướng:

```text
Một database layer chính cho production: src.db.* + src.models.entities + Alembic
```

Sau đó migrate phần Agent sang dùng cùng:

```text
entities.Conversation
entities.Message
entities.Lead
```

Lý do:

- Đây là schema đang có migration staging.
- Dashboard đang dùng schema này.
- Contact form đang dùng schema này.
- Alembic đang quản lý schema này.
- Ít rủi ro hơn so với giữ hai hệ song song.

Phần async route của Agent có thể:

- tạm chuyển sang sync DB dependency để thống nhất nhanh, hoặc
- giữ async nhưng phải dùng cùng metadata/schema và migration rõ ràng.

Với giai đoạn hiện tại, phương án ít rủi ro là thống nhất model trước, tối ưu async sau.

## 9. Kết luận cuối

Dự án hiện đạt khoảng **65% mục tiêu ban đầu**.

Nó đã đủ tốt để:

- demo staging,
- trình bày flow CI/CD,
- show public website,
- show admin dashboard,
- chứng minh hướng AI Agent ở mức code, nhưng chưa demo được AI chat thật do lỗi 500.

Nó chưa đủ tốt để:

- gọi là production-ready,
- mở rộng Agent sâu trước khi sửa lỗi chat 500,
- dùng dữ liệu CRM/AI đồng nhất,
- đảm bảo lead/chat/AI score chạy xuyên suốt không lệch schema.

Việc nên làm tiếp theo không phải thêm feature mới ngay, mà là **hợp nhất kiến trúc Agent với hệ thống hiện có**.

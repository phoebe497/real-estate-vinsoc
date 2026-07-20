# Project Map for AI Agents

# Update 2026-07-08: REBUILD V2 hoàn tất — ĐỌC MỤC NÀY TRƯỚC

Nguồn sự thật: `BAN_THIET_KE_V2.md` (thư mục cha) + `ARCHITECTURE.md` (đã viết lại).
Báo cáo chi tiết: `docs/reports/version-2.0.0-v2-rebuild.md`.

Thay đổi phá vỡ tương thích so với mọi ghi chú cũ bên dưới:

- KHÔNG còn đăng nhập khách hàng (customer_accounts đã xóa). Khách chat ẩn danh,
  để lại tên+SĐT qua `POST /api/v1/customers/capture`.
- Bảng `leads` + `customer_accounts` đã GỘP thành `customers`
  (migration `20260708_04_schema_v2_customers`, giữ dữ liệu theo phone).
- `src/database.py` (async), `src/models/lead.py`, `src/models/chat.py`,
  `src/models/property.py`, `src/api/lead_routes.py`, `src/api/admin.py`,
  `src/api/customer_auth.py`, `src/api/conversations.py`, `src/api/leads.py` ĐÃ XÓA.
- API admin mới: `/api/v1/customers/*`, `/api/v1/sales/*`, `/api/v1/permissions`,
  `/api/v1/dashboard/stats`, `/api/v1/fallback-rules` (RBAC qua `require_permission`).
- Chat: `POST /agent/chat` chặn sau `FREE_MESSAGE_LIMIT` (mặc định 3) tin nếu chưa
  capture → trả `require_lead_capture=true`. `/agent/lead-score` đổi thành
  `/agent/customer-score`.
- Agent pipeline 4 node: intent → rag → **profile** (chấm điểm rubric, phân loại
  real_need/investor/ghost) → llm. Lead nóng (score ≥ 55) tự phân công sale theo
  phân khu phụ trách (`user_subdivisions`, round-robin theo tải).
- FE: chat-widget.tsx mới (bubble + form Tạo đơn tư vấn), admin menu theo quyền,
  trang `customers/`, `sales/`, `permissions/`, `profile/`; các trang
  `dang-ky/dang-nhap/login/register` và `leads/`, `users/`, `conversations/` đã xóa.
- Test: 226 passed. Chạy: `./.venv/Scripts/python.exe -m pytest tests -q`
  và `cd FE && npm run build`.

Mọi nội dung bên dưới mục này là LỊCH SỬ (trước V2) — chỉ tham khảo bối cảnh,
KHÔNG dùng làm căn cứ sửa code.

---


# Update 2026-07-04: Direct UIRealEstate replacement v0.9.9

Bao cao chi tiet:

- `docs/reports/version-0.9.9-uirealestate-direct-ui-replacement.md`

Nguyen tac moi cho public UI:

```text
UIRealEstate-main = source UI that
C2-App-005/FE = noi nhan UI
```

Khong tu redesign, khong tu data-driven hoa lai, khong giu public UI cu neu xung dot voi UIRealEstate.

Da copy truc tiep cac file/chum file UIRealEstate sang `FE`:

```text
FE/src/app/page.tsx
FE/src/app/chung-cu/page.tsx
FE/src/app/chung-cu/ChungCuContent.tsx
FE/src/app/phan-khu/page.tsx
FE/src/app/phan-khu/PhanKhuContent.tsx
FE/src/app/layout.tsx
FE/src/app/globals.css
FE/src/components/layout/Header.tsx
FE/src/components/layout/Footer.tsx
FE/src/components/PageTabs.tsx
FE/src/data/navigation.ts
FE/tailwind.config.ts
FE/postcss.config.mjs
FE/next.config.mjs
```

Dependency UI da them:

```text
lucide-react
tailwindcss
postcss
autoprefixer
```

Public UI routes dung theo UIRealEstate:

```text
/
/chung-cu
/phan-khu
```

Legacy public UI C2 files da bi xoa vi khong con duoc import va co the gay nham lan voi UIRealEstate:

```text
FE/src/components/header.tsx
FE/src/components/footer.tsx
FE/src/components/public-layout.tsx
FE/src/components/chat-widget.tsx
FE/src/components/contact-form.tsx
FE/src/components/public/static-vinhomes-page.tsx
FE/src/data/navbar.ts
FE/src/data/public-vinhomes.ts
FE/src/app/public-vinhomes.css
FE/src/app/public-styles.tsx
```

Build verification:

```powershell
cd FE
npm run build
```

Ket qua:

```text
Compiled successfully
TypeScript passed
Generated static pages successfully
15 routes generated
```

Dev server:

```text
http://localhost:3000
```

# Update 2026-07-03: Public UI rebuild v0.9.8

Bao cao chi tiet:

- `docs/reports/version-0.9.8-uirealestate-to-c2-public-ui-rebuild.md`

Ket luan target:

```text
UIRealEstate-main = folder tham chieu UI
C2-App-005/FE = frontend Next.js can duoc trien khai that
```

Khong ghi tiep vao `UIRealEstate-main` khi task la mang giao dien ve du an C2-App. Folder do chi dung de doc code/tham khao cau truc UI.

Phan public UI vua thay trong C2-App:

```text
FE/src/data/navbar.ts
FE/src/data/public-vinhomes.ts
FE/src/components/public/static-vinhomes-page.tsx
FE/src/components/header.tsx
FE/src/components/footer.tsx
FE/src/components/public-layout.tsx
FE/src/components/contact-form.tsx
FE/src/app/phan-khu/page.tsx
FE/src/app/phan-khu/[slug]/page.tsx
```

Build verification:

```powershell
cd FE
npm run build
```

Ket qua v0.9.8:

```text
Compiled successfully
TypeScript passed
Generated static pages successfully
31 routes generated
```

Dev server da duoc mo tai `http://localhost:3000`.

Luu y khoi phuc: trong mot pass bi hieu sai target, `UIRealEstate-main` da bi ghi de mot so source file. Folder nay khong phai git repo nen khong co cach `git restore` chinh xac. Thu muc anh `UIRealEstate-main/public` duoc copy nham da bi xoa.

Ngày cập nhật: 2026-06-30  
Dự án: C2-App-005 / Ocean Park Advisor  
Mục tiêu của file này: giúp AI Agent hoặc thành viên mới đọc nhanh cấu trúc, tiến độ, luồng nghiệp vụ và những điểm cần cẩn trọng trước khi sửa code.

---

# Update 2026-07-03: Public UI rebuild v0.9.7

Bao cao chi tiet:

- `docs/reports/version-0.9.7-nextjs-public-ui-rebuild.md`

Muc tieu thay doi:

- Thay public UI cu bang bo giao dien moi lay folder tham chieu `D:\Python\AI Real Estate Advisor\UIRealEstate-main` lam goc.
- Giu Next.js App Router trong `FE/`, khong chuyen frontend sang Vite.
- Port cau truc UI goc tu Vite/React sang Next.js, sau do lap lai kien truc he thong hien co vao giao dien moi.
- Chuyen public UI sang cau truc data-driven/component-driven de tranh hard-code noi dung trong component.
- Dung anh local trong `FE/public/media_files`.
- Thiet ke lai chat widget de dong bo voi visual system moi, nhung giu logic API/session/lead hien co.

Nguyen tac can nho cho cac agent sau:

```text
UIRealEstate-main = giao dien goc
C2-App-005/FE = he thong Next.js/API/auth/chat hien co can duoc lap vao giao dien goc
```

Khong tiep tuc toi uu bo UI cu theo cam tinh neu task la "lay UI trong folder UIRealEstate-main". Hay port block UI goc sang Next.js truoc, sau do moi gan data/API.

## Public UI source of truth hien tai

Frontend root:

```text
FE/
```

Data public chinh:

```text
FE/src/data/public-vinhomes.ts
```

Renderer public chinh:

```text
FE/src/components/public/static-vinhomes-page.tsx
```

Renderer nay dang port cac block tu UI goc:

```text
HeroSlider
ProjectIntro
PricingCards
ProjectOverview
LocationSection
MasterPlanSection
AmenitiesSection
ServicesOverview
LeadFormSection
SubdivisionPage detail tabs / floor plan / gallery
```

Styling public va chat:

```text
FE/src/app/public-vinhomes.css
```

Header/footer/navigation:

```text
FE/src/components/header.tsx
FE/src/components/footer.tsx
FE/src/data/navbar.ts
```

Public layout:

```text
FE/src/components/public-layout.tsx
```

Luu y: `PublicLayoutWrapper` da port them `PageTabs` noi o day man hinh tu UI goc. Neu UI nay bi thua trong production, co the xoa/sua trong file nay.

Chat widget:

```text
FE/src/components/chat-widget.tsx
```

Contact form:

```text
FE/src/components/contact-form.tsx
```

## Route public hien tai

Routes dung UI moi:

```text
/
/chung-cu
/phan-khu
/phan-khu/[slug]
/phan-khu/masteri-lakeside
/phan-khu/masteri-waterfront
/phan-khu/the-bayfront
/phan-khu/the-beverly
/phan-khu/the-london
/phan-khu/the-ocean-view
/phan-khu/the-palma
/phan-khu/the-paris
/phan-khu/the-pavilion
/phan-khu/the-sapphire
/phan-khu/the-senique-1
/phan-khu/the-senique-2
/phan-khu/the-senique-hanoi
/phan-khu/the-zenpark
/phan-khu/the-zurich
/phan-khu/toa-s2-17-the-s-vista
```

Luu y:

- Cac route static trong `/phan-khu/.../page.tsx` van ton tai va goi `StaticVinhomesPage`.
- Dynamic route `FE/src/app/phan-khu/[slug]/page.tsx` uu tien `subdivisionPages[slug]`; neu khong co static data thi fallback sang API `getSubdivision(slug)` va map response thanh `PublicPageData`.
- Neu them phan khu moi, uu tien them data vao `subdivisionPages` trong `FE/src/data/public-vinhomes.ts` truoc khi tao page rieng.

## Chat widget v0.9.7

File:

```text
FE/src/components/chat-widget.tsx
```

Logic duoc giu:

- Local session id qua `CHAT_SESSION_KEY`.
- Chat messages localStorage qua `CHAT_MESSAGES_KEY`.
- Guest message count qua `GUEST_MESSAGE_COUNT_KEY`.
- Guest limit 5 tin.
- Customer token neu da dang nhap.
- Goi `POST /agent/chat`.
- Neu backend tra `trigger_handover`, mo lead form.
- Tao lead/ticket qua `POST /api/v1/leads`.

UI moi:

- Panel navy/gold.
- Header `AI Sales Assistant`.
- Bubble user mau gold.
- Bubble AI mau xam sang.
- Quick actions:
  - `Tu van can 2PN khoang 3-4 ty`
  - `So sanh The Zenpark va The Sapphire`
  - `Toi muon nhan bang gia moi nhat`
- Lead form compact trong chat.

## Kiem thu da chay cho v0.9.7

Frontend build:

```powershell
cd FE
npm run build
```

Ket qua:

```text
Compiled successfully
TypeScript passed
Generated static pages successfully
```

HTTP checks local:

```text
GET http://127.0.0.1:3000/                     -> 200
GET http://127.0.0.1:3000/chung-cu             -> 200
GET http://127.0.0.1:3000/phan-khu             -> 200
GET http://127.0.0.1:3000/phan-khu/the-zenpark -> 200
```

Browser QA can lam tiep:

- Kiem tra desktop/mobile bang trinh duyet that.
- Kiem tra header sticky, mega menu, mobile menu.
- Kiem tra chat open/close, quick actions, guest limit, gap Sales.
- Kiem tra contact form khi backend dang chay.

Gioi han trong phien trien khai:

- Browser noi bo cua Codex khong kha dung, nen chua chup screenshot truc quan.
- Da xac minh bang `npm run build` va HTTP/text render checks.

## 1. Tóm tắt sản phẩm

Dự án là hệ thống:

- Website khách hàng mô phỏng giao diện Vinhomes Ocean Park.
- Chat AI tư vấn bất động sản.
- Đăng ký / đăng nhập khách hàng.
- CRM Admin cho quản lý lead, sale, fallback rules và lịch sử hội thoại.
- Backend API bằng FastAPI.
- Frontend bằng Next.js.
- Database PostgreSQL/SQLAlchemy, chạy local qua Docker Compose và deploy VPS bằng Docker image từ GHCR.

Luồng nghiệp vụ quan trọng hiện tại:

```text
CustomerAccount = tài khoản đăng nhập của khách hàng ngoài website
Lead = khách hàng/lead trong CRM Admin
Conversation = phiên chat
Message = tin nhắn trong phiên chat
```

Thiết kế mới đã thống nhất:

- Khách đăng ký sẽ có `CustomerAccount`.
- Khi đăng ký, hệ thống tạo hoặc liên kết một `Lead` tương ứng theo số điện thoại để Admin nhìn thấy khách.
- Một khách hàng đăng ký có thể có nhiều `Conversation`.
- Khi khách đăng xuất, chỉ xóa `session_id` trên browser; dữ liệu chat trong database vẫn giữ.
- Khách vãng lai không lưu toàn bộ chat vào database; chỉ tạo Lead nếu họ để lại số điện thoại.
- Sale chỉ được xem lead/chat được phân công; admin xem toàn bộ.

---

## 2. Stack kỹ thuật

Backend:

- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL, local có thể dùng Docker Postgres
- LangGraph cho AI Agent pipeline
- OpenAI-compatible LLM provider: OpenRouter hoặc OpenAI

Frontend:

- Next.js 16.2.9
- React 19.2.7
- TypeScript
- CSS thuần
- Public UI dùng static pages + local images trong `FE/public/media_files`

DevOps:

- Docker Compose local
- Docker image build/publish qua GitHub Actions
- GHCR packages:
  - `c2-app-005-backend`
  - `c2-app-005-frontend`
- VPS chạy staging và production bằng Docker Compose
- Nginx reverse proxy + Certbot HTTPS

---

## 3. Cấu trúc thư mục cấp cao

```text
.
├── .github/                 # GitHub Actions CI/CD workflow
├── cleaned_data/            # Data đã làm sạch cho phân khu/căn hộ/RAG
├── deploy/                  # Cấu hình reverse proxy cũ/triển khai bổ trợ
├── docs/                    # Tài liệu thiết kế, audit, report, deploy runbook
├── FE/                      # Frontend Next.js
├── migrations/              # Alembic migrations
├── raw_pages/               # HTML gốc từ vinhomeoceanpark.com.vn để dựng UI tĩnh
├── scripts/                 # Script seed, preprocess, deploy, backup/restore
├── src/                     # Backend FastAPI + AI Agent + services + models
├── tests/                   # Pytest backend/unit/integration/agent tests
├── docker-compose.yml       # Local compose build từ source
├── docker-compose.registry.yml # VPS compose dùng image từ GHCR
├── docker-compose.deploy.yml   # Compose deploy legacy/tham khảo
├── docker-compose.https.yml    # Compose HTTPS/Caddy legacy/tham khảo
├── Dockerfile               # Backend Dockerfile
├── pyproject.toml           # Python dependencies/package config
└── requirements.txt
```

Lưu ý: repo có một số file legacy còn tồn tại để tương thích hoặc do các phase trước. Khi sửa database/model, ưu tiên đọc `src/models/entities.py`, `src/db/session.py`, `migrations/`, không tự ý dựa vào model legacy trong `src/models/lead.py` hoặc `src/models/chat.py` nếu chưa kiểm tra import thực tế.

---

## 4. Backend map

### 4.1 Entry point

- `src/main.py`
  - Tạo FastAPI app.
  - Gắn CORS.
  - Include router chính:
    - `/api/v1/*`
    - `/agent/*`
  - Endpoint health:
    - `GET /health`
    - `GET /ready`
  - Lifespan:
    - tạo thư mục `data`
    - nếu `AUTO_CREATE_TABLES=true` thì init database
    - nếu `AUTO_SEED_CATALOG=true` thì seed catalog + admin

### 4.2 Config

- `src/config.py`
  - Đọc `.env`.
  - Chọn provider LLM qua:
    - `LLM_PROVIDER=openrouter|openai|custom`
    - `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `OPENROUTER_BASE_URL`
    - `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`
  - Validate staging/production:
    - `JWT_SECRET_KEY` phải đủ mạnh.
    - `DATABASE_URL` phải là PostgreSQL.
    - `AUTO_CREATE_TABLES=false`.
    - production không được dùng CORS localhost.

### 4.3 Database/session

- `src/db/session.py`
  - Engine/session sync SQLAlchemy cho API hiện tại.
- `src/database.py`
  - Có phần async/legacy. Kiểm tra import trước khi sửa.
- `migrations/versions/`
  - `20260620_01_initial_schema.py`
  - `20260622_02_auth_and_lead_workflow.py`
  - `20260627_03_customer_accounts_sessions.py`

### 4.4 Model chính hiện tại

Nguồn model chính: `src/models/entities.py`

Các bảng chính:

- `subdivisions`
- `apartment_specs`
- `amenities`
- `sales_policies`
- `users`
- `customer_accounts`
- `leads`
- `lead_notes`
- `conversations`
- `messages`
- `fallback_rules`

Quan hệ nghiệp vụ quan trọng:

```text
CustomerAccount.id
  └── Lead.customer_account_id
        └── Conversation.lead_id hoặc Conversation.customer_account_id
              └── Message.conversation_id
```

Model legacy cần cẩn trọng:

- `src/models/lead.py`
- `src/models/chat.py`
- `src/models/property.py`

Các file này dùng `src.database.Base` và có schema cũ. Không nên thêm logic mới vào đây nếu hệ thống hiện tại đang import `src.models.entities`.

### 4.5 API routes

Router tập trung:

- `src/api/routes.py`
  - Include:
    - `catalog_router`
    - `leads_router`
    - `auth_router`
    - `customer_auth_router`
    - `admin_router`
    - `conversations_router`
  - Có endpoint FE legacy:
    - `GET /api/v1/subdivisions`
    - `GET /api/v1/subdivisions/{slug}`
    - `POST /api/v1/contact`
    - `POST /api/v1/chat`
    - `GET /api/v1/status`

Auth/admin/customer:

- `src/api/auth.py`
  - Admin/sale login.
- `src/api/customer_auth.py`
  - Customer register/login/me.
  - Khi register: tạo `CustomerAccount`, sau đó `_link_or_create_registered_lead`.
- `src/api/dependencies.py`
  - JWT auth dependencies.
- `src/api/admin.py`
  - CRM admin:
    - `GET /api/v1/admin/dashboard`
    - `GET /api/v1/admin/leads`
    - `GET /api/v1/admin/leads/{lead_id}`
    - `PATCH /api/v1/admin/leads/{lead_id}`
    - `GET /api/v1/admin/leads/{lead_id}/conversations`
    - fallback rules CRUD
    - conversations list/detail
    - users CRUD
  - Sale scope:
    - sale chỉ thấy lead được assign.
    - admin thấy toàn bộ.

AI/chat:

- `src/api/agent_routes.py`
  - `POST /agent/chat`
  - `POST /agent/recommend`
  - `POST /agent/lead-score`
  - Khách vãng lai:
    - rate limit 5 tin/60 giây phía backend.
    - không lưu full conversation vào DB.
    - nếu phát hiện số điện thoại thì tạo/cập nhật Lead.
  - Khách đăng nhập:
    - lưu Conversation/Message.
    - liên kết với CustomerAccount/Lead.
    - dùng fallback rule trước khi gọi AI nếu match keyword.

Lead submit:

- `src/api/leads.py`
- `src/api/lead_routes.py`

Catalog/zone:

- `src/api/catalog.py`
- `src/api/zone_routes.py`

---

## 5. AI Agent map

Entry:

- `src/agents/graph.py`

Flow:

```text
intent_node
  ├── nếu greeting/out_of_scope/handover hoặc trigger_handover -> llm_node
  └── còn lại -> rag_node -> llm_node
```

Nodes:

- `src/agents/nodes/intent_node.py`
  - Phân loại intent.
  - Detect prompt injection.
  - Detect handover.
  - Handover hiện đã được siết lại để tránh trigger quá sớm.
- `src/agents/nodes/rag_node.py`
  - Tìm context/phân khu phù hợp.
  - Cập nhật 2026-06-30: với intent tư vấn thông thường (`consult`, `zone_match`, `price_query`), nếu có project/zone context đủ dùng thì không đánh dấu `insufficient_context` quá sớm. Mục tiêu là tránh chat trả lời máy móc “không đủ nguồn” cho câu hỏi như “2PN khu nào hợp lý?”.
- `src/agents/nodes/llm_node.py`
  - Sinh câu trả lời cuối.
  - Nếu handover thì trả câu hướng khách để lại thông tin/gặp sales.
  - Cập nhật 2026-06-30: `citation_verifier` chỉ được quyền thay câu trả lời bằng fallback khi câu hỏi/câu trả lời thuộc nhóm nhạy cảm cần nguồn chặt: giá chốt, quỹ căn, mã căn, đặt cọc, pháp lý, chính sách/ưu đãi/lãi suất. Với câu tư vấn thông thường, nếu verifier báo thiếu citation thì vẫn giữ câu trả lời và set `status=ok`.
  - Nếu provider LLM lỗi nhưng RAG đã có `recommended_zones` hoặc `zone_context`, hệ thống trả fallback tư vấn từ zone context thay vì trả “không đủ nguồn”.
  - Khi sinh chunk giả từ `recommended_zones`, citation token dùng dạng `C1`, `C2` để tương thích `src/services/citation_verifier.py`.
  - Cập nhật 2026-07-01: để tránh AI trả lời nối nhiều câu hỏi cũ, `agent_routes.py` chỉ truyền câu hỏi user mới nhất vào `messages`; lịch sử DB được truyền riêng qua `profile_messages` để `intent_node` chỉ dùng cho extract nhu cầu. `llm_node.py` cũng chỉ gửi HumanMessage mới nhất vào provider LLM.

State:

- `src/agents/state.py`

Services liên quan:

- `src/services/llm.py`
  - Gọi OpenRouter/OpenAI-compatible endpoint.
- `src/services/retrieval.py`
- `src/services/knowledge_retriever.py`
- `src/services/embeddings.py`
- `src/services/recommender.py`
- `src/services/lead_scorer.py`
- `src/services/citation_verifier.py`
  - Không phải LLM. Đây là lớp kiểm tra deterministic sau khi LLM trả lời: xóa link/citation giả, render `[C1]` thành link tin cậy, và cảnh báo/chặn nếu câu trả lời có dữ kiện nhạy cảm nhưng thiếu nguồn phù hợp.

Data cho AI/RAG:

- `cleaned_data/cleaned_apartment_zones.json`
- `cleaned_data/cleaned_apartment_zones.csv`
- `cleaned_data/ai_knowledge_chunks.json`

Lưu ý hiện trạng embedding/vector:

- Code có service embeddings/retrieval và config pgvector/RAG.
- Cần kiểm tra kỹ `RAG_PROVIDER`, migrations và runtime DB trước khi kết luận production đang dùng pgvector thật hay fallback legacy.
- Không giả định Supabase vector đang hoạt động nếu chưa kiểm tra env và bảng/vector extension thực tế.

---

## 6. Frontend map

Frontend root: `FE/`

### 6.1 App routes chính

Public/client:

- `FE/src/app/page.tsx`
- `FE/src/app/chung-cu/page.tsx`
- `FE/src/app/phan-khu/page.tsx`
- `FE/src/app/phan-khu/[slug]/page.tsx`
- Các trang phân khu static:
  - `masteri-lakeside`
  - `masteri-waterfront`
  - `the-bayfront`
  - `the-beverly`
  - `the-london`
  - `the-ocean-view`
  - `the-palma`
  - `the-paris`
  - `the-pavilion`
  - `the-sapphire`
  - `the-senique-1`
  - `the-senique-2`
  - `the-senique-hanoi`
  - `the-zenpark`
  - `the-zurich`
  - `toa-s2-17-the-s-vista`
- `FE/src/app/lien-he/page.tsx`
- `FE/src/app/dang-ky/page.tsx`
- `FE/src/app/dang-nhap/page.tsx`
- `FE/src/app/login/page.tsx`
- `FE/src/app/register/page.tsx`

Admin:

- `FE/src/app/admin/login/page.tsx`
- `FE/src/app/admin/(dashboard)/layout.tsx`
- `FE/src/app/admin/(dashboard)/page.tsx`
- `FE/src/app/admin/(dashboard)/leads/page.tsx`
- `FE/src/app/admin/(dashboard)/leads/[id]/page.tsx`
- `FE/src/app/admin/(dashboard)/fallback-rules/page.tsx`
- `FE/src/app/admin/(dashboard)/users/page.tsx`
- `FE/src/app/admin/(dashboard)/conversations/page.tsx`

Lưu ý: UI admin hiện đã chuyển hướng nghiệp vụ sang `Khách hàng -> chi tiết khách -> danh sách phiên chat -> tin nhắn`. Menu “Hội thoại” riêng từng được yêu cầu ẩn; nếu còn file page thì cần kiểm tra navigation trong `FE/src/components/admin-shell.tsx`, không nhất thiết xóa file.

### 6.2 Component chính

- `FE/src/components/chat-widget.tsx`
  - Chat AI.
  - Lưu `session_id`/messages localStorage.
  - Guest 5 messages.
  - Login customer gửi token.
  - Logout tạo session mới trên browser.
- `FE/src/components/contact-form.tsx`
- `FE/src/components/header.tsx`
- `FE/src/components/footer.tsx`
- `FE/src/components/public-layout.tsx`
- `FE/src/components/subdivision-grid.tsx`
- `FE/src/components/admin-shell.tsx`
- `FE/src/components/public/static-vinhomes-page.tsx`

### 6.3 Data/UI static

- `FE/src/data/public-vinhomes.ts`
- `FE/src/data/homepage.ts`
- `FE/src/data/apartments.ts`
- `FE/src/data/navbar.ts`

Static HTML nguồn:

- `raw_pages/*.html`

Ảnh local:

- `FE/public/media_files/project/...`
- `FE/public/media_files/subzone/...`

Mentor yêu cầu UI public giống `vinhomeoceanpark.com.vn`; các ảnh đã được tải local vào `public`. Khi deploy online, ảnh trong `FE/public` sẽ được bundle/serve cùng Next.js nếu Dockerfile copy `public`.

### 6.4 Styling

- `FE/src/app/public-vinhomes.css`
  - UI public theo style Vinhomes.
- `FE/src/app/admin.css`
  - UI admin.
  - Gần đây đã chỉnh font/màu admin đồng bộ hơn với client để tránh lỗi font tiếng Việt.
- `FE/src/app/public-styles.tsx`
- `FE/src/app/layout.tsx`

---

## 7. Deploy/DevOps map

### 7.1 Compose files

- `docker-compose.yml`
  - Local development/build từ source.
  - Dùng khi chạy:
    - `docker compose up -d --build`
- `docker-compose.registry.yml`
  - Dùng trên VPS.
  - Pull image từ GHCR theo biến:
    - `BACKEND_IMAGE`
    - `FRONTEND_IMAGE`
  - Map port bằng:
    - `BACKEND_PORT`
    - `FRONTEND_PORT`
- `docker-compose.deploy.yml`
  - File deploy legacy/tham khảo. Cần kiểm tra trước khi dùng.
- `docker-compose.https.yml`
  - File HTTPS/Caddy legacy/tham khảo. Hiện hướng triển khai thực tế đang dùng Nginx host + Certbot.

### 7.2 Scripts deploy

- `scripts/deploy/staging_deploy.sh`
- `scripts/deploy/staging_https_deploy.sh`
- `scripts/deploy/production_deploy.sh`
- `scripts/deploy/check_vps_prerequisites.sh`
- `scripts/deploy/backup_postgres.sh`
- `scripts/deploy/restore_postgres.sh`
- `scripts/deploy/rollback_images.sh`

Staging thực tế:

```text
VPS path: /opt/ocean-park-advisor
Git branch: dev
Project name: ocean-park-staging
Frontend port: 3000
Backend port: 8000
Domain: https://staging.c2-app-005.quangtm.site
Image tag thường dùng: :dev
```

Production thực tế:

```text
VPS path: /opt/ocean-park-production
Git branch: main
Project name: ocean-park-production
Frontend port: 3001
Backend port: 8001
Domain: https://c2-app-005.quangtm.site
Image tag đang muốn dùng thẳng: :main
```

Nginx host reverse proxy:

- Domain public trỏ về frontend container.
- `/api/v1/*`, `/agent/*`, `/docs`, `/openapi.json`, `/health`, `/ready` cần proxy về backend.
- Không gọi `https://domain:8000` hoặc `https://domain:8001` từ browser; browser phải gọi cùng domain qua Nginx path:
  - `https://domain/api/v1`
  - `https://domain/agent/chat`

### 7.3 GitHub Actions/Registry

Workflow nằm trong `.github/workflows/`.

Các job chính đã từng dùng:

- Backend lint/tests.
- Frontend build.
- Docker build and publish.

Do billing GitHub-hosted runner từng lỗi, dự án đã chuyển một số job sang self-hosted runner. Docker build/publish đã pass sau khi chỉnh label runner phù hợp.

GHCR packages nằm trong GitHub organization/repo Packages:

- `c2-app-005-backend`
- `c2-app-005-frontend`

---

## 8. Environment map

File mẫu:

- `.env.example`
- `.env.staging.example`
- `.env.production.example`

Biến quan trọng:

```env
APP_ENV=development|staging|production
DATABASE_URL=postgresql+psycopg://...
AUTO_CREATE_TABLES=false
AUTO_SEED_CATALOG=true
JWT_SECRET_KEY=...
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
CORS_ORIGINS=https://...
NEXT_PUBLIC_API_URL=https://.../api/v1
BACKEND_IMAGE=ghcr.io/.../c2-app-005-backend:dev|main
FRONTEND_IMAGE=ghcr.io/.../c2-app-005-frontend:dev|main
FRONTEND_PORT=3000|3001
BACKEND_PORT=8000|8001
LLM_PROVIDER=openrouter|openai
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=...
OPENROUTER_SITE_URL=https://...
```

Cảnh báo:

- Không commit `.env` thật.
- Không để `JWT_SECRET_KEY` dưới 32 ký tự ở staging/production.
- Nếu frontend gọi nhầm `localhost:8000` trên VPS/domain, sẽ lỗi CORS/private network.
- Nếu HTTPS domain gọi kèm `:8000`, thường lỗi SSL protocol vì port backend không có TLS.

---

## 9. Test map

Backend:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Frontend:

```powershell
cd FE
npm run build
```

Docker local:

```powershell
docker compose up -d --build
docker compose ps
```

Health local:

```powershell
curl http://localhost:8000/ready
curl http://localhost:3000
```

VPS staging:

```bash
cd /opt/ocean-park-advisor
git checkout dev
git pull origin dev
bash scripts/deploy/staging_deploy.sh
curl http://127.0.0.1:8000/ready
curl -I http://127.0.0.1:3000
```

VPS production, dùng thẳng main:

```bash
cd /opt/ocean-park-production
git checkout main
git pull origin main
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml pull
docker compose --env-file .env -p ocean-park-production -f docker-compose.registry.yml up -d
curl http://127.0.0.1:8001/ready
curl -I http://127.0.0.1:3001
```

---

## 10. Tiến độ và trạng thái hiện tại

Đã hoàn thành/chạy được:

- Backend FastAPI cơ bản.
- Frontend Next.js public pages.
- Giao diện public theo hướng giống vinhomeoceanpark.com.vn, dùng ảnh local trong `FE/public/media_files`.
- Customer register/login.
- Admin login.
- CRM Lead list.
- Lead detail page với danh sách phiên chat và messages.
- Admin customer list có filter nhanh:
  - `Tất cả`
  - `Đã đăng ký`
  - `Khách vãng lai`
  - filter trạng thái dùng chung với search/pagination.
- Cột `Nhu cầu` đã được bỏ khỏi bảng khách hàng; `summary`/AI summary là nguồn mô tả nhu cầu chính.
- Dashboard admin đã có analytics mở rộng:
  - lead mới theo thời gian;
  - khách đăng ký;
  - nguồn khách hàng;
  - trạng thái lead;
  - top sale được phân công;
  - số conversation/message;
  - conversion funnel.
- Font frontend đã được chuẩn hóa toàn dự án về `Roboto, Arial, Helvetica, sans-serif`; block chuẩn cuối nằm trong `FE/src/app/public-vinhomes.css`.
- Liên kết CustomerAccount -> Lead khi đăng ký.
- Chat AI với OpenRouter/OpenAI-compatible provider.
- Guest chat limit và không lưu full guest chat.
- Handover intent đã siết lại.
- Fallback rules có API/admin page.
- Staging deploy online HTTPS.
- Production deploy online HTTPS.
- Docker build/publish GHCR đã pass.
- Tài liệu deploy cuối:
  - `docs/reportsDevOps/final-staging-production-deployment-runbook-2026-06-29.md`
- Tài liệu audit customer/admin:
  - `docs/reportsDevOps/project-structure-admin-customer-registration-audit-2026-06-29.md`
- Tài liệu fix customer-lead-admin-chat:
  - `docs/reportsDevOps/customer-lead-ai-admin-flow-fix-report-2026-06-30.md`

Đã từng gặp và đã xử lý/ghi nhớ:

- Docker backend unhealthy do role Postgres không tồn tại.
- Alembic permission denied trong container.
- JWT secret staging không đủ 32 ký tự.
- TLS handshake timeout khi pull `postgres:16-alpine`.
- Frontend `crypto.randomUUID` lỗi khi chạy HTTP/IP không secure context.
- CORS do frontend build trỏ nhầm `localhost:8000` trên VPS.
- HTTPS bị lỗi khi gọi `https://domain:8000`; phải proxy qua Nginx path.
- GitHub Actions billing/self-hosted runner.
- Docker build skipped do event/condition.
- React hydration/minified error trên production cần test kỹ route cụ thể.
- Next dynamic route params ở `/admin/leads/[id]` cần dùng `use(params)` nếu params là Promise.

Đang/ cần kiểm tra tiếp:

- Admin lead detail sau các chỉnh sửa gần nhất:
  - Khi click một khách hàng, phải hiện info + conversation list + messages.
  - Profile detail không hiển thị email/source; chỉ hiển thị loại khách: `Khách vãng lai` hoặc `Khách đăng kí`.
- Kiểm tra sale permission:
  - sale chỉ thấy khách được assign.
  - admin thấy toàn bộ.
- Kiểm tra production có đồng nhất staging sau mỗi merge main.
- Kiểm tra thực tế RAG/vector provider đang dùng legacy hay pgvector.

---

## 11. Những file report quan trọng nên đọc trước khi sửa lớn

DevOps/deploy:

- `docs/reportsDevOps/final-staging-production-deployment-runbook-2026-06-29.md`
- `docs/reportsDevOps/vps-online-domain-deployment-summary-2026-06-29.md`
- `docs/reportsDevOps/production-deployment-plan-after-staging-2026-06-29.md`
- `docs/reportsDevOps/version-0.9.0-automated-staging-cd-plan.md`
- `docs/reportsDevOps/ghcr-publish-success-next-steps.md`

AI/Data:

- `docs/ai_agent_data_agent_audit_2026-06-27.md`
- `docs/report_AI/rag_test_report.md`
- `docs/report_AI/rag_pipeline_compact.md`
- `docs/report_AI/PHASE_2_PGVECTOR_RETRIEVAL_NOTES.md`
- `docs/report_AI/LEAD_FILTERING_SALES_TICKET_CRM_SPEC.md`

Customer/Admin/CRM:

- `docs/reportsDevOps/project-structure-admin-customer-registration-audit-2026-06-29.md`
- `docs/reportsDevOps/customer-lead-ai-admin-flow-fix-report-2026-06-30.md`

Architecture:

- `ARCHITECTURE.md`
- `docs/architecture_diagram.md`

---

## 12. Quy tắc làm việc cho AI Agent kế tiếp

Trước khi sửa:

1. Đọc file này.
2. Đọc file liên quan trực tiếp tới task.
3. Chạy search bằng `rg`, không đoán theo tên file.
4. Kiểm tra import thực tế để tránh sửa nhầm file legacy.
5. Không sửa `.env` thật hoặc commit secret.
6. Nếu sửa DB schema:
   - sửa `src/models/entities.py`
   - tạo Alembic migration
   - cập nhật tests
   - ghi report
7. Nếu sửa API:
   - cập nhật schema trong `src/models/schemas.py`
   - kiểm tra FE đang gọi endpoint nào.
8. Nếu sửa FE route dynamic Next 16:
   - chú ý `params` có thể là Promise trong client component.
9. Nếu sửa deploy:
   - phân biệt local `docker-compose.yml` và VPS `docker-compose.registry.yml`.
   - staging dùng `dev`, production dùng `main`.
10. Sau mỗi thay đổi quan trọng:
    - chạy pytest backend.
    - chạy `npm run build`.
    - cập nhật report nếu user yêu cầu theo version.

---

## 13. Quick start cho AI Agent trong phiên mới

Nếu cần nắm dự án trong 5 phút, đọc theo thứ tự:

1. `docs/PROJECT_MAP_FOR_AI_AGENTS.md`
2. `src/main.py`
3. `src/config.py`
4. `src/models/entities.py`
5. `src/api/agent_routes.py`
6. `src/api/admin.py`
7. `src/api/customer_auth.py`
8. `FE/src/components/chat-widget.tsx`
9. `FE/src/app/admin/(dashboard)/leads/page.tsx`
10. `FE/src/app/admin/(dashboard)/leads/[id]/page.tsx`
11. `docker-compose.registry.yml`
12. `docs/reportsDevOps/final-staging-production-deployment-runbook-2026-06-29.md`

Nếu đang debug production/staging:

1. kiểm tra `.env` trên VPS.
2. kiểm tra Nginx route.
3. kiểm tra `docker ps`.
4. kiểm tra backend `/ready`.
5. kiểm tra frontend `NEXT_PUBLIC_API_URL` đã build đúng domain chưa.
6. kiểm tra image tag đang chạy là `dev` hay `main`.

---

## 14. Ghi chú cuối

Repo này đã trải qua nhiều phase nhanh: UI static, AI Agent, CRM Admin, customer auth, staging/production deploy. Vì vậy có một số dấu tích legacy còn lại. Khi có mâu thuẫn giữa tài liệu cũ và code hiện tại, ưu tiên:

```text
source code đang được import/chạy
> migrations
> tests hiện tại
> report mới nhất
> report cũ/README cũ
```

File này nên được cập nhật sau mỗi thay đổi kiến trúc lớn, đặc biệt là:

- thay đổi schema database;
- đổi luồng CustomerAccount/Lead/Conversation;
- đổi cách deploy staging/production;
- đổi provider AI/RAG/vector DB;
- đổi cấu trúc UI public/admin.
# Update 2026-07-01: AI advisory/RAG stabilization v0.9.6

Mục tiêu thay đổi:

- Chat không được trả lời fallback máy móc kiểu “Thông tin này hiện chưa...” khi dữ liệu dự án vẫn có đủ thông tin tư vấn tổng quan.
- Với câu hỏi tư vấn có ngân sách, gia đình, mục đích mua, hệ thống phải trả lời rõ ràng, có cấu trúc, không bịa giá chốt/quỹ căn.
- Kết quả phải ổn định dù retrieval đang chạy bằng `legacy` JSON/context hoặc sau này chuyển sang `pgvector`.

Các file chính đã thay đổi:

- `src/agents/nodes/intent_node.py`
  - Extract profile từ `profile_messages` để lưu nhu cầu dài hạn nhưng LLM chỉ trả lời câu hỏi mới nhất.
  - Fix lỗi “gia đình 4 người, có 2 con” bị hiểu thành `family_size=2`; hiện lấy số lớn nhất.
  - Nhận diện `school_need` qua các cụm như `con nhỏ`, `cấp 2`, `trường`, `Vinschool`.
  - Nếu gia đình từ 3 người trở lên và chưa có purpose, mặc định tư vấn theo hướng `ở thật`.

- `src/agents/nodes/rag_node.py`
  - Thêm chọn loại căn ứng viên theo profile: gia đình 4 người ưu tiên `2PN+1`, `3PN`, `2PN`.
  - Tính khoảng giá theo loại căn phù hợp thay vì lấy min tổng toàn phân khu, tránh gợi ý sai vì Studio/1PN rẻ.
  - Cộng điểm cho phân khu có căn phù hợp gia đình và tiện ích giáo dục.
  - Cho trạng thái `ok` nếu có project context đủ dùng cho tư vấn tổng quan, không phụ thuộc tuyệt đối vào vector chunks.

- `src/agents/nodes/llm_node.py`
  - Thêm deterministic advisory response: nếu RAG đã chọn được phân khu + profile đủ rõ, backend tự dựng câu trả lời tư vấn an toàn.
  - Lớp này tránh hallucination và tránh citation verifier chặn nhầm câu tư vấn bình thường.
  - Citation strict chỉ nên áp dụng mạnh với giá chốt, quỹ căn, mã căn, đặt cọc, pháp lý, chính sách, ưu đãi.
  - LLM chỉ nhận latest user message, không nhận lại toàn bộ lịch sử để tránh trả lời nối toàn bộ câu hỏi cũ.

- `tests/test_agents/test_customer_advisory_scenarios.py`
  - Test tình huống khách hàng: gia đình 4 người, 2 con học cấp 2, ngân sách 4 tỷ.
  - Kỳ vọng: profile đúng, có phân khu hợp lệ, không fallback, không bịa các phân khu ngoài dữ liệu như The Venice/The Milan/The Manhattan.

- `docs/report_AI/AI_RAG_REARCHITECTURE_PLAN_2026_07_01.md`
  - Bản thiết kế lại AI/RAG contract để dùng được cả legacy context và vectorDB.

Lệnh test đã chạy:

```powershell
.\.venv\Scripts\ruff.exe check src\agents\state.py src\agents\nodes\intent_node.py src\agents\nodes\rag_node.py src\agents\nodes\llm_node.py tests\test_agents\test_customer_advisory_scenarios.py tests\test_agents\test_llm_fallback_policy.py --output-format concise
.\.venv\Scripts\python.exe -m pytest tests\test_agents\test_customer_advisory_scenarios.py tests\test_agents\test_llm_fallback_policy.py tests\test_agents\test_rag_eval_regressions.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_agents\test_rag_scenario2.py -q
```

Kết quả:

- Ruff: passed.
- Targeted AI/RAG tests: `11 passed`.
- RAG scenario2 regression: `18 passed`.

---

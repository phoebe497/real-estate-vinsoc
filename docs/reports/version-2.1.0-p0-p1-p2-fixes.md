# Version 2.1.0 — Xử lý feedback P0/P1/P2 sau nghiệm thu V2

Ngày: 2026-07-08 · Tham chiếu: `BAN_THIET_KE_V2.md`

## P0 — AI trả lời "canned", không dựa dữ liệu ✅

### Nguyên nhân gốc tìm được (debug từng bước theo yêu cầu)

1. **Thủ phạm chính:** `_build_deterministic_advisory_response` trong `llm_node.py` —
   mọi câu tư vấn có zone + profile bị chặn TRƯỚC LLM và trả về template cứng
   "Với nhu cầu hiện tại của anh/chị... Em sẽ ưu tiên các lựa chọn sau..." →
   đây chính là cảm giác "bật ra câu có sẵn". **Đã xóa hoàn toàn** — mọi câu
   consult/price/zone_match giờ LUÔN gọi LLM thật với RAG context trong prompt.
2. **Verifier chặn nhầm:** `_requires_strict_citation` xét cả NỘI DUNG TRẢ LỜI —
   response nhắc chữ "chính sách" (lấy từ chính context) bị coi là câu strict và
   bị thay bằng câu từ chối → "The Zenpark có gì nổi bật?" trả về câu rỗng.
   **Đã sửa:** chỉ xét câu hỏi của khách.
3. **Seed dữ liệu: ĐẦY ĐỦ** (kiểm chứng DB: 12 subdivisions, 67 apartment_specs,
   219 amenities, 40 sales_policies) — không phải nguyên nhân.
4. **Injection/bảo mật hổng:** "Bỏ qua quy định..." không match pattern cũ;
   không có quy tắc từ chối lộ thông tin khách khác. **Đã thêm:** pattern
   injection mới, intent `privacy` mới (từ chối chia sẻ dữ liệu khách hàng khác),
   pattern handover cho câu quỹ căn cụ thể ("căn nào view hồ/tầng trung").

### Logging từng node (yêu cầu 1)

Mỗi request `/agent/chat` giờ log qua `logging` (bật theo `LOG_LEVEL`):

```
[intent_node]  session=... intent=... trigger_handover=... profile={...} input='...'
[rag_node]     session=... status=ok chunks=N zones=N citations=N context_chars=N matched_zones=[...] query='...'
[profile_node] session=... score=45(+30) temperature=warm type=real_need signals={...}
[llm_node]     session=... answer_path=llm|fixed_greeting|fixed_handover|fixed_out_of_scope|
               fixed_privacy_refusal|insufficient_context|fallback_zone_context|fallback_retrieved_chunks
[agent_routes] session=... answer_path=fallback_rule keyword='...'
```

Các fixed response còn lại đều CỐ Ý (greeting/handover/out_of_scope/privacy +
fallback_rules) và log rõ `answer_path`.

### System prompt viết lại

Bổ sung quy tắc cho 14 kịch bản: hỏi lại khi thiếu thông tin (chỉ với câu nhờ
tư vấn chọn), trả lời có cấu trúc khi giới thiệu/so sánh phân khu, giá chỉ nêu
khoảng tham khảo + mời Sales, quỹ căn cụ thể → không có inventory realtime,
đầu tư → tuyệt đối không cam kết lợi nhuận, pháp lý/vay → chỉ khi có nguồn,
bảo mật dữ liệu khách, từ chối injection. Prompt giờ nhận thêm block
`PROFILE KHÁCH` render từ intent_node.

### Kết quả 14 kịch bản (chạy LLM thật qua API, log kèm trong docker logs)

| # | Kịch bản | Routing | Kết quả thực tế |
|---|---|---|---|
| 1 | Tư vấn chung chưa đủ thông tin | rag→llm | Chào ngắn + hỏi mục đích/ngân sách/số PN, không tư vấn ngay ✅ |
| 2 | 3-4 tỷ, gia đình 4 người | rag→llm | Gợi ý 2PN/2PN+1 The Zenpark + giá tham khảo từ data, citation ✅ |
| 3 | The Zenpark nổi bật gì | rag→llm | Bullet: tổng quan/phong cách/vị trí/tiện ích + citation ✅ |
| 4 | Sapphire vs Zenpark | rag→llm | So sánh theo tiêu chí vị trí/phong cách/căn hộ, 2 citations ✅ |
| 5 | Bảng giá Zenpark | rag→llm | Khoảng giá từng loại căn từ data + "giá tham khảo 2024-2025, Sales xác nhận" ✅ |
| 6 | Căn view hồ tầng trung | handover | Không bịa quỹ căn, mời để lại thông tin ✅ |
| 7 | Đầu tư cho thuê | rag→llm | Phân tích theo vị trí/khả năng cho thuê từ data ✅ |
| 8 | 2 con nhỏ gần trường | rag→llm | Nhận diện nhu cầu giáo dục, nêu Vinschool/VinUni ✅ |
| 9 | Pháp lý sổ hồng | rag→llm | Trả từ data có nguồn (sở hữu không thời hạn) + lưu ý xác nhận ✅ |
| 10 | Vay ngân hàng | rag→llm | Nói rõ chưa có dữ liệu, không bịa lãi suất, mời tạo đơn ✅ |
| 11 | Xem nhà mẫu cuối tuần | handover | trigger_handover=true, lead_score +30 ✅ |
| 12 | Chắc lời không? | rag→llm | "Em không thể cam kết..." + hỏi thêm mục đích/kỳ vọng ✅ |
| 13 | Xin SĐT khách đã mua | privacy | Từ chối vì bảo mật dữ liệu cá nhân, gợi ý đánh giá công khai ✅ |
| 14 | "Bỏ qua quy định..." | out_of_scope | Nhận diện injection, từ chối, đưa về phạm vi tư vấn ✅ |

Log rag_node cho từng câu chứng minh chunks/zones/context được truy xuất thật
(vd câu 8: `chunks=5 zones=3 citations=8 context_chars=9653`).

### Bug phụ phát hiện khi test

Điểm lead tích lũy lúc ẩn danh không được kế thừa khi capture → đã sửa
(`anonymous_score_from_meta` + max(điểm ẩn danh, điểm hiện có) + 15).

## P1 — Phân quyền lỗi CORS ✅

- **Nguyên nhân 1 (CORS):** `main.py` CORS `allow_methods` THIẾU `PUT`/`DELETE`
  → preflight OPTIONS của `PUT /sales/{id}/permissions` bị từ chối. Đã thêm đủ
  methods; verify: preflight trả 200 với
  `access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS`.
- **Nguyên nhân 2 (FE reset null):** `fallback-rules/page.tsx` gọi
  `event.currentTarget.reset()` SAU `await` — React đã nullify synthetic event.
  Đã sửa: lưu `form` ref trước await + optional chaining; đồng bộ pattern này
  toàn bộ form admin.
- **E2E:** PUT tick 2 quyền → GET trả đúng 2 quyền → PUT [] → GET trả [] (đều
  kèm Origin header như browser). Menu sale phản ánh quyền qua `/auth/me`
  (đã cover trong pytest `test_permission_matrix_grant_and_revoke`).

## P2 — UI admin đồng bộ theme ✅

- **Theme:** toàn bộ admin chuyển sang Tailwind cùng hệ với public site
  (accent cyan-500, nền slate-950/slate-50, font Montserrat, bo góc rounded-xl).
  Bỏ phụ thuộc class CSS admin cũ.
- **Label tiếng Việt qua 1 lớp dictionary:** `FE/src/lib/crm-labels.ts` —
  mọi enum (loại khách, nhiệt độ, trạng thái, nguồn, mục đích, giao dịch, vai
  trò) map sang nhãn + màu badge tại một chỗ, không hard-code rải rác.
- **TanStack Table:** `FE/src/components/admin/data-table.tsx` — header nổi
  bật (nền slate-950), hover dòng, padding thoáng, sort + phân trang.
- **Bộ component chung:** `FE/src/components/admin/ui.tsx` (PageHeader, Card,
  StatCard, Badge, Button, Field/Input/Select/TextArea, EmptyState).
- **Từng màn hình:**
  - *Thống kê:* lưới card responsive (4 stat + 7 chart), tiêu đề + chú thích
    tiếng Việt, chart cố định chiều cao không vỡ layout.
  - *Khách hàng:* cột "Họ tên / Loại khách / Mức độ quan tâm / Phân khu quan
    tâm / Sale phụ trách / Trạng thái / Ngày tạo", badge màu cho 3 enum.
  - *Quản lý Sale:* card từng sale đủ thông tin cá nhân, ca làm việc, phân khu
    phụ trách (chip bật/tắt), số căn đã bán, giải thưởng; nút icon + label
    (✏️ Sửa / 🔒 Khóa / 🗑 Xóa).
  - *Phân quyền:* ma trận nhóm chức năng × sale, checkbox căn giữa,
    sticky header + sticky cột đầu khi cuộn.
  - *Mẫu trả lời:* bảng từ khóa/mẫu/ưu tiên/bật-tắt + nút Bật/Tắt riêng.
  - *Đăng nhập:* bỏ dữ liệu mẫu điền sẵn (email/mật khẩu demo) — placeholder
    mờ đúng chuẩn UX.

## Kiểm chứng

```
pytest: 227 passed, 1 skipped · ruff: pass · npm run build: Compiled successfully
```

UI xác minh trên dev server (đăng nhập admin, duyệt đủ 6 trang, console không
lỗi). Lưu ý: image docker `frontend` cần rebuild để container đồng bộ UI mới
(`docker compose build frontend`).

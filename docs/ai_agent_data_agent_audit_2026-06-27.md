# Báo cáo rà soát data và hệ thống AI Agent

Ngày lập: 2026-06-27

## 1. Tóm tắt kết luận

Hiện tượng “AI trả lời không đúng” không đến từ một lỗi đơn lẻ của model, mà chủ yếu đến từ việc pipeline RAG chưa thật sự sử dụng đầy đủ bộ `cleaned_data` mới.

Kết luận ngắn gọn:

- Bộ `cleaned_data` mới đã có nhiều thông tin tốt hơn trước: 12 phân khu, 72 knowledge chunks, mỗi phân khu có overview, location, apartment specs, amenities và sales policies.
- Tuy nhiên `src.services.vinhomes_data` hiện chỉ map một phần rất nhỏ dữ liệu cleaned vào format cũ của Agent.
- RAG hiện vẫn cần các field cũ như `unit_types`, `total_price_range_billion`, `design_style`, `matching_rules`, `project`, nhưng bộ cleaned mới lại dùng schema khác: `apartment_specs`, `internal_amenities`, `external_amenities`, `sales_policies`, `handover_standard`, `legal_status`.
- Vì field không khớp, context đưa vào LLM đang bị thiếu giá, thiếu loại căn, thiếu tiện ích, thiếu chính sách và thiếu project info.
- AI Agent hiện mới ở mức “rule-based RAG rất đơn giản”, chưa có semantic retrieval/vector search, chưa dùng `ai_knowledge_chunks.json`, chưa có evaluation dataset để đo trả lời đúng/sai.

Đây là nguyên nhân chính khiến AI có thể trả lời sai, trả lời chung chung hoặc tự suy đoán.

## 2. Bộ data hiện tại

### 2.1. File được phát hiện

Trong thư mục `cleaned_data` hiện có:

| File | Vai trò | Ghi chú |
|---|---|---|
| `cleaned_apartment_zones.json` | Catalog chính theo phân khu | Đang được seed vào database và được Agent fallback đọc |
| `cleaned_apartment_zones.csv` | Bản CSV tương ứng | Phù hợp review thủ công |
| `ai_knowledge_chunks.json` | Knowledge chunks cho AI/RAG | Hiện chưa được Agent sử dụng |

Không thấy file `data/vinhomes_real.json`. Vì vậy hàm `load_seed_data()` fallback sang `cleaned_apartment_zones.json`.

### 2.2. Coverage của `cleaned_apartment_zones.json`

Data có 12 phân khu:

1. `the-sapphire`
2. `the-zenpark`
3. `the-pavilion`
4. `the-bayfront`
5. `the-zurich`
6. `the-beverly`
7. `the-london`
8. `the-paris`
9. `the-palma`
10. `masteri-waterfront`
11. `masteri-lakeside`
12. `the-senique-hanoi`

Các field chính trong cleaned data:

- `name`
- `developer`
- `scale`
- `introduction`
- `location`
- `sales_policies`
- `apartment_specs`
- `handover_standard`
- `legal_status`
- `internal_amenities`
- `external_amenities`
- `handover_status`

Đây là schema hợp lý hơn hướng cũ vì bám theo mô hình `subdivisions`.

### 2.3. Coverage theo phân khu

| Phân khu | Specs | Giá chưa cập nhật | Giá đã bán hết | Internal amenities | External amenities | Sales policies |
|---|---:|---:|---:|---:|---:|---:|
| The Sapphire | 7 | 3 | 0 | 7 | 8 | 7 |
| The Zenpark | 7 | 0 | 1 | 7 | 8 | 10 |
| The Pavilion | 7 | 2 | 0 | 6 | 8 | 8 |
| Lumiere Orient Pearl / The Bayfront | 7 | 0 | 0 | 6 | 8 | 2 |
| The Zurich | 7 | 3 | 0 | 7 | 8 | 10 |
| The Beverly | 7 | 2 | 0 | 7 | 8 | 10 |
| The London | 7 | 2 | 0 | 6 | 8 | 5 |
| The Paris | 7 | 2 | 0 | 7 | 8 | 8 |
| The Palma | 7 | 0 | 0 | 6 | 8 | 1 |
| Masteri Waterfront | 7 | 2 | 0 | 7 | 8 | 10 |
| Masteri Lakeside | 7 | 2 | 0 | 6 | 8 | 8 |
| The Senique Hanoi | 7 | 7 | 0 | 7 | 8 | 10 |

Nhận xét:

- Coverage tổng thể tốt hơn trước: phân khu nào cũng có đủ 7 loại căn phổ biến.
- Tuy nhiên nhiều giá đang là “Chưa cập nhật”, đặc biệt The Senique Hanoi có 7/7 loại căn chưa có giá.
- Một số sales policy có dấu hiệu lẫn nội dung mô tả/bài viết marketing, không hoàn toàn là chính sách bán hàng.
- Một số tên/slug có thể gây lệch định danh, ví dụ `the-bayfront` nhưng `name` là `Lumiere Orient Pearl`.

### 2.4. Coverage của `ai_knowledge_chunks.json`

Có 72 chunks:

- 12 phân khu.
- Mỗi phân khu có 6 topic:
  - `overview`
  - `location`
  - `apartment_specs`
  - `internal_amenities`
  - `external_amenities`
  - `sales_policies`

Phân bố rất đều: mỗi phân khu có đúng 6 chunks.

Đây là cấu trúc phù hợp để làm RAG tốt hơn. Nhưng hiện tại Agent chưa dùng file này.

## 3. Hệ thống AI Agent hiện tại

### 3.1. Flow hiện tại

Agent hiện chạy theo LangGraph:

```text
intent_node -> rag_node -> llm_node
```

Route public:

```text
POST /agent/chat
```

Các node chính:

- `src/agents/nodes/intent_node.py`
- `src/agents/nodes/rag_node.py`
- `src/agents/nodes/llm_node.py`
- `src/services/vinhomes_data.py`
- `src/services/recommender.py`

### 3.2. Intent node

Điểm tốt:

- Có nhận diện greeting, handover, price query, zone match, out-of-scope.
- Có guardrail chống prompt injection cơ bản.
- Có extract budget, unit type, purpose từ lịch sử chat.

Vấn đề:

- Pattern tiếng Việt trong file đang hiển thị mojibake khi đọc bằng terminal, cần kiểm tra encoding nguồn thực tế trong editor. Nếu file thật bị mojibake, regex tiếng Việt sẽ không match đúng.
- Một số intent thực tế bị phân loại thành `consult` thay vì `price_query` hoặc `zone_match`.
- Extract budget phụ thuộc vào pattern “tỷ/triệu”; nếu input encoding lỗi hoặc người dùng viết “3 tỉ”, “3ty”, “3 tỷ đổ lại”, có thể không nhận.

### 3.3. RAG node

Đây là điểm yếu nhất hiện tại.

RAG hiện dùng:

```python
get_all_zones()
get_matching_rules()
format_zones_for_context()
```

Nhưng `get_all_zones()` đang nhận dữ liệu fallback từ cleaned data theo format rút gọn:

```python
{
  "slug": slug,
  "name": ...,
  "description": introduction,
  "handover_status": ...,
  "location_in_project": ...,
  "design_style": "",
  "total_price_range_billion": {}
}
```

Nghĩa là các field quan trọng bị bỏ mất:

- `apartment_specs`
- `unit_types`
- `price_min/price_max`
- `internal_amenities`
- `external_amenities`
- `sales_policies`
- `handover_standard`
- `legal_status`

Runtime kiểm tra thực tế cho thấy context đang bị build như sau:

```text
Giá tham khảo: ?-? tỷ
Dự án: None
Vị trí: None
Mô tả: None
Điểm nổi bật:
```

Với context như vậy, LLM không có đủ căn cứ để trả lời đúng.

### 3.4. LLM node

Điểm tốt:

- System prompt có guardrail khá rõ: chỉ trả lời dựa trên context, không tư vấn mã căn/quỹ căn, phải disclaimer giá.
- Có fallback khi thiếu API key.
- Có handover response riêng.

Vấn đề:

- Prompt yêu cầu “chỉ dùng context”, nhưng context lại thiếu dữ liệu. Khi context nghèo, model sẽ có xu hướng trả lời chung chung hoặc cố suy luận.
- LLM node chỉ đưa `HumanMessage` cho user messages, chưa đưa lại `AIMessage` từ các lượt trước nên multi-turn context bị yếu.
- Chưa có citation/source chunk trong response.
- Chưa có cơ chế “nếu context không chứa thông tin cụ thể thì từ chối trả lời phần đó” ở mức code. Hiện chỉ dựa vào prompt.

### 3.5. Recommender endpoint

Endpoint:

```text
POST /agent/recommend
```

Vấn đề tương tự RAG:

- `score_zone()` cần `total_price_range_billion`, `unit_types`, `matching_rules`.
- Cleaned data mới không expose các field này theo format mà recommender cần.
- Vì vậy scoring dễ rơi về default, top kết quả có thể chỉ là thứ tự dữ liệu ban đầu thay vì phù hợp thật.

## 4. Nguyên nhân AI trả lời sai

### Nguyên nhân 1: Data schema mới chưa được map vào schema Agent

Cleaned data mới dùng schema đúng hơn:

```text
apartment_specs -> unit type -> area/price
internal_amenities
external_amenities
sales_policies
```

Nhưng Agent vẫn kỳ vọng schema cũ:

```text
unit_types
total_price_range_billion
design_style
matching_rules
project
amenities
transport_routes
```

Kết quả là Agent “có file mới” nhưng không đọc được phần quan trọng nhất.

### Nguyên nhân 2: `ai_knowledge_chunks.json` chưa được dùng

File chunks đã được chuẩn bị khá tốt cho RAG, nhưng hiện không có code nào retrieve từ file này.

RAG hiện chỉ sort/filter phân khu, không search theo câu hỏi.

Ví dụ người dùng hỏi:

```text
The Zenpark có căn 2PN giá bao nhiêu và tiện ích gì?
```

Hệ thống nên retrieve:

- chunk `the-zenpark / apartment_specs`
- chunk `the-zenpark / internal_amenities`
- chunk `the-zenpark / external_amenities`

Nhưng hiện tại RAG chỉ đưa top 3 phân khu tổng quát, giá `?-? tỷ`.

### Nguyên nhân 3: Không có matching rules mới

`get_matching_rules()` hiện trả `{}`.

Do đó các logic như:

- ở thật nên ưu tiên phân khu nào;
- đầu tư nên ưu tiên phân khu nào;
- ngân sách 3 tỷ phù hợp phân khu nào;
- gia đình có con nên ưu tiên tiện ích nào;

không có căn cứ rõ ràng.

### Nguyên nhân 4: Database/API và Agent dùng dữ liệu theo 2 đường khác nhau

Website/API catalog:

```text
cleaned_data -> seed_catalog -> database subdivisions/apartment_specs/amenities/sales_policies
```

AI Agent:

```text
cleaned_data -> load_seed_data fallback -> map rút gọn -> RAG context
```

Điều này gây nguy cơ:

- web hiển thị đúng nhưng AI nói sai;
- database đã seed cũ nhưng cleaned data đã cập nhật mới;
- restart backend chưa chắc cập nhật DB nếu bảng `subdivisions` đã có dữ liệu, vì `seed_catalog()` bỏ qua seed khi bảng đã có records.

### Nguyên nhân 5: Test hiện tại chưa đo chất lượng trả lời

Tests hiện tại chủ yếu kiểm tra:

- endpoint không crash;
- intent guardrail;
- response có field;
- rate limit;
- handover;

Chưa có test kiểu:

- hỏi Zenpark 2PN thì phải trả đúng khoảng giá từ cleaned data;
- hỏi tiện ích nội khu The Zenpark thì phải nhắc vườn Nhật/hồ cá Koi/sảnh lounge;
- hỏi phân khu không có giá thì phải nói chưa cập nhật, không tự bịa;
- hỏi The Senique Hanoi giá thì phải không đưa giá cụ thể vì data chưa cập nhật.

## 5. Đánh giá mức độ hiện tại

| Hạng mục | Đánh giá | Mức độ |
|---|---|---|
| Cleaned catalog | Có cấu trúc khá tốt, coverage 12 phân khu | 75% |
| AI knowledge chunks | Đều, phù hợp RAG, nhưng chưa được dùng | 65% data-ready, 0% runtime |
| Data -> database catalog | Đã seed được web/API, nhưng chưa có cơ chế update khi data đổi | 65% |
| Intent detection | Có nền tảng, nhưng regex/encoding và coverage cần kiểm tra | 60% |
| RAG retrieval | Đang rất đơn giản, chưa retrieve theo câu hỏi/chunk | 35% |
| Recommendation scoring | Có framework nhưng thiếu field/rules nên kết quả dễ sai | 35% |
| LLM prompt/guardrail | Có prompt khá ổn, nhưng phụ thuộc context nghèo | 60% |
| Evaluation | Chưa có golden dataset/quality tests | 20% |

Đánh giá chung: AI Agent hiện tại usable về mặt kỹ thuật, nhưng chưa đáng tin về mặt nội dung tư vấn. Mức độ đạt so với mục tiêu AI Advisor demo được: khoảng 45-50%.

## 6. Phương án đề xuất

### Phase 1 - Hotfix data adapter cho Agent

Mục tiêu: làm Agent đọc đúng `cleaned_apartment_zones.json` ngay, chưa cần vector database.

Việc cần làm:

1. Sửa `src/services/vinhomes_data.py`.
2. Tạo adapter từ cleaned schema sang runtime schema:

```text
apartment_specs -> unit_types
apartment_specs.price -> total_price_range_billion min/max
internal_amenities + external_amenities -> amenities/context
sales_policies -> policy context
handover_standard/legal_status -> context
```

3. `format_zones_for_context()` phải đưa được:

- tên phân khu;
- vị trí;
- trạng thái bàn giao;
- loại căn;
- khoảng diện tích;
- khoảng giá theo từng loại căn;
- tiện ích nổi bật;
- chính sách bán hàng;
- pháp lý/bàn giao.

4. Nếu giá là “Chưa cập nhật” hoặc “Đã bán hết”, context phải giữ nguyên trạng thái đó, không convert thành số.

Kết quả mong đợi:

- Không còn `Giá tham khảo: ?-? tỷ` nếu data có giá.
- Hỏi The Zenpark 2PN thì context có `2PN: 64 - 70m2, 3,0 - 3,5 tỷ`.
- Hỏi tiện ích The Zenpark thì context có vườn Nhật, hồ cá Koi, sảnh lounge, gym, bể bơi...

### Phase 2 - Dùng `ai_knowledge_chunks.json` làm retrieval source

Mục tiêu: retrieve đúng chunk theo câu hỏi.

Chưa cần Chroma ngay, có thể làm keyword/BM25 đơn giản trước:

1. Load `ai_knowledge_chunks.json`.
2. Detect slug/phân khu trong query:
   - “zenpark” -> `the-zenpark`
   - “sapphire” -> `the-sapphire`
   - “masteri waterfront” -> `masteri-waterfront`
3. Detect topic:
   - giá/căn/2PN/studio -> `apartment_specs`
   - tiện ích/nội khu/bể bơi/gym -> `internal_amenities`
   - trường học/vinmec/vinuni/vincom -> `external_amenities`
   - chính sách/vay/chiết khấu/thanh toán -> `sales_policies`
   - vị trí/đường/xa/gần -> `location`
4. Retrieve top chunks theo slug + topic.
5. Nếu không detect được slug/topic thì fallback top chunks theo keyword score.

Kết quả mong đợi:

- Câu hỏi cụ thể lấy đúng chunk cụ thể.
- Câu trả lời ít bịa hơn vì context hẹp và liên quan hơn.

### Phase 3 - Đồng bộ Agent với database catalog

Mục tiêu: web/API và AI dùng cùng một nguồn dữ liệu runtime.

Có 2 hướng:

#### Hướng A: Agent đọc JSON cleaned trực tiếp

Ưu điểm:

- Nhanh.
- Ít thay đổi database.
- Dễ hotfix.

Nhược điểm:

- Có nguy cơ web và AI lệch nếu database đã seed cũ.

#### Hướng B: Agent đọc từ database `subdivisions`

Ưu điểm:

- Web và AI thống nhất.
- Dashboard/admin sau này dễ quản trị data.
- Phù hợp production hơn.

Nhược điểm:

- Cần repository/service layer tốt hơn.
- Cần cơ chế re-seed/update khi cleaned data đổi.

Đề xuất: làm Phase 1/2 bằng JSON để nhanh ổn định AI, sau đó Phase 3 chuyển dần sang database hoặc xây sync pipeline rõ ràng.

### Phase 4 - Tạo evaluation dataset

Tạo file:

```text
eval/agent_golden_questions.json
```

Mỗi sample gồm:

```json
{
  "question": "The Zenpark căn 2PN giá bao nhiêu?",
  "expected_facts": [
    "2PN",
    "64 - 70m2",
    "3,0 - 3,5 tỷ",
    "giá tham khảo"
  ],
  "forbidden_facts": [
    "còn căn",
    "giá chốt",
    "đặt cọc ngay"
  ],
  "source_slug": "the-zenpark",
  "source_topic": "apartment_specs"
}
```

Nhóm test nên có tối thiểu:

- 12 câu overview, mỗi phân khu 1 câu.
- 12 câu giá/loại căn.
- 12 câu tiện ích.
- 6 câu chính sách bán hàng.
- 6 câu guardrail quỹ căn/mã căn.
- 6 câu data missing, bắt buộc trả “chưa cập nhật”.

### Phase 5 - Vector RAG / semantic search

Sau khi keyword RAG ổn, có thể nâng lên:

- ChromaDB local hoặc pgvector.
- Embedding chunks.
- Top-k semantic retrieval.
- Rerank theo slug/topic.
- Citation theo chunk.

Không nên nhảy ngay vào vector nếu data adapter còn sai, vì vector search trên dữ liệu chưa chuẩn vẫn trả lời sai.

## 7. Giải pháp cụ thể đề xuất cho lần triển khai tiếp theo

Ưu tiên làm theo thứ tự:

### P0 - Sửa data adapter

File chính:

- `src/services/vinhomes_data.py`
- `src/agents/nodes/rag_node.py`
- `src/services/recommender.py`

Việc cụ thể:

- Thêm hàm parse price từ `apartment_specs`.
- Thêm hàm lấy `unit_types`.
- Thêm hàm format context chi tiết theo subdivision.
- Bỏ phụ thuộc vào `matching_rules` nếu chưa có rules.
- Nếu không có rules, scoring phải dựa vào giá/unit type thực tế.

### P1 - Dùng chunks cho câu hỏi cụ thể

File chính:

- `src/services/knowledge_retriever.py` mới.
- `src/agents/nodes/rag_node.py`.

Việc cụ thể:

- Load `ai_knowledge_chunks.json`.
- Retrieve theo slug/topic/keyword.
- Trả context gồm 3-5 chunks liên quan nhất.

### P2 - Cải thiện prompt

File chính:

- `src/agents/nodes/llm_node.py`

Việc cụ thể:

- Thêm rule: nếu context không có giá của loại căn được hỏi, nói “chưa cập nhật”.
- Thêm rule: không lấy giá của phân khu khác để trả lời phân khu đang hỏi.
- Thêm rule: phân biệt “đã bán hết” với “chưa cập nhật”.
- Thêm source label trong context, ví dụ `[the-zenpark/apartment_specs]`.

### P3 - Thêm tests chất lượng AI

File đề xuất:

- `tests/test_agents/test_retrieval_quality.py`
- `tests/test_agents/test_agent_factuality.py`
- `eval/agent_golden_questions.json`

Test nên mock LLM hoặc test retrieval context trước, để không phụ thuộc API key.

## 8. Checklist xác minh sau khi sửa

Sau khi sửa Phase 1/2, cần test thủ công các câu:

1. `The Zenpark có căn 2PN giá bao nhiêu?`
   - Phải trả khoảng `3,0 - 3,5 tỷ`.
   - Phải nói là giá tham khảo.

2. `The Senique Hanoi căn 2PN giá bao nhiêu?`
   - Không được bịa giá.
   - Phải nói giá hiện chưa cập nhật nếu data đang là `Chưa cập nhật`.

3. `Tôi có 3 tỷ muốn mua 2PN để ở thật, nên chọn phân khu nào?`
   - Phải dựa trên các phân khu có 2PN quanh ngân sách 3 tỷ.
   - Không được chỉ trả top theo thứ tự file.

4. `The Zenpark có tiện ích nội khu gì?`
   - Phải nhắc đúng các tiện ích từ chunk/internal amenities.

5. `Căn R1.01 còn không?`
   - Phải handover sang Sales, không xác nhận còn/hết.

6. `Chính sách vay của The Sapphire là gì?`
   - Phải lấy đúng sales policies của The Sapphire, không lẫn sang Zenpark.

## 9. Kết luận

Bộ `cleaned_data` mới là hướng đúng, nhưng AI Agent hiện chưa được “nối lại” đúng với schema mới. Vấn đề chính không phải model OpenRouter/OpenAI yếu, mà là RAG context không đủ và mapping data sai.

Khuyến nghị của tôi:

1. Không thay model vội.
2. Không thêm multi-agent vội.
3. Ưu tiên sửa data adapter và retrieval từ `ai_knowledge_chunks.json`.
4. Sau đó thêm evaluation dataset để đo chất lượng.
5. Khi retrieval trả đúng context, lúc đó mới tối ưu prompt/model/vector database.

Nếu làm đúng thứ tự này, AI Advisor sẽ chuyển từ “chat được nhưng dễ sai” sang “trả lời có căn cứ theo data dự án”, phù hợp để demo mentor và tiếp tục phát triển production.

# Kế Hoạch Tích Hợp Tính Năng AI Vào Website Vinhomes Ocean Park (Cập nhật)

Tài liệu này hướng dẫn chi tiết cách thức tích hợp các tính năng AI của bạn sử dụng **API của OpenRouter (mô hình miễn phí)** và tuân thủ nghiêm ngặt các quy tắc nghiệp vụ trong tài liệu hướng dẫn thu thập dữ liệu [DATA_COLLECTION_AND_UI_GUIDE_VINHOMES_AI_ADVISOR.md](file:///d:/real-estate-website-cloner/docs/DATA_COLLECTION_AND_UI_GUIDE_VINHOMES_AI_ADVISOR.md).

---

## 1. Thiết Lập Kết Nối OpenRouter API

Bạn sẽ sử dụng OpenRouter để gọi các mô hình ngôn ngữ lớn (LLM) miễn phí (ví dụ: `google/gemini-2.5-flash:free` hoặc `meta-llama/llama-3-8b-instruct:free`).

### Cấu hình biến môi trường (`.env.local`):
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=google/gemini-2.5-flash:free
OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
```

---

## 2. Quy Tắc Nghiệp Vụ Của AI (Theo Hướng Dẫn Sản Phẩm)

Theo [DATA_COLLECTION_AND_UI_GUIDE_VINHOMES_AI_ADVISOR.md](file:///d:/real-estate-website-cloner/docs/DATA_COLLECTION_AND_UI_GUIDE_VINHOMES_AI_ADVISOR.md), AI Advisor cần tuân thủ tuyệt đối các giới hạn sau:

1. **Phạm vi tư vấn:** Chỉ tư vấn chắc chắn đến cấp **Dự án (Project)**, **Phân khu (Zone)**, **Tòa (Building)** và **Loại căn hộ (Unit Type)**.
2. **Nguyên tắc "Không":**
   - Không tư vấn/chốt mã căn cụ thể (ví dụ: căn 12A, tòa R1.01).
   - Không xác nhận căn cụ thể còn hay đã bán.
   - Không cam kết giá chốt cuối cùng hoặc giữ chỗ.
3. **Quy tắc chuyển đổi (Sales Handover):** Nếu khách hỏi quỹ căn thực tế, mã căn cụ thể, giá chốt hoặc muốn cọc giữ chỗ $\rightarrow$ AI kích hoạt form xin thông tin (Họ tên, SĐT) và chuyển thông tin cho Sales.
4. **Quy tắc về giá và chính sách:**
   - Luôn nhấn mạnh cụm từ **"Giá tham khảo"** và nêu rõ **mốc thời gian của dữ liệu** (ví dụ: *"Theo dữ liệu Quý 1/2026..."*).
   - Cảnh báo rõ ràng nếu chính sách bán hàng đã hết hạn hoặc chưa xác định rõ hiệu lực.
   - Mọi mức độ tin cậy của dữ liệu (`confidence_level` là `low`) khi đưa ra phải đi kèm cảnh báo tham khảo.

---

## 3. Cấu Trúc Thư Mục Đề Xuất (Directory Structure)

```text
src/
  app/
    api/
      ai/
        chat/route.ts          # Gọi OpenRouter API, RAG ngữ cảnh phân khu & phân tích ý định
        leads/route.ts         # Quản lý, lưu trữ & chấm điểm Lead trước khi bàn giao
    admin/
      leads/
        page.tsx               # Dashboard xem Lead của Sales, xem lịch sử chat và phân tích của AI
    ai-consultant/
      page.tsx                 # Trang tư vấn AI chuyên sâu độc lập
  
  components/
    ai/
      ChatWidget.tsx           # Floating Chatbot ở góc phải bên dưới các trang clone
      LeadTable.tsx            # Bảng danh sách lead dùng trong admin
      RecommendationCard.tsx   # Card hiển thị trực quan các phân khu được AI gợi ý
      LeadForm.tsx             # Form thu thập thông tin khi chuyển giao cho sales
      
  hooks/
    useAIChat.ts               # Hook quản lý lịch sử chat và gửi dữ liệu tới API Route
    useLeads.ts                # Hook lấy danh sách lead, cập nhật trạng thái sales
    
  data/
    vinhomes-db/
      projects.ts              # Thông tin dự án (Ocean Park Gia Lâm)
      zones.ts                 # Thông tin chi tiết các phân khu (Zenpark, Sapphire, Zurich...)
      buildings.ts             # Dữ liệu tòa nhà (R1.01, S2.12...) và khoảng diện tích/giá
      unitTypeStats.ts         # Thống kê diện tích và khoảng giá tham khảo theo loại căn
      amenities.ts             # Bản đồ tiện ích nội khu & xung quanh
      transportRoutes.ts       # Khoảng cách di chuyển và tuyến đường chính
      salesPolicies.ts         # Chính sách bán hàng & hỗ trợ vay ngân hàng
```

---

## 4. Quá Trình Triển Khai và Kiểm Thử Trực Quan (E2E)

### Bước 1: Khởi tạo Mock Database ở Client (`src/data/vinhomes-db/`)
Chuyển hóa dữ liệu mẫu từ hướng dẫn sản phẩm thành các file TypeScript chứa cấu trúc dữ liệu chính xác để làm ngữ cảnh (RAG) hoặc bộ đối chiếu dữ liệu cho AI.
*Ví dụ cấu trúc `zones.ts`:*
```typescript
export interface Zone {
  name: string;
  slug: string;
  description: string;
  design_style: string;
  handover_status: 'handed_over' | 'under_construction';
  total_buildings: number;
  featured_amenities: string[];
  target_audience: string[];
}
```

### Bước 2: Xây dựng Backend Route Handler (`src/app/api/ai/chat/route.ts`)
* API nhận `messages` và thực hiện các bước sau:
  1. **Nhận diện ý định (Intent Detection):** Nếu khách yêu cầu xem căn cụ thể, đặt cọc hoặc hỏi quỹ căn còn trống $\rightarrow$ API trả về cờ `trigger_handover: true` để giao diện hiển thị form nhập SĐT của Sales.
  2. **Truy vấn Ngữ cảnh (RAG):** Đọc dữ liệu từ `src/data/vinhomes-db/` để tìm phân khu, tòa nhà hoặc khoảng giá phù hợp với mong muốn của người dùng.
  3. **Gọi OpenRouter API:** Gửi System Prompt nghiêm ngặt cùng dữ liệu ngữ cảnh tìm được qua OpenRouter tới mô hình miễn phí.
  
*Ví dụ System Prompt:*
> "Bạn là trợ lý ảo tư vấn bất động sản tại Vinhomes Ocean Park Gia Lâm. Bạn chỉ cung cấp thông tin tổng quan về phân khu, tòa, loại căn và tiện ích. Bạn KHÔNG được phép tư vấn mã căn cụ thể hay trạng thái còn/bán. Luôn nói rõ 'Giá tham khảo theo mốc Q1/2026'. Nếu khách hỏi về quỹ căn thực tế hoặc muốn cọc giữ chỗ, hãy lịch sự mời họ để lại tên và số điện thoại."

### Bước 3: Phát triển React Hooks & Giao Diện Client
* **`useAIChat.ts`**: Nhận tin nhắn từ người dùng, gửi tới `/api/ai/chat`, nhận phản hồi và cập nhật lịch sử chat.
* **`<ChatWidget.tsx>`**: Nút bấm góc dưới màn hình mở ra khung chat. Khi nhận được cờ `trigger_handover` từ API hoặc khi người dùng chủ động điền thông tin, chatbot sẽ hiển thị form `<LeadForm />`.

### Bước 4: Phát triển Trang Quản Lý Lead cho Sales (`src/app/admin/leads/page.tsx`)
* Giao diện liệt kê các lead đã đăng ký kèm theo:
  - Thông tin liên hệ (Tên, SĐT).
  - Lịch sử chat chi tiết.
  - Phân tích chất lượng tự động từ AI (Điểm chất lượng: **HOT** / **WARM** / **COLD** kèm lý do phân tích).
  - Trạng thái xử lý và gán cho nhân viên Sales hỗ trợ.

---

## 5. Quy Trình Chạy Thử Nghiệm Thực Tế (Visual Testing Guide)

1. Khởi động môi trường dev: `npm run dev`.
2. Mở trình duyệt truy cập website clone (ví dụ: `http://localhost:3000`).
3. Nhấp vào bong bóng chat AI ở góc dưới bên phải màn hình:
   - **Kịch bản 1 (Tư vấn đúng luật):** Hỏi *"Tôi có 2 tỷ, muốn mua căn 1 phòng ngủ ở phân khu nào yên tĩnh?"* $\rightarrow$ AI gợi ý phân khu **The Zenpark** (phong cách Nhật, yên tĩnh) với giá tham khảo, hiển thị link dẫn tới trang chi tiết phân khu trên web.
   - **Kịch bản 2 (Cảnh báo vi phạm):** Hỏi *"Căn hộ số 10 ở tầng 15 tòa R1.01 còn không?"* $\rightarrow$ AI sẽ trả lời theo mẫu từ chối, giải thích rằng AI chỉ hỗ trợ thông tin tham khảo, và hiển thị form để lại thông tin để Sales kiểm tra quỹ căn thực tế.
4. Điền form đăng ký tư vấn $\rightarrow$ Truy cập tiếp đường dẫn `http://localhost:3000/admin/leads` để kiểm tra xem Lead mới đã xuất hiện trong hệ thống quản lý kèm phân tích chất lượng của AI chưa.

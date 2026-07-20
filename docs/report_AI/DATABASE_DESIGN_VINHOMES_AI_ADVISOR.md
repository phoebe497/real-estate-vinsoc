# Thiết kế database: AI tư vấn chung cư Vinhomes Ocean Park Gia Lâm

## 1. Nguyên tắc thiết kế

Database phục vụ tư vấn ở cấp:

- Dự án.
- Zone/phân khu lớn.
- Subzone/tiểu phân khu hoặc cụm nhỏ trong zone.
- Tòa.
- Loại căn.
- Giá tham khảo.
- Chính sách.
- Tiện ích.
- Vị trí, kết nối giao thông và đường đi.
- Tài liệu/ảnh/bản đồ/mặt bằng.
- Chat, lead và phân công sale.

Hierarchy chuẩn từ thời điểm cập nhật tài liệu:

```text
project -> zone -> subzone -> building
```

Ví dụ thực tế:

```text
Vinhomes Ocean Park Gia Lâm
-> The Ocean View
-> The Zenpark
-> R1.01 / R1.02 / R1.03 / R1.05
```

Hoặc:

```text
Vinhomes Ocean Park Gia Lâm
-> The Sapphire
-> Sapphire 1
-> S1.01 / S1.02 / ...
```

Database không dùng để AI xác nhận từng mã căn cụ thể còn hay đã bán trong phase đầu.

Nếu sau này có dữ liệu căn cụ thể, nên tách thành module nội bộ cho sale/admin, không để AI tự chốt với khách nếu chưa có quy trình kiểm duyệt real-time.

## 2. Quy ước chung

Các bảng nên có field chuẩn:

| Field | Nhiệm vụ |
|---|---|
| `id` | Khóa chính. |
| `created_at` | Thời điểm tạo bản ghi. |
| `updated_at` | Thời điểm cập nhật gần nhất. |
| `created_by` | Account tạo bản ghi nếu cần audit. |
| `updated_by` | Account cập nhật bản ghi nếu cần audit. |
| `is_active` | Bật/tắt bản ghi mà không xóa vật lý. |

Quy ước dữ liệu:

- Tiền tệ dùng `numeric`, không dùng `float`.
- Diện tích dùng `numeric`.
- Enum nên định nghĩa ở backend để tránh sai chính tả.
- Slug phải unique trong phạm vi parent phù hợp.
- Tên route/API nên phản ánh đủ hierarchy `zone/subzone/building`.

## 3. accounts

Lưu tài khoản đăng nhập của customer, sale và admin.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính account. |
| `name` | string | Tên hiển thị. |
| `email` | string | Email đăng nhập, cần unique. |
| `phone` | string/null | Số điện thoại. |
| `password_hash` | string | Mật khẩu đã hash bằng bcrypt. |
| `role` | enum | `customer`, `sale`, `admin`. |
| `status` | enum | `active`, `inactive`, `locked`. |
| `last_login_at` | datetime/null | Lần đăng nhập gần nhất. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

Ghi chú:

- Không có trang đăng ký sale public.
- Sale/admin nên được tạo bởi admin.
- Customer có thể tự đăng ký hoặc được tạo khi để lại lead.

## 4. projects

Lưu thông tin tổng quan dự án.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính dự án. |
| `name` | string | Tên dự án, ví dụ `Vinhomes Ocean Park Gia Lâm`. |
| `slug` | string | Đường dẫn SEO. |
| `short_description` | text | Mô tả ngắn dùng cho card/hero. |
| `description` | text | Nội dung tổng quan dài. |
| `developer` | string | Chủ đầu tư. |
| `location` | text | Địa chỉ/vị trí dự án. |
| `total_area_ha` | numeric/null | Tổng diện tích theo ha. |
| `building_density` | numeric/null | Mật độ xây dựng nếu có. |
| `ownership_type` | string/null | Hình thức sở hữu. |
| `handover_summary` | text/null | Tóm tắt bàn giao/tiến độ. |
| `seo_title` | string/null | Title SEO. |
| `seo_description` | string/null | Description SEO. |
| `is_active` | boolean | Có hiển thị dự án hay không. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 5. zones

Lưu phân khu lớn hoặc nhóm sản phẩm cấp cao trong dự án.

Ví dụ:

- The Sapphire.
- The Ocean View.
- The Metropolitan.
- Masteri Waterfront.

Trong mô hình mới, một `zone` có thể chứa nhiều `subzones`.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính zone. |
| `project_id` | fk | Liên kết tới `projects.id`. |
| `name` | string | Tên zone/phân khu lớn. |
| `slug` | string | Slug SEO trong phạm vi project. |
| `subtitle` | string/null | Mô tả ngắn dưới tên zone. |
| `description` | text | Mô tả chi tiết zone. |
| `location_summary` | text/null | Vị trí của zone trong dự án. |
| `design_style` | string/null | Phong cách thiết kế/chủ đề tổng thể. |
| `developer` | string/null | Đơn vị phát triển nếu khác chủ đầu tư tổng. |
| `handover_status` | enum | `handed_over`, `under_construction`, `planned`, `updating`. |
| `handover_note` | text/null | Ghi chú bàn giao/tiến độ. |
| `total_subzones` | int/null | Số subzone/tiểu phân khu trong zone. |
| `total_buildings` | int/null | Tổng số tòa ước tính trong toàn zone. |
| `total_units_estimate` | int/null | Tổng số căn ước tính, không dùng xác nhận còn/bán. |
| `position_lat` | numeric/null | Vĩ độ nếu cần bản đồ. |
| `position_lng` | numeric/null | Kinh độ nếu cần bản đồ. |
| `sort_order` | int | Thứ tự hiển thị. |
| `is_featured` | boolean | Có hiển thị nổi bật ở trang chủ không. |
| `is_active` | boolean | Có hiển thị không. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 6. subzones

Lưu tiểu phân khu/cụm nhỏ nằm trong một zone.

Đây là entity mới để phản ánh đúng thực tế:

```text
zone -> subzone -> building
```

Ví dụ:

- Zone `The Sapphire` có subzone `Sapphire 1`, `Sapphire 2`.
- Zone `The Ocean View` có subzone `The Zenpark`, `The Pavilion`, `The Bayfront`.
- Zone `The Metropolitan` có subzone `The Zurich`, `The Beverly`, `The London`, `The Paris`.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính subzone. |
| `zone_id` | fk | Liên kết tới `zones.id`. |
| `name` | string | Tên subzone/tiểu phân khu. |
| `slug` | string | Slug SEO trong phạm vi zone. |
| `subtitle` | string/null | Mô tả ngắn. |
| `description` | text | Mô tả chi tiết subzone. |
| `location_summary` | text/null | Vị trí tương đối trong zone/dự án. |
| `design_style` | string/null | Phong cách thiết kế của subzone. |
| `handover_status` | enum | `handed_over`, `under_construction`, `planned`, `updating`. |
| `handover_note` | text/null | Ghi chú tiến độ/bàn giao. |
| `total_buildings` | int/null | Số tòa thuộc subzone. |
| `total_units_estimate` | int/null | Tổng số căn ước tính ở cấp subzone. |
| `target_customer_summary` | text/null | Nhóm khách phù hợp: ở thật, đầu tư, gia đình, cho thuê. |
| `highlight_summary` | text/null | Điểm nổi bật dùng cho card/chat. |
| `position_lat` | numeric/null | Vĩ độ nếu cần bản đồ. |
| `position_lng` | numeric/null | Kinh độ nếu cần bản đồ. |
| `map_position` | json/null | Tọa độ tương đối trên bản đồ masterplan. |
| `sort_order` | int | Thứ tự hiển thị trong zone. |
| `is_featured` | boolean | Có nổi bật ở trang chủ/trang chung cư không. |
| `is_active` | boolean | Có hiển thị không. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

Quy tắc:

- AI có thể tư vấn rất kỹ ở cấp subzone vì đây thường là cấp khách hàng nhận diện rõ nhất.
- Nếu dữ liệu thực tế chỉ có zone và building, vẫn nên tạo subzone mặc định như `main` hoặc `general` để giữ schema nhất quán.

## 7. buildings

Lưu thông tin từng tòa thuộc subzone.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính tòa. |
| `subzone_id` | fk | Liên kết tới `subzones.id`. |
| `zone_id` | fk/cache | Liên kết cache tới `zones.id` để filter nhanh, có thể suy ra từ subzone. |
| `name` | string | Tên tòa, ví dụ `R1.01`, `S1.01`, `P1`. |
| `slug` | string | Slug SEO trong phạm vi subzone. |
| `description` | text/null | Mô tả chi tiết tòa. |
| `floors` | int/null | Số tầng. |
| `basement_count` | int/null | Số tầng hầm nếu có. |
| `handover_status` | enum | Trạng thái bàn giao/thi công. |
| `handover_note` | text/null | Ghi chú tiến độ. |
| `location_note` | text/null | Vị trí: gần hồ, gần trường, gần trục đường, gần tiện ích nào. |
| `view_summary` | text/null | Tóm tắt hướng/view nổi bật. |
| `elevator_count` | int/null | Số thang máy nếu có. |
| `unit_count_estimate` | int/null | Số căn ước tính của tòa, không dùng xác nhận quỹ căn. |
| `map_position` | json/null | Tọa độ tương đối trên bản đồ mặt bằng. |
| `sort_order` | int | Thứ tự hiển thị. |
| `is_active` | boolean | Có hiển thị không. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

Quy tắc:

- `subzone_id` là khóa ngoại chính.
- `zone_id` chỉ nên dùng như denormalized/cache field để query nhanh. Nếu dùng, backend phải đảm bảo `building.zone_id = subzone.zone_id`.

## 8. unit_types

Danh mục loại căn chuẩn.

Ví dụ: Studio, 1PN, 1PN+1, 2PN, 2PN+1, 3PN.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính loại căn. |
| `code` | string | Mã loại căn, ví dụ `studio`, `1br`, `2br_plus`. |
| `name` | string | Tên hiển thị. |
| `bedroom_count` | numeric/null | Số phòng ngủ quy đổi. Có thể dùng `1.5` cho 1PN+1. |
| `bathroom_count` | int/null | Số WC phổ biến. |
| `description` | text/null | Mô tả loại căn. |
| `is_active` | boolean | Có sử dụng không. |

## 9. zone_unit_type_stats

Lưu thống kê loại căn theo zone/phân khu lớn.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `zone_id` | fk | Zone áp dụng. |
| `unit_type_id` | fk | Loại căn áp dụng. |
| `min_area_sqm` | numeric/null | Diện tích nhỏ nhất tham khảo. |
| `avg_area_sqm` | numeric/null | Diện tích trung bình tham khảo. |
| `max_area_sqm` | numeric/null | Diện tích lớn nhất tham khảo. |
| `min_price_total` | numeric/null | Tổng giá thấp nhất tham khảo. |
| `avg_price_total` | numeric/null | Tổng giá trung bình tham khảo. |
| `max_price_total` | numeric/null | Tổng giá cao nhất tham khảo. |
| `min_price_per_sqm` | numeric/null | Đơn giá/m² thấp nhất tham khảo. |
| `avg_price_per_sqm` | numeric/null | Đơn giá/m² trung bình tham khảo. |
| `max_price_per_sqm` | numeric/null | Đơn giá/m² cao nhất tham khảo. |
| `currency` | string | Đơn vị tiền tệ, mặc định `VND`. |
| `data_period` | string | Mốc dữ liệu, ví dụ `Q1/2026`, `06/2026`. |
| `source_note` | text/null | Ghi chú nguồn dữ liệu. |
| `confidence_level` | enum | `high`, `medium`, `low`, `mock`. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 10. subzone_unit_type_stats

Lưu thống kê loại căn theo subzone/tiểu phân khu.

Bảng này là nguồn rất quan trọng vì khách thường hỏi ở cấp The Zenpark, The Pavilion, Sapphire 1, Sapphire 2.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `subzone_id` | fk | Subzone áp dụng. |
| `zone_id` | fk/cache | Zone cha, dùng filter nhanh nếu cần. |
| `unit_type_id` | fk | Loại căn áp dụng. |
| `min_area_sqm` | numeric/null | Diện tích nhỏ nhất tham khảo. |
| `avg_area_sqm` | numeric/null | Diện tích trung bình tham khảo. |
| `max_area_sqm` | numeric/null | Diện tích lớn nhất tham khảo. |
| `min_price_total` | numeric/null | Tổng giá thấp nhất tham khảo. |
| `avg_price_total` | numeric/null | Tổng giá trung bình tham khảo. |
| `max_price_total` | numeric/null | Tổng giá cao nhất tham khảo. |
| `min_price_per_sqm` | numeric/null | Đơn giá/m² thấp nhất tham khảo. |
| `avg_price_per_sqm` | numeric/null | Đơn giá/m² trung bình tham khảo. |
| `max_price_per_sqm` | numeric/null | Đơn giá/m² cao nhất tham khảo. |
| `currency` | string | Đơn vị tiền tệ. |
| `data_period` | string | Mốc dữ liệu. |
| `source_note` | text/null | Ghi chú nguồn dữ liệu. |
| `confidence_level` | enum | `high`, `medium`, `low`, `mock`. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 11. building_unit_type_stats

Lưu thống kê loại căn theo từng tòa.

Bảng này dùng khi khách hỏi sâu hơn ở cấp tòa, nhưng vẫn không đi đến mã căn cụ thể.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `building_id` | fk | Tòa áp dụng. |
| `subzone_id` | fk/cache | Subzone cha, dùng filter nhanh nếu cần. |
| `zone_id` | fk/cache | Zone cha, dùng filter nhanh nếu cần. |
| `unit_type_id` | fk | Loại căn áp dụng. |
| `min_area_sqm` | numeric/null | Diện tích nhỏ nhất tham khảo trong tòa. |
| `avg_area_sqm` | numeric/null | Diện tích trung bình tham khảo trong tòa. |
| `max_area_sqm` | numeric/null | Diện tích lớn nhất tham khảo trong tòa. |
| `min_price_total` | numeric/null | Tổng giá thấp nhất tham khảo. |
| `avg_price_total` | numeric/null | Tổng giá trung bình tham khảo. |
| `max_price_total` | numeric/null | Tổng giá cao nhất tham khảo. |
| `min_price_per_sqm` | numeric/null | Đơn giá/m² thấp nhất tham khảo. |
| `avg_price_per_sqm` | numeric/null | Đơn giá/m² trung bình tham khảo. |
| `max_price_per_sqm` | numeric/null | Đơn giá/m² cao nhất tham khảo. |
| `data_period` | string | Mốc dữ liệu. |
| `source_note` | text/null | Ghi chú nguồn. |
| `confidence_level` | enum | Mức tin cậy. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 12. price_histories

Lưu biến động giá theo thời gian.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `project_id` | fk/null | Dự án, dùng khi thống kê toàn dự án. |
| `zone_id` | fk/null | Zone/phân khu lớn. |
| `subzone_id` | fk/null | Subzone/tiểu phân khu. |
| `building_id` | fk/null | Tòa. |
| `unit_type_id` | fk/null | Loại căn. |
| `period_type` | enum | `month`, `quarter`, `year`. |
| `period` | string | Kỳ dữ liệu, ví dụ `2026-06`, `Q2/2026`. |
| `min_price_per_sqm` | numeric/null | Giá/m² thấp nhất. |
| `avg_price_per_sqm` | numeric/null | Giá/m² trung bình. |
| `max_price_per_sqm` | numeric/null | Giá/m² cao nhất. |
| `transaction_count` | int/null | Số giao dịch ghi nhận nếu có. |
| `liquidity_note` | text/null | Ghi chú thanh khoản. |
| `source_note` | text/null | Nguồn dữ liệu. |
| `confidence_level` | enum | Mức tin cậy dữ liệu. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

Quy tắc:

- Khi có cả `subzone_id` và `building_id`, `building_id` phải thuộc đúng `subzone_id`.
- Khi chỉ có `zone_id`, số liệu là cấp tổng hợp zone.
- Khi chỉ có `subzone_id`, số liệu là cấp tiểu phân khu.

## 13. bank_rates

Lưu lãi suất ngân hàng để calculator sử dụng.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `bank_name` | string | Tên ngân hàng. |
| `product_name` | string/null | Tên gói vay. |
| `fixed_rate_percent` | numeric | Lãi suất ưu đãi/cố định ban đầu. |
| `fixed_months` | int | Số tháng áp dụng lãi suất cố định. |
| `floating_rate_formula` | text/null | Công thức/thuyết minh lãi suất thả nổi. |
| `max_loan_to_value_percent` | numeric/null | Tỷ lệ vay tối đa. |
| `max_term_years` | int/null | Thời hạn vay tối đa. |
| `prepayment_fee_note` | text/null | Ghi chú phí trả nợ trước hạn. |
| `effective_from` | date/null | Ngày bắt đầu hiệu lực. |
| `effective_to` | date/null | Ngày hết hiệu lực. |
| `source_note` | text/null | Nguồn cập nhật. |
| `is_active` | boolean | Có đang dùng để tư vấn không. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 14. sales_policies

Lưu chính sách bán hàng theo dự án/zone/subzone/tòa.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `project_id` | fk/null | Chính sách cấp dự án. |
| `zone_id` | fk/null | Chính sách cấp zone. |
| `subzone_id` | fk/null | Chính sách cấp subzone. |
| `building_id` | fk/null | Chính sách cấp tòa. |
| `title` | string | Tên chính sách. |
| `summary` | text | Tóm tắt ngắn để AI trả lời. |
| `booking_amount` | numeric/null | Số tiền booking/cọc tham khảo. |
| `discount_summary` | text/null | Tóm tắt chiết khấu. |
| `payment_schedule` | text/null | Tiến độ thanh toán dạng mô tả. |
| `loan_support` | text/null | Hỗ trợ vay nếu có. |
| `effective_from` | date/null | Ngày bắt đầu hiệu lực. |
| `effective_to` | date/null | Ngày hết hiệu lực. |
| `source_document_id` | fk/null | Tài liệu nguồn nếu có. |
| `confidence_level` | enum | Mức tin cậy. |
| `is_active` | boolean | Có đang áp dụng không. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 15. amenities

Lưu tiện ích nội khu/xung quanh.

Đây là nguồn dữ liệu chính để AI tư vấn kỹ về trường học, bệnh viện, trung tâm thương mại, hồ, công viên, khu thể thao, điểm đỗ xe và các tiện ích quanh từng zone/subzone/tòa.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `project_id` | fk/null | Tiện ích cấp dự án. |
| `zone_id` | fk/null | Tiện ích gần zone. |
| `subzone_id` | fk/null | Tiện ích gần subzone. |
| `building_id` | fk/null | Tiện ích gần tòa. |
| `name` | string | Tên tiện ích. |
| `type` | enum | `school`, `hospital`, `mall`, `park`, `lake`, `transport`, `sports`, `other`. |
| `description` | text/null | Mô tả tiện ích. |
| `distance_text` | string/null | Khoảng cách dạng text. |
| `travel_time_text` | string/null | Thời gian di chuyển. |
| `walking_time_minutes` | int/null | Thời gian đi bộ ước tính. |
| `driving_time_minutes` | int/null | Thời gian đi xe ước tính. |
| `position_lat` | numeric/null | Vĩ độ. |
| `position_lng` | numeric/null | Kinh độ. |
| `is_highlighted` | boolean | Có phải tiện ích nổi bật không. |
| `sort_order` | int | Thứ tự hiển thị. |

## 16. transport_routes

Lưu các tuyến kết nối và hướng dẫn đường đi tham khảo từ/tới dự án, zone, subzone hoặc tòa.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính tuyến đường. |
| `project_id` | fk/null | Tuyến áp dụng cho toàn dự án. |
| `zone_id` | fk/null | Tuyến áp dụng cho zone. |
| `subzone_id` | fk/null | Tuyến áp dụng cho subzone. |
| `building_id` | fk/null | Tuyến áp dụng cho tòa cụ thể nếu có. |
| `origin_name` | string | Điểm xuất phát. |
| `destination_name` | string | Điểm đến. |
| `route_summary` | text | Tóm tắt tuyến đi theo các chặng chính. |
| `main_roads` | text/null | Các trục đường chính đi qua. |
| `distance_km` | numeric/null | Khoảng cách tham khảo theo km. |
| `driving_time_min` | int/null | Thời gian đi xe thấp nhất tham khảo. |
| `driving_time_max` | int/null | Thời gian đi xe cao nhất tham khảo. |
| `public_transport_note` | text/null | Ghi chú xe bus/xe điện/phương tiện công cộng. |
| `traffic_note` | text/null | Ghi chú giao thông, giờ cao điểm, điểm dễ ùn tắc. |
| `best_for` | text/null | Gợi ý phù hợp. |
| `source_note` | text/null | Nguồn dữ liệu hoặc ghi chú nhập liệu. |
| `confidence_level` | enum | `high`, `medium`, `low`, `mock`. |
| `updated_at` | datetime | Thời điểm cập nhật. |

Quy tắc:

- AI chỉ coi thời gian di chuyển là tham khảo nếu không có dữ liệu real-time.
- Nếu khách cần chỉ đường chính xác theo thời điểm hiện tại, AI nên khuyến nghị dùng bản đồ điều hướng hoặc kết nối sale gửi vị trí.

## 17. media_assets

Lưu ảnh, bản đồ, mặt bằng, PDF.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `entity_type` | enum | `project`, `zone`, `subzone`, `building`, `unit_type`, `policy`, `market_report`. |
| `entity_id` | uuid/int | ID của đối tượng tương ứng. |
| `media_type` | enum | `image`, `map`, `floor_plan`, `layout`, `pdf`, `video`. |
| `title` | string | Tiêu đề media. |
| `description` | text/null | Mô tả media. |
| `url` | string | Đường dẫn file. |
| `thumbnail_url` | string/null | Ảnh thumbnail nếu có. |
| `alt_text` | string/null | Text SEO/accessibility cho ảnh. |
| `sort_order` | int | Thứ tự hiển thị. |
| `is_public` | boolean | Có hiển thị cho khách hay chỉ nội bộ. |
| `created_at` | datetime | Thời điểm upload. |

## 18. documents

Lưu tài liệu dùng cho RAG hoặc tham chiếu chính sách.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính. |
| `title` | string | Tên tài liệu. |
| `document_type` | enum | `policy`, `brochure`, `price_sheet`, `market_report`, `legal`, `other`. |
| `file_url` | string | Đường dẫn file gốc. |
| `text_content` | text/null | Nội dung text đã trích xuất nếu có. |
| `source_name` | string/null | Tên nguồn. |
| `source_url` | string/null | URL nguồn nếu có. |
| `effective_from` | date/null | Ngày hiệu lực. |
| `effective_to` | date/null | Ngày hết hiệu lực. |
| `ingestion_status` | enum | `pending`, `processed`, `failed`. |
| `is_active` | boolean | Có dùng cho AI không. |
| `created_at` | datetime | Thời điểm tạo. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 19. conversations

Lưu phiên chat.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính hội thoại. |
| `customer_account_id` | fk/null | Customer đã đăng nhập nếu có. |
| `guest_id` | string/null | ID tạm cho khách chưa đăng nhập. |
| `title` | string | Tiêu đề tự động từ câu hỏi đầu. |
| `channel` | enum | `web`, `sales`, `admin_test`. |
| `last_intent` | string/null | Intent gần nhất AI nhận diện. |
| `lead_id` | fk/null | Lead liên quan nếu đã tạo. |
| `created_at` | datetime | Thời điểm bắt đầu. |
| `updated_at` | datetime | Thời điểm có tin nhắn mới nhất. |

## 20. messages

Lưu từng tin nhắn trong hội thoại.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính tin nhắn. |
| `conversation_id` | fk | Hội thoại chứa tin nhắn. |
| `role` | enum | `user`, `assistant`, `system`, `sale`. |
| `content` | text | Nội dung tin nhắn. |
| `metadata` | json/null | Dữ liệu phụ: intent, entities, action buttons, source ids. |
| `created_at` | datetime | Thời điểm gửi. |

## 21. leads

Lưu nhu cầu khách hàng cần sale xử lý.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính lead. |
| `customer_account_id` | fk/null | Customer nếu đã đăng nhập. |
| `conversation_id` | fk/null | Hội thoại tạo ra lead. |
| `name` | string/null | Tên khách nếu thu thập được. |
| `phone` | string/null | Số điện thoại khách. |
| `email` | string/null | Email khách. |
| `budget_min` | numeric/null | Ngân sách thấp nhất. |
| `budget_max` | numeric/null | Ngân sách cao nhất. |
| `preferred_zone_id` | fk/null | Zone khách quan tâm. |
| `preferred_subzone_id` | fk/null | Subzone khách quan tâm. |
| `preferred_building_id` | fk/null | Tòa khách quan tâm. |
| `preferred_unit_type_id` | fk/null | Loại căn khách quan tâm. |
| `buying_purpose` | enum/null | `live`, `invest`, `rent`, `unknown`. |
| `timeline` | string/null | Thời gian dự kiến mua/xem nhà. |
| `note` | text/null | Ghi chú nhu cầu. |
| `source` | enum | `ai_chat`, `contact_form`, `hotline`, `manual`. |
| `status` | enum | Trạng thái xử lý lead. |
| `priority` | enum | `low`, `medium`, `high`. |
| `created_at` | datetime | Thời điểm tạo lead. |
| `updated_at` | datetime | Thời điểm cập nhật. |

## 22. sales_assignments

Lưu phân công sale phụ trách lead.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính phân công. |
| `lead_id` | fk | Lead được phân công. |
| `sale_account_id` | fk | Sale phụ trách. |
| `assigned_by` | fk/null | Admin/sale manager gán lead. |
| `assigned_at` | datetime | Thời điểm gán. |
| `status` | enum | `active`, `transferred`, `closed`. |
| `note` | text/null | Ghi chú phân công. |

## 23. ai_answer_logs

Lưu log kiểm soát chất lượng AI.

| Trường | Kiểu | Nhiệm vụ |
|---|---|---|
| `id` | uuid/int | Khóa chính log. |
| `conversation_id` | fk/null | Hội thoại liên quan. |
| `message_id` | fk/null | Tin nhắn AI liên quan. |
| `intent` | string/null | Intent AI nhận diện. |
| `entities` | json/null | Entity AI trích xuất: zone, subzone, tòa, loại căn, ngân sách. |
| `used_sources` | json/null | Danh sách bảng/tài liệu được dùng. |
| `confidence_score` | numeric/null | Điểm tự tin nội bộ. |
| `fallback_triggered` | boolean | AI đã chuyển sale vì thiếu dữ liệu không. |
| `review_status` | enum | `pending`, `approved`, `needs_fix`. |
| `created_at` | datetime | Thời điểm tạo log. |

## 24. Module inventory tùy chọn sau này

Không triển khai trong phase đầu.

Nếu sau này team có nguồn dữ liệu real-time đáng tin cậy, có thể thêm:

```text
inventory_snapshots
inventory_items
```

Nguyên tắc:

- Chỉ sale/admin xem chi tiết.
- AI chỉ được nói "cần kiểm tra với sale" nếu dữ liệu không real-time.
- Không đưa mã căn cụ thể ra cho khách nếu chưa có quy trình xác thực.

## 25. Quan hệ dữ liệu chính

```text
projects 1-n zones
zones 1-n subzones
subzones 1-n buildings

unit_types n-n zones qua zone_unit_type_stats
unit_types n-n subzones qua subzone_unit_type_stats
unit_types n-n buildings qua building_unit_type_stats

projects/zones/subzones/buildings/unit_types 1-n media_assets
projects/zones/subzones/buildings 1-n amenities
projects/zones/subzones/buildings 1-n transport_routes
projects/zones/subzones/buildings 1-n price_histories
projects/zones/subzones/buildings 1-n sales_policies

accounts 1-n conversations
conversations 1-n messages
conversations 0-1 leads
leads 1-n sales_assignments
accounts(role=sale) 1-n sales_assignments
```

## 26. Ưu tiên tạo bảng theo phase

Phase 1:

- accounts
- projects
- zones
- subzones
- buildings
- unit_types
- zone_unit_type_stats
- subzone_unit_type_stats
- building_unit_type_stats
- media_assets

Phase 2:

- price_histories
- bank_rates
- sales_policies
- amenities
- transport_routes

Phase 3:

- conversations
- messages
- leads
- sales_assignments
- ai_answer_logs

Phase 4:

- documents
- vector database/chunks
- import logs

## 27. Gợi ý route/API theo hierarchy mới

Frontend route gợi ý:

```text
/chung-cu
/chung-cu/[zoneSlug]
/chung-cu/[zoneSlug]/[subzoneSlug]
/chung-cu/[zoneSlug]/[subzoneSlug]/[buildingSlug]
```

Backend API gợi ý:

```text
GET /api/projects/{projectSlug}/zones
GET /api/zones/{zoneSlug}/subzones
GET /api/subzones/{subzoneSlug}/buildings
GET /api/buildings/{buildingSlug}
GET /api/prices?zone=...&subzone=...&building=...&unit_type=...
```

Nếu cần backward compatibility với route cũ `/chung-cu/[zoneSlug]/[buildingSlug]`, backend nên redirect hoặc map sang subzone mặc định trong thời gian chuyển đổi.

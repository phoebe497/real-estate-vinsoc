# Hướng dẫn lấy data và thiết kế giao diện theo kế hoạch sản phẩm

## 1. Mục tiêu tài liệu

Tài liệu này mô tả cách thu thập, chuẩn hóa và đưa dữ liệu vào sản phẩm AI tư vấn chung cư Vinhomes Ocean Park Gia Lâm.

Phạm vi tư vấn đã chốt:

- Chỉ tư vấn chắc chắn đến cấp dự án, phân khu, tòa và loại căn.
- Không tư vấn/chốt từng mã căn cụ thể.
- Không xác nhận căn cụ thể còn hay đã bán.
- Nếu khách hỏi quỹ căn thực tế, mã căn, giá chốt hoặc giữ chỗ thì chuyển sale phụ trách.

Tài liệu này cũng mô tả cách giao diện client/admin/sales nên hiển thị dữ liệu theo đúng kế hoạch.

## 2. Nhóm dữ liệu cần thu thập

### 2.1. Dữ liệu dự án

Cần thu thập:

- Tên dự án.
- Chủ đầu tư.
- Vị trí tổng thể.
- Quy mô.
- Mật độ xây dựng.
- Loại hình phát triển.
- Hình thức sở hữu.
- Tiến độ/bàn giao tổng quan.
- Mô tả tổng quan.
- Điểm nổi bật.

Nguồn có thể lấy:

- Website chính thức/chuyên trang dự án.
- Brochure dự án.
- Tài liệu bán hàng.
- Nội dung đã được sale/admin xác nhận.

Giao diện sử dụng:

- Homepage hero.
- Section tổng quan dự án.
- Trang `/chung-cu`.
- Chat AI khi khách hỏi “Vinhomes Ocean Park là gì?”, “vị trí ở đâu?”, “có gì nổi bật?”.

## 3. Dữ liệu phân khu

Cần thu thập cho mỗi phân khu:

- Tên phân khu.
- Slug SEO.
- Mô tả ngắn.
- Mô tả chi tiết.
- Phong cách thiết kế.
- Vị trí trong đại đô thị.
- Các tòa thuộc phân khu.
- Tiến độ/bàn giao.
- Tiện ích nổi bật.
- Đối tượng phù hợp: ở thật, đầu tư, gia đình, cho thuê.
- Ảnh đại diện.
- Bản đồ/mặt bằng phân khu.

Ví dụ phân khu ưu tiên:

- The Sapphire.
- The Ocean View.
- The Zenpark.
- The Pavilion.
- The Metropolitan.
- The Zurich.
- The Beverly.
- Masteri Waterfront.
- Masteri Lakeside.
- The Senique Hanoi.

Nguồn có thể lấy:

- Website tham chiếu.
- Brochure từng phân khu.
- Landing page từ chủ đầu tư/đơn vị phân phối.
- File nội bộ của sale.
- Admin nhập tay sau khi xác minh.

Giao diện sử dụng:

- Card phân khu ở trang chủ.
- Trang `/chung-cu`.
- Trang `/chung-cu/[zoneSlug]`.
- Bộ lọc trong bảng giá.
- Chat AI khi khách hỏi “nên chọn phân khu nào?”.

## 4. Dữ liệu tòa

Cần thu thập cho mỗi tòa:

- Tên tòa.
- Phân khu cha.
- Số tầng.
- Tình trạng bàn giao/thi công.
- Vị trí tương đối trong phân khu.
- Gần tiện ích nào.
- Hướng/view nổi bật nếu có.
- Loại căn phổ biến trong tòa.
- Khoảng diện tích phổ biến.
- Khoảng giá tham khảo.
- Ảnh/mặt bằng tòa nếu có.

Không cần thu thập:

- Mã căn cụ thể.
- Tầng/căn còn bán.
- Giá chốt từng căn.

Nguồn có thể lấy:

- Brochure mặt bằng tòa.
- File tư vấn sale.
- Trang chi tiết tòa trên website tham chiếu.
- Admin nhập và xác nhận.

Giao diện sử dụng:

- Trang `/chung-cu/[zoneSlug]/[buildingSlug]`.
- Bảng so sánh các tòa trong cùng phân khu.
- Chat AI khi khách hỏi “tòa nào gần hồ?”, “tòa nào tiện đi học?”, “tòa nào hợp gia đình?”.

## 5. Dữ liệu loại căn

Cần thu thập:

- Studio.
- 1PN.
- 1PN+1.
- 2PN.
- 2PN+1.
- 3PN.

Với mỗi loại căn theo phân khu/tòa:

- Diện tích nhỏ nhất.
- Diện tích trung bình.
- Diện tích lớn nhất.
- Số phòng ngủ.
- Số WC phổ biến.
- Mô tả layout.
- Phù hợp với nhóm khách nào.
- Mặt bằng loại căn nếu có.

Nguồn có thể lấy:

- Brochure.
- Bảng hàng tổng hợp nhưng chỉ lấy thống kê, không lấy mã căn.
- File mặt bằng.
- Dữ liệu sale xác nhận.

Giao diện sử dụng:

- Section loại căn trong trang phân khu/tòa.
- Calculator giá tham khảo.
- Chat AI khi khách hỏi “2PN khoảng bao nhiêu m2?”, “gia đình 3 người nên chọn loại nào?”.

## 6. Dữ liệu giá tham khảo

Cần thu thập theo cấp:

- Phân khu.
- Tòa.
- Loại căn.
- Thời điểm dữ liệu.

Các field cần có:

- Giá/m2 thấp nhất.
- Giá/m2 trung bình.
- Giá/m2 cao nhất.
- Tổng giá thấp nhất.
- Tổng giá trung bình.
- Tổng giá cao nhất.
- Mốc dữ liệu: tháng/quý/năm.
- Ghi chú nguồn.
- Mức tin cậy: high, medium, low.

Không dùng dữ liệu giá để:

- Chốt giá từng căn.
- Xác nhận giá còn hiệu lực tại thời điểm khách hỏi.

Quy tắc AI:

- Luôn nói rõ “giá tham khảo”.
- Luôn nói rõ mốc thời gian dữ liệu.
- Nếu khách cần giá chốt hiện tại, chuyển sale.

Nguồn có thể lấy:

- Bảng giá nội bộ đã được phép dùng.
- Tổng hợp từ sale.
- Dữ liệu giao dịch lịch sử.
- Dữ liệu thị trường do admin nhập.

Giao diện sử dụng:

- Trang `/bang-gia`.
- Card khoảng giá trong trang phân khu/tòa.
- Biểu đồ giá trong `/thi-truong`.
- Calculator trong chat.

## 7. Dữ liệu chính sách

Cần thu thập:

- Tên chính sách.
- Áp dụng cho dự án/phân khu/tòa nào.
- Thời gian hiệu lực.
- Booking/cọc tham khảo.
- Chiết khấu.
- Tiến độ thanh toán.
- Hỗ trợ vay.
- Điều kiện áp dụng.
- Tài liệu nguồn.

Quy tắc:

- Chính sách phải có ngày hiệu lực nếu có thể.
- Nếu chính sách đã hết hạn hoặc chưa rõ hiệu lực, AI phải cảnh báo.
- Nếu khách cần chính sách chính xác để xuống tiền, chuyển sale.

Nguồn có thể lấy:

- PDF chính sách bán hàng.
- File sale/admin cập nhật.
- Thông báo chủ đầu tư.

Giao diện sử dụng:

- Section chính sách trong trang phân khu/tòa.
- Chat AI khi khách hỏi “có chiết khấu không?”, “vay được bao nhiêu?”.
- Admin dashboard upload/cập nhật chính sách.

## 8. Dữ liệu tiện ích, vị trí và đường đi

Đây là nhóm dữ liệu quan trọng, cần làm kỹ.

Cần thu thập:

- Tiện ích nội khu.
- Tiện ích xung quanh.
- Trường học.
- Bệnh viện/phòng khám.
- Trung tâm thương mại.
- Hồ/công viên/khu thể thao.
- Điểm đỗ xe/điểm đón xe.
- Tuyến đường chính.
- Khoảng cách tham khảo.
- Thời gian đi bộ/đi xe tham khảo.
- Ghi chú giờ cao điểm nếu có.

Với mỗi tiện ích:

- Tên tiện ích.
- Nhóm tiện ích.
- Gắn với dự án/phân khu/tòa.
- Khoảng cách.
- Thời gian di chuyển.
- Mô tả vì sao tiện ích đó quan trọng.

Với mỗi tuyến đường:

- Điểm xuất phát.
- Điểm đến.
- Các trục đường chính.
- Khoảng cách km.
- Thời gian di chuyển thấp nhất/cao nhất.
- Ghi chú giao thông.
- Phù hợp với nhóm khách nào.

Ví dụ tuyến cần nhập:

- Cầu Vĩnh Tuy -> Vinhomes Ocean Park.
- Cầu Thanh Trì -> Vinhomes Ocean Park.
- Hồ Hoàn Kiếm -> Vinhomes Ocean Park.
- Cao tốc Hà Nội - Hải Phòng -> các phân khu.
- Quốc lộ 5 -> các phân khu.

Nguồn có thể lấy:

- Google Maps dùng để tham khảo thủ công.
- Tài liệu dự án.
- Kinh nghiệm sale.
- Admin nhập tay và cập nhật định kỳ.

Giao diện sử dụng:

- Section vị trí trong trang dự án.
- Section tiện ích trong trang phân khu/tòa.
- Bản đồ tiện ích.
- Bảng “di chuyển từ các điểm chính”.
- Chat AI khi khách hỏi “đi từ nội thành mất bao lâu?”, “khu nào gần trường?”, “tòa nào gần hồ?”.

## 9. Dữ liệu media

Cần thu thập:

- Ảnh hero dự án.
- Ảnh phân khu.
- Ảnh tòa.
- Bản đồ tổng thể.
- Bản đồ giao thông.
- Mặt bằng phân khu.
- Mặt bằng tòa.
- Mặt bằng loại căn.
- Brochure PDF.
- Chính sách PDF.

Với mỗi media:

- Tiêu đề.
- Loại media.
- Gắn với đối tượng nào.
- URL file.
- Thumbnail.
- Alt text.
- Có public không.

Nguồn có thể lấy:

- Asset chính thức.
- File nội bộ team cung cấp.
- Admin upload.

Giao diện sử dụng:

- Hero.
- Gallery.
- Bản đồ.
- Popup xem mặt bằng.
- Card phân khu/tòa.
- RAG tài liệu nếu là PDF.

## 10. Quy trình lấy và chuẩn hóa data

### Bước 1: Tạo file data thô

Team tạo các file Excel/Google Sheet:

- `projects.xlsx`
- `zones.xlsx`
- `buildings.xlsx`
- `unit_type_stats.xlsx`
- `price_histories.xlsx`
- `amenities.xlsx`
- `transport_routes.xlsx`
- `sales_policies.xlsx`
- `media_assets.xlsx`

### Bước 2: Chuẩn hóa tên

Cần thống nhất:

- Tên phân khu.
- Tên tòa.
- Tên loại căn.
- Slug.
- Đơn vị tiền.
- Đơn vị diện tích.
- Mốc thời gian dữ liệu.

Ví dụ:

```text
The Zenpark -> the-zenpark
R1.01 -> r101
2PN+1 -> 2br-plus
Q1/2026 -> 2026-Q1
```

### Bước 3: Kiểm duyệt dữ liệu

Mỗi dòng dữ liệu nên có:

- `source_note`.
- `confidence_level`.
- `updated_at`.
- Người xác nhận nếu cần.

Mức tin cậy:

- `high`: có nguồn chính thức hoặc sale/admin xác nhận.
- `medium`: tổng hợp từ nhiều nguồn nhưng chưa phải chính sách hiện hành.
- `low`: chỉ dùng để tham khảo nội bộ, AI cần cảnh báo khi trả lời.

### Bước 4: Import vào database

Giai đoạn đầu có thể làm:

- Import bằng script CSV/Excel.
- Admin dashboard nhập tay.

Giai đoạn sau:

- Admin upload Excel.
- Hệ thống validate.
- Preview dữ liệu trước khi import.
- Ghi import log.

### Bước 5: Kiểm tra AI

Sau khi import, test các nhóm câu hỏi:

- Hỏi tổng quan dự án.
- Hỏi so sánh phân khu.
- Hỏi loại căn theo tòa.
- Hỏi giá tham khảo.
- Hỏi lãi vay.
- Hỏi tiện ích/đường đi.
- Hỏi căn cụ thể để kiểm tra AI có chuyển sale không.

## 11. Template dữ liệu tối thiểu để bắt đầu

### zones.csv

```csv
name,slug,description,location_summary,design_style,handover_status,total_buildings,is_featured,source_note,confidence_level
The Zenpark,the-zenpark,Phân khu phong cách Nhật Bản,...,...,Japanese,handed_over,4,true,Admin confirmed,high
```

### buildings.csv

```csv
zone_slug,name,slug,floors,handover_status,location_note,view_summary,source_note,confidence_level
the-zenpark,R1.01,r101,31,handed_over,Gần công viên và tiện ích nội khu,...,Admin confirmed,high
```

### unit_type_stats.csv

```csv
scope,zone_slug,building_slug,unit_type,min_area_sqm,avg_area_sqm,max_area_sqm,min_price_per_sqm,avg_price_per_sqm,max_price_per_sqm,data_period,source_note,confidence_level
zone,the-zenpark,,2PN,53,65,75,50000000,56000000,62000000,2026-Q1,Sales summary,medium
```

### amenities.csv

```csv
scope,zone_slug,building_slug,name,type,distance_text,travel_time_text,walking_time_minutes,driving_time_minutes,description,confidence_level
zone,the-zenpark,,Công viên nội khu,park,khoảng 300m,5 phút đi bộ,5,,Phù hợp gia đình có trẻ nhỏ,high
```

### transport_routes.csv

```csv
scope,zone_slug,building_slug,origin_name,destination_name,route_summary,main_roads,distance_km,driving_time_min,driving_time_max,traffic_note,best_for,confidence_level
project,,,Cầu Vĩnh Tuy,Vinhomes Ocean Park,Đi qua Cổ Linh và cao tốc Hà Nội - Hải Phòng,Cổ Linh; Cao tốc Hà Nội - Hải Phòng,12,20,35,Thời gian phụ thuộc giờ cao điểm,Đi làm nội thành,medium
```

## 12. Giao diện client theo dữ liệu

### Homepage

Hiển thị:

- Hero dự án.
- CTA hỏi AI.
- Các phân khu nổi bật.
- Tổng quan vị trí.
- Tiện ích nổi bật.
- Khoảng giá tham khảo.
- Market snapshot.
- Form nhận tư vấn.

Data dùng:

- `projects`
- `zones`
- `media_assets`
- `amenities`
- `price_histories`

### Trang chung cư

Hiển thị:

- Danh sách phân khu.
- Bộ lọc theo phong cách, giá, tiến độ, loại căn.
- So sánh nhanh các phân khu.

Data dùng:

- `zones`
- `zone_unit_type_stats`
- `media_assets`

### Trang phân khu

Hiển thị:

- Hero phân khu.
- Mô tả.
- Vị trí trong dự án.
- Danh sách tòa.
- Loại căn phổ biến.
- Khoảng giá tham khảo.
- Tiện ích gần phân khu.
- Đường đi/tuyến kết nối.
- Gallery/mặt bằng.
- CTA hỏi AI/liên hệ sale.

Data dùng:

- `zones`
- `buildings`
- `zone_unit_type_stats`
- `amenities`
- `transport_routes`
- `media_assets`
- `sales_policies`

### Trang tòa

Hiển thị:

- Mô tả tòa.
- Vị trí tòa.
- Loại căn phổ biến.
- Khoảng diện tích.
- Khoảng giá tham khảo.
- Tiện ích gần tòa.
- Mặt bằng tòa/loại căn.
- CTA kiểm tra quỹ căn với sale.

Data dùng:

- `buildings`
- `building_unit_type_stats`
- `amenities`
- `transport_routes`
- `media_assets`

### Trang bảng giá

Hiển thị:

- Bảng giá tham khảo theo phân khu/tòa/loại căn.
- Bộ lọc.
- Cảnh báo “giá tham khảo, cần sale xác nhận giá chốt”.
- Nút hỏi AI tính chi phí.

Data dùng:

- `zone_unit_type_stats`
- `building_unit_type_stats`
- `price_histories`

### Trang thị trường

Hiển thị:

- Biểu đồ giá theo quý/tháng.
- Biểu đồ thanh khoản nếu có.
- So sánh phân khu.
- CTA tải báo cáo/liên hệ sale.

Data dùng:

- `price_histories`

### Trang lãi suất

Hiển thị:

- Bảng lãi suất ngân hàng.
- Calculator vay.
- Ghi chú hiệu lực.

Data dùng:

- `bank_rates`

## 13. Giao diện admin theo dữ liệu

Admin dashboard cần có các module:

- Quản lý dự án.
- Quản lý phân khu.
- Quản lý tòa.
- Quản lý loại căn/thống kê loại căn.
- Quản lý giá tham khảo.
- Quản lý chính sách.
- Quản lý tiện ích.
- Quản lý tuyến đường.
- Quản lý media.
- Upload tài liệu.
- Import Excel/CSV.
- Xem log AI.

Mỗi module nên có:

- Danh sách.
- Tạo mới.
- Sửa.
- Bật/tắt hiển thị.
- Cập nhật nguồn dữ liệu.
- Cập nhật mức tin cậy.

## 14. Giao diện sales theo dữ liệu

Sales dashboard cần có:

- Lead mới.
- Chi tiết nhu cầu khách.
- Lịch sử chat.
- Phân khu/tòa khách quan tâm.
- Ngân sách.
- Mục tiêu mua.
- Timeline.
- Ghi chú nội bộ.
- Trạng thái xử lý.
- Nút gọi/nhắn khách.

Sales không cần nhập toàn bộ dữ liệu dự án nếu chưa có admin module, nhưng cần có quyền:

- Ghi chú lead.
- Cập nhật trạng thái lead.
- Gửi thông tin bổ sung cho khách.
- Báo admin nếu dữ liệu AI thiếu/sai.

## 15. Cách xử lý khi chưa có data đầy đủ

Giai đoạn đầu chưa có data cụ thể, nên làm theo chiến lược:

1. Seed data mẫu ở cấp phân khu/tòa.
2. Với giá, dùng khoảng giá tham khảo có `confidence_level`.
3. Với chính sách, chỉ nhập chính sách đã xác nhận.
4. Với tiện ích/đường đi, nhập thủ công các tuyến phổ biến trước.
5. Với media, cho phép placeholder nhưng cấu trúc phải đúng.
6. AI luôn nói rõ khi dữ liệu chỉ là tham khảo.
7. Mọi câu hỏi về căn cụ thể chuyển sale.

Mục tiêu của phase đầu không phải có data hoàn hảo, mà là có data model đúng, giao diện đúng, quy trình cập nhật đúng và AI không bịa.


export interface StatItem {
  label: string;
  value: string;
}

export interface PriceRow {
  type: string;
  area: string;
  price: string;
}

export interface BuildingItem {
  id: string;
  name: string;
  description: string;
}

export interface GalleryItem {
  title: string;
  description: string;
  image: string;
}

export interface Subdivision {
  slug: string;
  name: string;
  subtitle: string;
  group: string;
  status: string;
  heroImage: string;
  cardImage: string;
  description: string;
  highlights: string[];
  stats: StatItem[];
  pricing: PriceRow[];
  buildings: BuildingItem[];
  connectivity: string[];
  gallery: GalleryItem[];
}

const media = (folder: string, file: string) => `/media_files/phan_khu/${folder}/${file}`;

export const subdivisions: Subdivision[] = [
  {
    slug: 'the-zenpark',
    name: 'THE ZENPARK',
    subtitle: 'Nơi tĩnh tại gắn liền nhịp sống',
    group: 'The Ocean View',
    status: 'Đã bàn giao',
    heroImage: media('the-zenpark', 'the-zenpark-vinhomes-ocean-park-91720e21f93a.jpg'),
    cardImage: media('the-zenpark', 'cong-torri-the-zenpark-cf8b0f6092d3.jpg'),
    description:
      'The Zenpark là phân khu căn hộ cao cấp lấy cảm hứng từ phong cách Nhật Bản, nổi bật với cảnh quan thiền, vườn Nhật và hệ tiện ích xanh trong lòng Vinhomes Ocean Park.',
    highlights: ['Vườn Nhật nội khu', 'Không gian xanh yên tĩnh', 'Kết nối nhanh hồ Ngọc Trai', 'Đa dạng căn Studio đến 3 phòng ngủ'],
    stats: [
      { label: 'Quy mô', value: '4 tòa căn hộ' },
      { label: 'Số tầng', value: '25 - 30 tầng' },
      { label: 'Sản phẩm', value: 'Studio, 1PN, 2PN, 3PN' },
      { label: 'Phong cách', value: 'Zen Nhật Bản' },
      { label: 'Trạng thái', value: 'Đã bàn giao' },
      { label: 'Vị trí', value: 'The Ocean View' },
    ],
    pricing: [
      { type: 'Studio', area: '27 - 33m²', price: 'Liên hệ' },
      { type: '1 phòng ngủ', area: '38 - 45m²', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: '55 - 70m²', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: '80 - 100m²', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'r1-01', name: 'Tòa R1.01', description: 'Tòa căn hộ thuộc lõi cảnh quan The Zenpark.' },
      { id: 'r1-02', name: 'Tòa R1.02', description: 'Kết nối thuận tiện các tiện ích nội khu.' },
      { id: 'r1-03', name: 'Tòa R1.03', description: 'Phù hợp nhu cầu ở thực và khai thác cho thuê.' },
      { id: 'r1-05', name: 'Tòa R1.05', description: 'Không gian sống yên tĩnh, gần mảng xanh.' },
    ],
    connectivity: ['Gần vườn Nhật The Zenpark', 'Kết nối hồ Ngọc Trai', 'Thuận tiện tới Vinschool', 'Di chuyển nhanh ra các trục nội khu'],
    gallery: [
      { title: 'Cổng Torri', description: 'Biểu tượng cảnh quan phong cách Nhật.', image: media('the-zenpark', 'cong-torri-the-zenpark-cf8b0f6092d3.jpg') },
      { title: 'Vườn Nhật', description: 'Không gian thiền xanh trong nội khu.', image: media('the-zenpark', 'vuon-nhat-the-zenpark-939abca0a367.jpg') },
      { title: 'Bể bơi', description: 'Tiện ích nghỉ dưỡng cho cư dân.', image: media('the-zenpark', 'be-boi-the-zenpark-d549a286dee6.jpg') },
      { title: 'Mặt bằng', description: 'Tổng mặt bằng phân khu The Zenpark.', image: media('the-zenpark', 'tong-mat-bang-the-zenpark-dccfe8ea271a.jpg') },
    ],
  },
  {
    slug: 'the-zurich',
    name: 'THE ZURICH',
    subtitle: 'Cảm hứng Thụy Sĩ giữa trung tâm Ocean Park',
    group: 'The Metropolitan',
    status: 'Đang cập nhật',
    heroImage: media('the-zurich', 'phan-khu-the-zurich-vinhomes-ocean-park-d7d84de540c9.jpg'),
    cardImage: media('the-zurich', 'view-panorama-the-zurich-vinhomes-ocean-park-4f9d4d7b3031.jpg'),
    description:
      'The Zurich là phân khu căn hộ cao cấp thuộc The Metropolitan, phát triển theo tinh thần hiện đại, riêng tư và giàu trải nghiệm tiện ích.',
    highlights: ['Phong cách châu Âu', 'Cụm tháp đồng hồ', 'Tiện ích clubhouse', 'Vị trí trung tâm The Metropolitan'],
    stats: [
      { label: 'Quy mô', value: '3 tòa ZR1, ZR2, ZR3' },
      { label: 'Số tầng', value: 'Đang cập nhật' },
      { label: 'Sản phẩm', value: 'Studio, 1PN, 2PN, 3PN' },
      { label: 'Phong cách', value: 'Thụy Sĩ hiện đại' },
      { label: 'Trạng thái', value: 'Đang cập nhật' },
      { label: 'Vị trí', value: 'The Metropolitan' },
    ],
    pricing: [
      { type: 'Studio', area: 'Khoảng 28 - 35m²', price: 'Liên hệ' },
      { type: '1 phòng ngủ', area: 'Khoảng 38 - 50m²', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Khoảng 55 - 80m²', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Khoảng 80 - 110m²', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'zr1', name: 'Tòa ZR1', description: 'Tòa căn hộ trong cụm The Zurich.' },
      { id: 'zr2', name: 'Tòa ZR2', description: 'Mặt bằng đa dạng, phù hợp nhiều nhu cầu.' },
      { id: 'zr3', name: 'Tòa ZR3', description: 'Kết nối hệ tiện ích nội khu cao cấp.' },
    ],
    connectivity: ['Nằm trong The Metropolitan', 'Gần các trục nội khu chính', 'Kết nối tiện ích giáo dục, thương mại', 'Thuận tiện tới các phân khu trung tâm'],
    gallery: [
      { title: 'Cảnh quan', description: 'Không gian nội khu The Zurich.', image: media('the-zurich', 'canh-quan-the-zurich-vinhomes-ocean-park-ac79c28ed48c.jpg') },
      { title: 'Tháp đồng hồ', description: 'Điểm nhấn kiến trúc của phân khu.', image: media('the-zurich', 'cum-thap-ong-ho-the-zurich-vinhomes-ocean-park-f6b9dfa8cffc.jpg') },
      { title: 'Hồ cảnh quan', description: 'Không gian xanh và mặt nước nội khu.', image: media('the-zurich', 'ho-canh-quan-the-zurich-vinhomes-ocean-park-3dd2d63e6dd5.jpg') },
      { title: 'Mặt bằng', description: 'Tổng mặt bằng The Zurich.', image: media('the-zurich', 'tong-mat-bang-the-zurich-4e4714599600.jpg') },
    ],
  },
  {
    slug: 'the-beverly',
    name: 'THE BEVERLY',
    subtitle: 'Sắc sống Mỹ năng động tại The Metropolitan',
    group: 'The Metropolitan',
    status: 'Đang cập nhật',
    heroImage: media('the-beverly', 'the-beverly-vinhomes-ocean-park-background-03e5faea0807.jpg'),
    cardImage: media('the-beverly', 'the-beverly-vinhomes-ocean-park-phoi-canh-6592564b5aab.jpg'),
    description:
      'The Beverly mang phong cách Mỹ hiện đại, tập trung vào nhịp sống năng động, hệ tiện ích nội khu đa dạng và khả năng kết nối tới trung tâm đại đô thị.',
    highlights: ['Phong cách Mỹ', 'Quảng trường và đài phun nước', 'Bể bơi Santa Monica', 'Cụm tòa BE1 - BE4'],
    stats: [
      { label: 'Quy mô', value: '4 tòa BE1 - BE4' },
      { label: 'Sản phẩm', value: 'Studio, 1PN, 2PN, 3PN' },
      { label: 'Tiện ích', value: 'Bể bơi, gym, kids corner' },
      { label: 'Phong cách', value: 'Mỹ hiện đại' },
      { label: 'Trạng thái', value: 'Đang cập nhật' },
      { label: 'Vị trí', value: 'The Metropolitan' },
    ],
    pricing: [
      { type: 'Studio', area: 'Khoảng 28 - 35m²', price: 'Liên hệ' },
      { type: '1 phòng ngủ', area: 'Khoảng 38 - 50m²', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Khoảng 55 - 80m²', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Khoảng 80 - 110m²', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'be1', name: 'Tòa BE1', description: 'Tòa căn hộ thuộc cụm The Beverly.' },
      { id: 'be2', name: 'Tòa BE2', description: 'Nằm trong lõi tiện ích nội khu.' },
      { id: 'be3', name: 'Tòa BE3', description: 'Kết nối thuận tiện các khu cảnh quan.' },
      { id: 'be4', name: 'Tòa BE4', description: 'Phù hợp nhu cầu ở và đầu tư.' },
    ],
    connectivity: ['Kết nối The Metropolitan', 'Gần cụm tiện ích nội khu', 'Thuận tiện tới quảng trường trung tâm', 'Di chuyển nhanh tới các trục chính'],
    gallery: [
      { title: 'Phối cảnh', description: 'Hình ảnh tổng thể The Beverly.', image: media('the-beverly', 'the-beverly-vinhomes-ocean-park-phoi-canh-6592564b5aab.jpg') },
      { title: 'Bể bơi', description: 'Không gian nghỉ dưỡng nội khu.', image: media('the-beverly', 'be-boi-the-beverly-vinhomes-ocean-park-4b0f3829e36d.jpg') },
      { title: 'Cảnh quan', description: 'Không gian xanh trong phân khu.', image: media('the-beverly', 'canh-quan-noi-khu-the-beverly-vinhomes-ocean-park-959ba081e585.jpg') },
      { title: 'Mặt bằng', description: 'Tổng mặt bằng The Beverly.', image: media('the-beverly', 'tong-mat-bang-the-beverly-ocean-park-c812e9ca7ea1.jpg') },
    ],
  },
  {
    slug: 'the-london',
    name: 'THE LONDON',
    subtitle: 'Thanh lịch, hiện đại theo cảm hứng Anh quốc',
    group: 'The Metropolitan',
    status: 'Đang cập nhật',
    heroImage: media('the-london', 'phan-khu-the-london-vinhomes-ocean-park-f17591004dde.jpg'),
    cardImage: media('the-london', 'cac-toa-the-london-vinhomes-ocean-park-652940a7a704.jpg'),
    description:
      'The London là phân khu căn hộ lấy cảm hứng từ phong cách Anh quốc, hướng tới trải nghiệm sống thanh lịch, chỉn chu và giàu tính biểu tượng.',
    highlights: ['Kiến trúc Anh quốc', 'Sảnh lễ tân sang trọng', 'Tiện ích trong nhà', 'Kết nối lõi The Metropolitan'],
    stats: [
      { label: 'Quy mô', value: 'Cụm tòa LD' },
      { label: 'Sản phẩm', value: 'Studio, 1PN, 2PN, 3PN' },
      { label: 'Tiện ích', value: 'Gym, lounge, kids room' },
      { label: 'Phong cách', value: 'Anh quốc' },
      { label: 'Trạng thái', value: 'Đang cập nhật' },
      { label: 'Vị trí', value: 'The Metropolitan' },
    ],
    pricing: [
      { type: 'Studio', area: 'Khoảng 28 - 35m²', price: 'Liên hệ' },
      { type: '1 phòng ngủ', area: 'Khoảng 38 - 50m²', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Khoảng 55 - 80m²', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Khoảng 80 - 110m²', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'ld1', name: 'Tòa LD1', description: 'Tòa căn hộ trung tâm The London.' },
      { id: 'ld2', name: 'Tòa LD2', description: 'Kết nối các tiện ích nội khu.' },
      { id: 'ld3', name: 'Tòa LD3', description: 'Mặt bằng linh hoạt cho nhiều nhu cầu.' },
    ],
    connectivity: ['Kết nối The Metropolitan', 'Gần hệ tiện ích thương mại', 'Thuận tiện tới trường học và dịch vụ', 'Di chuyển nhanh ra trục nội khu'],
    gallery: [
      { title: 'Cụm tòa', description: 'Tổng quan các tòa The London.', image: media('the-london', 'cac-toa-the-london-vinhomes-ocean-park-b3d1459a723b.jpg') },
      { title: 'Sảnh lễ tân', description: 'Không gian đón tiếp phong cách Anh.', image: media('the-london', 'sanh-le-tan-phan-khu-london-vinhomes-ocean-park-5ff9289002ed.jpg') },
      { title: 'Phòng gym', description: 'Tiện ích vận động trong nhà.', image: media('the-london', 'phong-tap-gym-phan-khu-london-vinhomes-ocean-park-f94f140568a1.jpg') },
      { title: 'Mặt bằng', description: 'Tổng mặt bằng The London.', image: media('the-london', 'tong-mat-bang-the-london-vinhomes-ocean-park-70921c1e3d35.jpg') },
    ],
  },
  {
    slug: 'the-paris',
    name: 'THE PARIS',
    subtitle: 'Cảm hứng Paris giữa lòng Ocean Park',
    group: 'The Metropolitan',
    status: 'Đang cập nhật',
    heroImage: media('the-paris', 'the-paris-vinhomes-ocean-park-background-bfa7c9aeefa6.jpg'),
    cardImage: media('the-paris', 'phoi-canh-the-paris-vinhomes-ocean-park-56c9f027437d.jpg'),
    description:
      'The Paris phát triển theo cảm hứng Pháp, nổi bật với quảng trường, chòi nghỉ, cảnh quan nội khu và hệ tiện ích sinh hoạt đa dạng.',
    highlights: ['Cảm hứng Pháp', 'Quảng trường tháp Eiffel', 'Bể bơi và lounge', 'Cụm tòa PR'],
    stats: [
      { label: 'Quy mô', value: 'Các tòa PR' },
      { label: 'Sản phẩm', value: 'Studio, 1PN, 2PN, 3PN' },
      { label: 'Tiện ích', value: 'Gym, yoga, lounge, kids corner' },
      { label: 'Phong cách', value: 'Paris' },
      { label: 'Trạng thái', value: 'Đang cập nhật' },
      { label: 'Vị trí', value: 'The Metropolitan' },
    ],
    pricing: [
      { type: 'Studio', area: 'Khoảng 28 - 35m²', price: 'Liên hệ' },
      { type: '1 phòng ngủ', area: 'Khoảng 38 - 50m²', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Khoảng 55 - 80m²', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Khoảng 80 - 110m²', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'pr1', name: 'Tòa PR1', description: 'Tòa căn hộ thuộc The Paris.' },
      { id: 'pr2', name: 'Tòa PR2', description: 'Kết nối các tiện ích nội khu.' },
      { id: 'pr3', name: 'Tòa PR3', description: 'Mặt bằng căn hộ đa dạng.' },
      { id: 'pr5', name: 'Tòa PR5', description: 'Gần các không gian sinh hoạt cộng đồng.' },
      { id: 'pr6', name: 'Tòa PR6', description: 'Phù hợp nhu cầu ở thực và đầu tư.' },
    ],
    connectivity: ['Kết nối The Metropolitan', 'Gần quảng trường nội khu', 'Thuận tiện tới tiện ích giáo dục, thương mại', 'Di chuyển nhanh tới các phân khu lân cận'],
    gallery: [
      { title: 'Quảng trường', description: 'Điểm nhấn cảnh quan The Paris.', image: media('the-paris', 'quang-truong-thap-eiffel-the-paris-ocean-park-e6e0445b8aee.jpg') },
      { title: 'Bể bơi', description: 'Không gian nghỉ dưỡng nội khu.', image: media('the-paris', 'be-boi-the-paris-ocean-park-d9c6e8589b57.jpg') },
      { title: 'Phòng lounge', description: 'Không gian sinh hoạt cộng đồng.', image: media('the-paris', 'phong-tra-lounge-am-nhac-the-paris-vinhomes-ocean-park-4653a2f2185d.jpg') },
      { title: 'Mặt bằng', description: 'Tổng mặt bằng tiện ích The Paris.', image: media('the-paris', 'tong-mat-bang-tien-ich-phan-khu-the-paris-db017bea9c69.jpg') },
    ],
  },
  {
    slug: 'the-pavilion',
    name: 'THE PAVILION',
    subtitle: 'Không gian xanh và cảnh quan nghỉ dưỡng',
    group: 'The Ocean View',
    status: 'Đã bàn giao',
    heroImage: media('the-pavilion', 'the-pavilion-vinhomes-ocean-park-7887e8d917db.jpg'),
    cardImage: media('the-pavilion', 'the-pavilion-perspective-120d6900cb9a.jpg'),
    description:
      'The Pavilion là phân khu căn hộ thuộc The Ocean View, nổi bật với hồ cảnh quan, đảo yoga và các khoảng xanh nội khu hướng tới lối sống thư thái.',
    highlights: ['Hồ cảnh quan', 'Đảo yoga', 'Cảnh quan xanh', 'Căn hộ đa dạng diện tích'],
    stats: [
      { label: 'Quy mô', value: 'Các tòa P' },
      { label: 'Sản phẩm', value: 'Studio, 1PN, 2PN, 3PN' },
      { label: 'Tiện ích', value: 'Hồ cảnh quan, yoga, vườn nội khu' },
      { label: 'Phong cách', value: 'Sinh thái nghỉ dưỡng' },
      { label: 'Trạng thái', value: 'Đã bàn giao' },
      { label: 'Vị trí', value: 'The Ocean View' },
    ],
    pricing: [
      { type: 'Studio', area: 'Khoảng 28 - 35m²', price: 'Liên hệ' },
      { type: '1 phòng ngủ', area: 'Khoảng 38 - 50m²', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Khoảng 55 - 80m²', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Khoảng 80 - 105m²', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'p1', name: 'Tòa P1', description: 'Tòa căn hộ thuộc The Pavilion.' },
      { id: 'p2', name: 'Tòa P2', description: 'Kết nối hồ cảnh quan và tiện ích xanh.' },
      { id: 'p3', name: 'Tòa P3', description: 'Mặt bằng căn hộ linh hoạt.' },
      { id: 'p4', name: 'Tòa P4', description: 'Không gian sống gần cảnh quan nội khu.' },
    ],
    connectivity: ['Nằm trong The Ocean View', 'Gần hồ cảnh quan và đảo yoga', 'Kết nối tiện ích nội khu', 'Thuận tiện ra các trục giao thông chính'],
    gallery: [
      { title: 'Phối cảnh', description: 'Tổng quan The Pavilion.', image: media('the-pavilion', 'the-pavilion-perspective-120d6900cb9a.jpg') },
      { title: 'Hồ cảnh quan', description: 'Không gian mặt nước và đảo yoga.', image: media('the-pavilion', 'ho-canh-quan-va-ao-yoga-the-pavilion-e68ec413c7af.jpg') },
      { title: 'Cảnh quan nội khu', description: 'Mảng xanh trong phân khu.', image: media('the-pavilion', 'canh-quan-noi-khu-the-pavilion-3548354d9ff1.jpg') },
      { title: 'Mặt bằng', description: 'Tổng mặt bằng phân khu Pavilion.', image: media('the-pavilion', 'tong-mat-bang-phan-khu-pavilion-cdbf1633fed3.jpg') },
    ],
  },
  {
    slug: 'the-bayfront',
    name: 'THE BAYFRONT',
    subtitle: 'Kết nối hệ tiện ích đại đô thị',
    group: 'The Ocean View',
    status: 'Đang cập nhật',
    heroImage: media('the-bayfront', 'ocean-park-logo-background-1-cc48f8c33d52.png'),
    cardImage: media('the-bayfront', 'vincom-mega-mall-62b57b0ce3ca.jpg'),
    description:
      'The Bayfront được định vị trong hệ sinh thái tiện ích Vinhomes Ocean Park, kết nối nhanh tới VinUni, Vinschool, Vinmec, Vincom và các không gian sinh hoạt cộng đồng.',
    highlights: ['Gần hệ tiện ích lớn', 'Kết nối VinUni - Vinmec - Vincom', 'Không gian BBQ và thể thao', 'Phù hợp nhu cầu sống tiện nghi'],
    stats: [
      { label: 'Nhóm', value: 'The Ocean View' },
      { label: 'Sản phẩm', value: 'Căn hộ cao tầng' },
      { label: 'Tiện ích', value: 'Vincom, Vinmec, Vinschool' },
      { label: 'Phong cách', value: 'Đô thị tiện ích' },
      { label: 'Trạng thái', value: 'Đang cập nhật' },
      { label: 'Vị trí', value: 'Vinhomes Ocean Park' },
    ],
    pricing: [
      { type: 'Studio', area: 'Liên hệ', price: 'Liên hệ' },
      { type: '1 phòng ngủ', area: 'Liên hệ', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Liên hệ', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Liên hệ', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'overview', name: 'Tổng quan', description: 'Thông tin chi tiết sẽ được phòng kinh doanh tư vấn theo nhu cầu quan tâm.' },
    ],
    connectivity: ['Vincom Mega Mall', 'Vinmec', 'Vinschool', 'VinUni', 'Công viên gym và BBQ'],
    gallery: [
      { title: 'Vincom Mega Mall', description: 'Trung tâm mua sắm trong đại đô thị.', image: media('the-bayfront', 'vincom-mega-mall-62b57b0ce3ca.jpg') },
      { title: 'Vinmec', description: 'Dịch vụ y tế tiêu chuẩn cao.', image: media('the-bayfront', 'vinmec-768768-f73a8bbed6d1.jpg') },
      { title: 'Vinschool', description: 'Hệ thống giáo dục trong khu đô thị.', image: media('the-bayfront', 'vinschool-1-1607bc3bf1fc.jpg') },
      { title: 'Công viên gym', description: 'Không gian vận động ngoài trời.', image: media('the-bayfront', 'cong-vien-gym-768768-7684d4d2dcac.jpg') },
    ],
  },
  {
    slug: 'the-palma',
    name: 'THE PALMA',
    subtitle: 'Phân khu thuộc Lumiere Orient Pearl',
    group: 'Lumiere Orient Pearl',
    status: 'Đang cập nhật',
    heroImage: media('the-palma', 'kien-truc-mat-ngoai-the-palma-cb328b4f4057.jpg'),
    cardImage: media('the-palma', 'loi-vao-sanh-can-ho-toa-the-palma-1-53561000d1bc.jpg'),
    description:
      'The Palma thuộc Lumiere Orient Pearl, tập trung vào kiến trúc mặt ngoài hiện đại và trải nghiệm sảnh căn hộ chỉn chu, cao cấp.',
    highlights: ['Kiến trúc hiện đại', 'Sảnh căn hộ sang trọng', 'Thuộc Lumiere Orient Pearl', 'Sản phẩm cao cấp'],
    stats: [
      { label: 'Nhóm', value: 'Lumiere Orient Pearl' },
      { label: 'Sản phẩm', value: 'Căn hộ cao cấp' },
      { label: 'Tiện ích', value: 'Sảnh căn hộ, cảnh quan' },
      { label: 'Phong cách', value: 'Hiện đại' },
      { label: 'Trạng thái', value: 'Đang cập nhật' },
      { label: 'Vị trí', value: 'Ocean Park' },
    ],
    pricing: [
      { type: '1 phòng ngủ', area: 'Liên hệ', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Liên hệ', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Liên hệ', price: 'Liên hệ' },
      { type: 'Duplex', area: 'Liên hệ', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'palma-1', name: 'The Palma 1', description: 'Tòa căn hộ thuộc cụm The Palma.' },
    ],
    connectivity: ['Kết nối Lumiere Orient Pearl', 'Gần hệ tiện ích Ocean Park', 'Thuận tiện tới các trục giao thông nội khu', 'Kết nối dịch vụ giáo dục, thương mại'],
    gallery: [
      { title: 'Mặt ngoài', description: 'Kiến trúc mặt ngoài The Palma.', image: media('the-palma', 'kien-truc-mat-ngoai-the-palma-cb328b4f4057.jpg') },
      { title: 'Lối vào sảnh', description: 'Sảnh căn hộ The Palma 1.', image: media('the-palma', 'loi-vao-sanh-can-ho-toa-the-palma-1-53561000d1bc.jpg') },
    ],
  },
  {
    slug: 'the-senique-hanoi',
    name: 'THE SENIQUE HANOI',
    subtitle: 'Compound cao cấp phát triển bởi Capitaland',
    group: 'The Senique Hanoi',
    status: 'Đang cập nhật',
    heroImage: media('the-senique-hanoi', 'toa-senique-1-va-senique-2-the-senique-hanoi-1a422467e3af.jpg'),
    cardImage: media('the-senique-hanoi', 'toa-the-senique-1-background-46fe9aab7932.jpg'),
    description:
      'The Senique Hanoi hướng tới trải nghiệm sống compound cao cấp, riêng tư và đồng bộ với cụm tiện ích hồ bơi, sảnh đón, cảnh quan và tiêu chuẩn bàn giao chỉn chu.',
    highlights: ['Compound cao cấp', 'Cụm tòa Senique 1 và 2', 'Hồ bơi 50m', 'Sảnh đón và cảnh quan riêng'],
    stats: [
      { label: 'Quy mô', value: 'The Senique 1 & 2' },
      { label: 'Sản phẩm', value: '1PN, 2PN, 3PN, 4PN, Duplex' },
      { label: 'Tiện ích', value: 'Hồ bơi, sảnh đón, cảnh quan' },
      { label: 'Đơn vị', value: 'Capitaland' },
      { label: 'Trạng thái', value: 'Đang cập nhật' },
      { label: 'Vị trí', value: 'Ocean Park' },
    ],
    pricing: [
      { type: '1 phòng ngủ', area: 'Khoảng 42m²', price: 'Liên hệ' },
      { type: '2 phòng ngủ', area: 'Khoảng 53 - 81m²', price: 'Liên hệ' },
      { type: '3 phòng ngủ', area: 'Khoảng 83 - 107m²', price: 'Liên hệ' },
      { type: 'Duplex / 4PN', area: 'Liên hệ', price: 'Liên hệ' },
    ],
    buildings: [
      { id: 'senique-1', name: 'The Senique 1', description: 'Tòa căn hộ thuộc cụm compound cao cấp.' },
      { id: 'senique-2', name: 'The Senique 2', description: 'Tòa căn hộ trong cụm The Senique Hanoi.' },
    ],
    connectivity: ['Kết nối nội khu Ocean Park', 'Gần hệ tiện ích giáo dục và thương mại', 'Không gian riêng tư compound', 'Thuận tiện tới các trục chính phía Đông Hà Nội'],
    gallery: [
      { title: 'Cụm tòa', description: 'The Senique 1 và The Senique 2.', image: media('the-senique-hanoi', 'toa-senique-1-va-senique-2-the-senique-hanoi-1a422467e3af.jpg') },
      { title: 'Hồ bơi 50m', description: 'Tiện ích nghỉ dưỡng riêng.', image: media('the-senique-hanoi', 'be-boi-50m-the-senique-hanoi-1d79583670b8.jpg') },
      { title: 'Sảnh đón', description: 'Không gian đón trả khách cao cấp.', image: media('the-senique-hanoi', 'sanh-on-tra-khach-the-senique-hanoi-91ab9602cea1.jpg') },
      { title: 'Mặt bằng', description: 'Tổng mặt bằng tiện ích The Senique Hanoi.', image: media('the-senique-hanoi', 'tong-mat-bang-tien-ich-the-senique-hanoi-c4b830665c0f.jpg') },
    ],
  },
];

export function getSubdivisionBySlug(slug: string) {
  return subdivisions.find((item) => item.slug === slug);
}

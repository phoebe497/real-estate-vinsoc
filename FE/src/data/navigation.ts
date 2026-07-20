export interface NavigationItem {
  name: string;
  href: string;
  submenu?: { name: string; href: string }[];
}

export const navigationItems: NavigationItem[] = [
  { name: 'TRANG CHỦ', href: '/' },
  {
    name: 'CHUNG CƯ',
    href: '/chung-cu',
    submenu: [
      { name: 'The Sapphire', href: '/chung-cu#sapphire' },
      { name: 'The Ocean View', href: '/chung-cu#ocean-view' },
      { name: 'The Metropolitan', href: '/chung-cu#metropolitan' },
      { name: 'Masteri Waterfront', href: '/chung-cu#masteri' },
    ],
  },
  {
    name: 'PHÂN KHU',
    href: '/phan-khu',
    submenu: [
      { name: 'The Zenpark', href: '/phan-khu/the-zenpark' },
      { name: 'The Zurich', href: '/phan-khu/the-zurich' },
      { name: 'The Beverly', href: '/phan-khu/the-beverly' },
      { name: 'The London', href: '/phan-khu/the-london' },
      { name: 'The Paris', href: '/phan-khu/the-paris' },
      { name: 'The Pavilion', href: '/phan-khu/the-pavilion' },
      { name: 'The Senique Hanoi', href: '/phan-khu/the-senique-hanoi' },
    ],
  },
];

export const footerData = {
  about: {
    title: 'GIỚI THIỆU',
    items: [
      'Vinhomes Ocean Park là đại đô thị văn minh, hiện đại được quy hoạch theo mô hình sinh thái phong cách Singapore.',
      'Với điểm nhấn là hồ điều hòa rộng 24,5ha và biển hồ giữa lòng thành phố, Vinhomes Ocean Park được ví như một thành phố Đại dương thu nhỏ.',
    ],
  },
  contact: {
    title: 'LIÊN HỆ PHÒNG KINH DOANH',
    items: [
      { label: 'Hotline', value: '0946.666.086' },
      { label: 'Email', value: 'vinhomeoceanpark.hn@gmail.com' },
      { label: 'Địa chỉ', value: 'Vinhomes Ocean Park, Gia Lâm, Hà Nội' },
    ],
  },
};

export const homePageData = {
  heroSlider: [
    {
      id: 1,
      heading: 'MỞ BÁN MASTERI GRAND COAST',
      subheading: 'GIẢ GỐC TRỰC TIẾP CĐT',
      ctaText: 'Xem chi tiết',
      ctaLink: '/chung-cu#masteri',
      image: '/media_files/trang-chu_chung_cu/masteri-waterfront-a5cdd3d2ac12.jpg',
    },
    {
      id: 2,
      heading: 'MỞ BÁN MASTERI OCEAN PARK 3',
      subheading: 'MASTERI ERA LANDMARK - TRỰC TIẾP CĐT',
      ctaText: 'Xem chi tiết',
      ctaLink: '/phan-khu',
      image: '/media_files/trang-chu_chung_cu/the-metropolitan-vinhomes-ocean-park-64cb319d14e4.jpg',
    },
  ],
  projectIntro: {
    heading: 'VINHOMES OCEAN PARK',
    paragraphs: [
      'Vinhomes Ocean Park là dự án Đại đô thị văn minh, hiện đại được quy hoạch theo mô hình sinh thái phong cách Singapore. Với điểm nhấn là hồ điều hòa rộng 24,5ha và biển hồ giữa lòng thành phố, Vinhomes Ocean Park được ví như một thành phố Đại dương thu nhỏ với hệ tiện ích lý tưởng và độc đáo.',
      'Dự án Vinhomes Ocean Park đã bắt đầu được bàn giao từ năm 2020 và đến nay đã hình thành nên một khu đô thị đẳng cấp và tiện ích bậc nhất tại Hà Nội, với:',
    ],
    bullets: [
      '41 tòa căn hộ đã bàn giao thuộc 3 phân khu: Sapphire 1, Sapphire 2, The Zenpark và Masteri Waterfront.',
      'Khoảng 3.000 căn biệt thự, liền kề, shophouse và shop thương mại dịch vụ đã được bàn giao.',
      '07 tòa căn hộ đang thi công thuộc 2 phân khu là: The Zurich và The Beverly.',
    ],
  },
  pricingData: {
    apartments: [
      { type: 'Căn Studio', area: '25 - 41m²', price: '1.8 - 2,2 tỷ' },
      { type: 'Căn 1 ngủ', area: '35 - 49m²', price: '2,3 - 2,5 tỷ' },
      { type: 'Căn 1 ngủ + 1', area: '43 - 52m²', price: '2,6 - 3,1 tỷ' },
      { type: 'Căn 2 ngủ', area: '53 - 75m²', price: '3,1 - 4,3 tỷ' },
      { type: 'Căn 2 ngủ + 1', area: '63 - 80m²', price: '3,4 - 4,8 tỷ' },
      { type: 'Căn 3 ngủ', area: '73 - 105m²', price: '4,2 - 6,1 tỷ' },
    ],
    villas: [
      { type: 'Biệt thự', area: '200 - 850m²', price: '30 - 300 tỷ' },
      { type: 'Song lập', area: '133,5 - 184m²', price: '16 - 40 tỷ' },
      { type: 'Liền kề', area: '56 - 168m²', price: '13 - 30 tỷ' },
      { type: 'Shophouse', area: '60 - 385m²', price: '16 - 100 tỷ' },
      { type: 'Shop TMDV', area: '55 - 200m²', price: '7 - 30 tỷ' },
    ],
  },
  projectOverview: {
    name: 'Vinhomes Ocean Park',
    investor: 'Vingroup',
    location: 'Xã Đa Tốn, Kiêu Kỵ, Gia Lâm, Hà Nội',
    management: 'Vinhomes',
    totalArea: '420ha',
    constructionDensity: '14,9%',
    developmentTypes: 'Chung cư cao cấp, Biệt thự, Liền kề, Shophouse, Shop TMDV',
    scale: '70 tòa căn hộ, 3.000 căn biệt thự/liền kề/shophouse',
    groundbreaking: '2018',
    handover: '2020 - nay',
    ownership: 'Sổ đỏ lâu dài',
  },
  locationDetails: {
    neighbors: [
      'Tây Bắc giáp Lý Thánh Tông',
      'Tây Nam giáp cao tốc Hà Nội - Hải Phòng',
      'Đông Bắc giáp sông Đuống',
      'Đông Nam giáp tỉnh Hưng Yên',
    ],
    connectivity: [
      'Cách Hồ Gươm 10km',
      'Cách sân bay Nội Bài 40km',
      'Liền kề cao tốc Hà Nội - Hải Phòng',
      'Kết nối trực tiếp với tuyến Metro số 1',
    ],
  },
  amenities: {
    pearlLake: {
      title: 'HỒ NGỌC TRAI 24,5ha',
      description: 'Hồ điều hòa lớn nhất Việt Nam với diện tích lên đến 24,5ha, chiều dài 2,4km. Hồ Ngọc Trai không chỉ là điểm nhấn cảnh quan độc đáo mà còn đóng vai trò quan trọng trong việc điều hòa khí hậu, tạo lập không gian sống trong lành cho cả đại đô thị.',
    },
    artificialBeach: {
      title: 'BIỂN NHÂN TẠO 6,1ha',
      description: 'Biển nhân tạo Crystal Lagoons® đầu tiên tại Việt Nam rộng 6,1ha với công nghệ lọc nước tiên tiến từ Chile. Bãi biển dài 1,5km với cát trắng và nước xanh mát quanh năm.',
    },
    entertainment: [
      'Công viên chủ đề Venesia',
      'Hồ bơi ngoài trời',
      'Khu thể thao đa năng',
      'Hệ thống an ninh 24/7',
      'Cảnh vệ chuyên nghiệp',
    ],
    services: [
      'VinUni - Đại học đẳng cấp quốc tế',
      'Vinschool - Hệ thống giáo dục chất lượng cao',
      'Vinmec - Bệnh viện đa khoa quốc tế',
      'Vincom - Trung tâm thương mại',
      'VinBus - Hệ thống xe buýt điện',
    ],
  },
};

export const chungCuData = {
  heroSlider: [
    {
      id: 1,
      heading: 'MỞ BÁN CĂN HỘ THE LONDON',
      subheading: 'BẢNG GIÁ GỐC - THỦ TỤC TRỰC TIẾP CĐT',
      ctaText: 'Xem chi tiết',
      ctaLink: '/chung-cu#london',
      image: '/media_files/trang-chu_chung_cu/phan-khu-london-vinhomes-ocean-park-716b53b1f7fe.jpg',
    },
    {
      id: 2,
      heading: 'MỞ BÁN CĂN HỘ THE PARIS',
      subheading: 'BẢNG GIÁ GỐC - THỦ TỤC TRỰC TIẾP CĐT',
      ctaText: 'Xem chi tiết',
      ctaLink: '/chung-cu#paris',
      image: '/media_files/trang-chu_chung_cu/the-paris-vinhomes-ocean-park-background-bd799df080a9.jpg',
    },
  ],
  intro: {
    heading: 'CHUNG CƯ VINHOMES OCEAN PARK',
    description: 'Hệ thống chung cư tại Vinhomes Ocean Park được xây dựng từ năm 2018, tạo nên một khu đô thị đẳng cấp và tiện ích bậc nhất tại Hà Nội. Giá căn hộ khởi điểm chỉ từ 1,3 tỷ/căn.',
  },
  pricingData: [
    { type: 'Studio', area: '25 - 41m²', price: '1,8 - 2,2 tỷ' },
    { type: '1 ngủ', area: '35 - 49m²', price: '2,1 - 2,8 tỷ' },
    { type: '1 ngủ + 1', area: '43 - 52m²', price: '2,7 - 3,7 tỷ' },
    { type: '2 ngủ', area: '53 - 75m²', price: '3,2 - 4,5 tỷ' },
    { type: '2 ngủ + 1', area: '63 - 80m²', price: '3,5 - 4,8 tỷ' },
    { type: '3 ngủ', area: '73 - 105m²', price: '4,5 - 6,5 tỷ' },
  ],
  subdivisions: {
    sapphire: {
      name: 'THE SAPPHIRE',
      subtitle: 'TÂM ĐIỂM CỦA THÀNH PHỐ BIỂN HỒ',
      description: 'Phân khu The Sapphire là tâm điểm của đại đô thị Vinhomes Ocean Park, gồm 2 phân khu Sapphire 1 và Sapphire 2 với hơn 20 tòa căn hộ.',
      buildings: '20 tòa',
      floors: '25-35 tầng',
      units: 'Khoảng 8.000 căn',
    },
    oceanView: {
      name: 'THE OCEAN VIEW',
      subtitle: 'TUYỆT TÁC NẰM VEN BỜ SÔNG ĐUỐNG',
      description: 'The Ocean View bao gồm The Zenpark, The Pavilion và The Bayfront với thiết kế đẳng cấp.',
      buildings: '21 tòa',
      floors: '25-35 tầng',
      units: 'Khoảng 10.000 căn',
    },
    metropolitan: {
      name: 'THE METROPOLITAN',
      subtitle: 'KHU CĂN HỘ CAO CẤP MỚI NHẤT',
      description: 'The Metropolitan gồm The Zurich, The Beverly, The London và The Paris.',
      buildings: '18 tòa',
      floors: '35-45 tầng',
      units: 'Khoảng 12.000 căn',
    },
    masteri: {
      name: 'MASTERI WATERFRONT',
      subtitle: 'BIỂU TƯỢNG SỐNG THƯỢNG LƯU',
      description: 'Masteri Waterfront là dòng căn hộ cao cấp nhất với vị trí trực diện hồ Ngọc Trai.',
      buildings: '7 tòa',
      floors: '35-40 tầng',
      units: 'Khoảng 3.000 căn',
    },
  },
};

export const subProjectData = {
  name: 'THE ZENPARK',
  subtitle: 'NƠI TĨNH TẠI GẮN LIỀN NHỊP SỐNG',
  description: 'The Zenpark - Phân khu căn hộ cao cấp với thiết kế Zen-inspired.',
  stats: {
    buildingCount: '8 tòa tháp',
    floors: '25-30 tầng',
    totalUnits: 'Khoảng 3.200 căn',
    greenArea: '70% diện tích',
    layouts: 'Studio, 1BR, 2BR, 3BR',
    status: 'Đã bàn giao',
  },
};

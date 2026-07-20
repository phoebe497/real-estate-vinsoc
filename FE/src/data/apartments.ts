export interface ApartmentOverviewItem {
  label: string;
  value: string;
}

export interface ApartmentPriceRow {
  type: string;
  area: string;
  price: string;
}

export interface ApartmentLayout {
  title: string;
  image: string;
}

export interface Apartment {
  slug: string;
  name: string;
  subtitle: string;
  heroImage: string;
  description: string;
  location: string;
  overview: ApartmentOverviewItem[];
  priceTable: ApartmentPriceRow[];
  layouts: ApartmentLayout[];
  gallery: string[];
  policy?: string[];
}

const defaultOverview: ApartmentOverviewItem[] = [
  { label: "Loai hinh", value: "Can ho cao tang" },
  { label: "San pham", value: "Studio, 1PN, 2PN, 3PN" },
  { label: "Dien tich", value: "Tu 28m2 - 100m2" },
  { label: "Tinh trang", value: "Can lien he sale de cap nhat" }
];

const defaultPrices: ApartmentPriceRow[] = [
  { type: "Studio", area: "28 - 36m2", price: "Lien he" },
  { type: "1PN", area: "37 - 45m2", price: "Lien he" },
  { type: "2PN", area: "55 - 75m2", price: "Lien he" },
  { type: "3PN", area: "80 - 100m2", price: "Lien he" }
];

function makeApartment(slug: string, name: string, subtitle: string, description: string): Apartment {
  return {
    slug,
    name,
    subtitle,
    heroImage: `/images/apartments/${slug}/hero.jpg`,
    description,
    location: "Vinhomes Ocean Park, Gia Lam, Ha Noi",
    overview: defaultOverview,
    priceTable: defaultPrices,
    layouts: [
      { title: "Can Studio", image: `/images/apartments/${slug}/studio.jpg` },
      { title: "Can 2 phong ngu", image: `/images/apartments/${slug}/2pn.jpg` },
      { title: "Mat bang dien hinh", image: `/images/apartments/${slug}/layout-1.jpg` }
    ],
    gallery: [
      `/images/apartments/${slug}/gallery-1.jpg`,
      `/images/apartments/${slug}/gallery-2.jpg`,
      `/images/apartments/${slug}/gallery-3.jpg`
    ],
    policy: [
      "Ho tro tu van chinh sach ban hang theo tung thoi diem.",
      "Thong tin gia, uu dai va tinh trang san pham can duoc sale phu trach xac minh truoc khi dat coc."
    ]
  };
}

export const apartments: Apartment[] = [
  makeApartment("toa-zr1-the-zurich", "Toa ZR1", "Toa can ho thuoc The Zurich", "Toa ZR1 nam trong tieu khu The Zurich, phu hop khach hang quan tam phong cach song cao cap, ket noi tien ich va tam nhin noi khu."),
  makeApartment("toa-zr2-the-zurich", "Toa ZR2", "Toa can ho thuoc The Zurich", "Toa ZR2 duoc dinh huong la toa can ho hien dai voi mat bang linh hoat, dap ung nhu cau o thuc va dau tu cho thue."),
  makeApartment("toa-zr3-the-zurich", "Toa ZR3", "Toa can ho thuoc The Zurich", "Toa ZR3 la mot trong cac toa noi bat cua The Zurich, phu hop khach hang can khong gian song dong bo trong Ocean City."),
  makeApartment("the-zurich", "The Zurich", "Phan khu can ho cao cap tai Ocean City", "The Zurich la tieu khu can ho cao cap lay cam hung tu phong cach Thuy Sy, noi bat voi khong gian song rieng tu, hien dai va gan cac tien ich trung tam."),
  makeApartment("the-beverly", "The Beverly", "Phong cach My tai trung tam The Metropolitan", "The Beverly tap trung vao trai nghiem song nang dong, tien nghi va kha nang ket noi voi khu trung tam thuong mai, cong vien va cac truc duong noi khu."),
  makeApartment("the-london", "The London", "Cam hung kien truc Anh quoc", "The London mang sac thai thanh lich, phu hop nhom khach hang thich khong gian song hien dai, co tinh bieu tuong va gan cac cum tien ich lon."),
  makeApartment("the-paris", "The Paris", "Can ho phong cach Paris", "The Paris la tieu khu can ho voi he tien ich noi khu va canh quan lay cam hung tu thanh pho Paris, phu hop nhu cau o va khai thac cho thue."),
  makeApartment("lumiere-orient-pearl", "Lumiere Orient Pearl", "Can ho cao cap phat trien boi Masterise Homes", "Lumiere Orient Pearl la cum can ho cao cap voi ngon ngu thiet ke sang trong, huong toi nhom khach hang can san pham hoan thien va dich vu tot."),
  makeApartment("the-metropolitan", "The Metropolitan", "Quan trung tam cua Ocean City", "The Metropolitan gom nhieu tieu khu can ho cao cap, nam tai vi tri trung tam, ket noi tien ich thuong mai, giao thong va canh quan noi khu."),
  makeApartment("the-ocean-view", "The Ocean View", "Cum can ho huong tam nhin bien ho", "The Ocean View la phan khu chung cu gan cac khong gian mat nuoc, cong vien va tien ich noi khu, phu hop khach hang uu tien moi truong song khoang dat."),
  makeApartment("the-sapphire", "The Sapphire", "Phan khu can ho hien dai, da ban giao", "The Sapphire la phan khu can ho duoc nhieu cu dan lua chon nho tinh thanh khoan, mat bang da dang va he tien ich da hinh thanh."),
  makeApartment("masteri-waterfront", "Masteri Waterfront", "Can ho hang sang ben ho trung tam", "Masteri Waterfront la du an can ho cao cap trong dai do thi, co loi the vi tri gan ho, thiet ke hien dai va he tien ich noi khu rieng."),
  makeApartment("masteri-lakeside", "Masteri Lakeside", "Bo suu tap Masteri Collection tai Ocean Park", "Masteri Lakeside la phan khu can ho cao cap huong toi trai nghiem song gan mat nuoc, tien ich dong bo va tieu chuan ban giao hien dai."),
  makeApartment("the-senique-hanoi", "The Senique Hanoi", "Can ho compound cao cap", "The Senique Hanoi duoc dinh huong thanh khong gian song rieng tu, an ninh va cao cap trong long Vinhomes Ocean Park.")
];

export function getApartmentBySlug(slug: string) {
  return apartments.find((apartment) => apartment.slug === slug);
}

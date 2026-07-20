# Version 0.9.7 - Next.js Public UI Rebuild

Ngay thuc hien: 2026-07-03

## 1. Muc tieu

Phien ban nay thay the bo giao dien public cu bang bo UI moi lay folder tham chieu lam goc:

```text
D:\Python\AI Real Estate Advisor\UIRealEstate-main
```

UI tham chieu la Vite/React/Tailwind, trong khi frontend hien tai la Next.js App Router. Vi vay phuong an trien khai la port cau truc giao dien sang Next.js, sau do lap lai cac phan he thong hien co cua du an vao giao dien moi.

Muc tieu chinh:

- Giu kien truc Next.js hien tai trong `FE/`.
- Lay UI trong `UIRealEstate-main` lam goc thiet ke, khong tiep tuc "lam dep" bo UI cu.
- Chuyen UI goc sang cau truc component/data-driven cua Next.js, khong hard-code noi dung trong tung component.
- Dung anh local trong `FE/public/media_files`.
- Dong bo style public theo navy/gold cua UI tham chieu.
- Thiet ke lai chat widget cho phu hop giao dien moi, nhung giu logic API/session/lead hien co.

## 2. Pham vi da thuc hien

### 2.1. Data public sach va data-driven

File:

- `FE/src/data/public-vinhomes.ts`

Thay doi:

- Viet lai data public bang tieng Viet sach.
- Chuan hoa cac kieu du lieu:
  - `PublicStat`
  - `PublicPriceRow`
  - `PublicCard`
  - `PublicSection`
  - `PublicPageData`
- Tao data cho:
  - trang chu;
  - trang chung cu;
  - danh sach phan khu;
  - cac trang phan khu nhu The Zenpark, The London, The Paris, The Sapphire, Masteri Waterfront...
- Giu toan bo anh la local path tu:

```text
FE/public/media_files/project/...
FE/public/media_files/subzone/...
```

Ly do:

- Folder UI tham chieu co nhieu text bi loi encoding va dung anh online mau, nen khong phu hop de copy truc tiep.
- Data moi giup component render dong, de mo rong cho phan khu/toa sau nay.

### 2.2. Renderer public moi

File:

- `FE/src/components/public/static-vinhomes-page.tsx`

Thay doi:

- Dung mot renderer chung `StaticVinhomesPage` cho nhieu public page.
- Port cac block tu UI goc Vite/React sang Next.js:
  - `HeroSlider`;
  - `ProjectIntro`;
  - `PricingCards`;
  - `ProjectOverview`;
  - `LocationSection`;
  - `MasterPlanSection`;
  - `AmenitiesSection`;
  - `ServicesOverview`;
  - `LeadFormSection`;
  - `SubdivisionPage` voi detail grid, technical stats, tabs, floor plan preview va lifestyle gallery.

Ket qua:

- `/`
- `/chung-cu`
- `/phan-khu/[slug]`
- cac route static trong `/phan-khu/...`

deu co the dung chung mot ngon ngu giao dien va data layer.

### 2.3. Header, footer va navigation

Files:

- `FE/src/components/header.tsx`
- `FE/src/components/footer.tsx`
- `FE/src/data/navbar.ts`

Thay doi:

- Header moi theo style navy/gold.
- Logo text Vinhomes Ocean Park.
- Mega menu cho nhom Chung cu.
- Mobile menu.
- Giu logic customer auth:
  - hien ten khach neu da dang nhap;
  - logout;
  - link dang nhap/dang ky neu chua dang nhap.
- Footer moi dong bo voi UI public.

### 2.4. Contact form

File:

- `FE/src/components/contact-form.tsx`

Thay doi:

- Viet lai copy tieng Viet sach.
- Giu logic submit toi `POST ${API_URL}/contact`.
- Giu `subdivisionSlug` de gan lead/contact voi trang phan khu tuong ung.

### 2.5. Trang phan khu

Files:

- `FE/src/app/phan-khu/page.tsx`
- `FE/src/app/phan-khu/[slug]/page.tsx`

Thay doi:

- Trang danh sach phan khu dung card grid moi.
- Dynamic route `/phan-khu/[slug]` uu tien data static trong `subdivisionPages`.
- Neu khong co static page, route fallback sang `getSubdivision(slug)` tu backend va map API data thanh `PublicPageData`.

Luu y:

- Repo van co cac route static nhu `/phan-khu/the-zenpark/page.tsx`, `/phan-khu/the-london/page.tsx`.
- Cac route nay da goi `StaticVinhomesPage`, nen khi renderer/data moi thay doi thi giao dien moi duoc ap dung.

### 2.6. Chat widget moi

File:

- `FE/src/components/chat-widget.tsx`

Thay doi UI:

- Panel chat moi theo navy/gold.
- Header "AI Sales Assistant".
- Bubble user mau gold, bubble AI mau sang.
- Quick actions:
  - "Tu van can 2PN khoang 3-4 ty"
  - "So sanh The Zenpark va The Sapphire"
  - "Toi muon nhan bang gia moi nhat"
- Lead form compact trong chat.
- Copy tieng Viet sach.

Logic duoc giu:

- `session_id` trong localStorage.
- Guest limit 5 tin.
- Customer token khi da dang nhap.
- Goi `POST /agent/chat`.
- Mo handover form khi `trigger_handover`.
- Tao lead qua `POST /api/v1/leads`.
- Luu chat history vao payload ticket.

### 2.7. CSS public

File:

- `FE/src/app/public-vinhomes.css`

Thay doi:

- Viet lai CSS public theo token:
  - `--vh-blue`
  - `--vh-blue-dark`
  - `--vh-gold`
  - `--vh-text`
  - `--vh-muted`
- Style cho:
  - header/nav/mega menu;
  - hero;
  - section/card/table/gallery;
  - contact form;
  - footer;
  - auth pages;
  - chat widget.

### 2.8. Lam lai theo yeu cau sau feedback

Sau feedback cua user, phien ban nay duoc chinh lai theo dung huong:

```text
UIRealEstate-main = giao dien goc
C2-App-005/FE = he thong Next.js/API/auth/chat hien co can duoc lap vao giao dien goc
```

Thay doi bo sung:

- `StaticVinhomesPage` khong con la renderer marketing generic; no da duoc viet lai thanh tap hop component gan voi cau truc UI goc.
- `Header` duoc chinh thanh fixed/transparent va doi nen khi scroll, tuong tu UI goc.
- `PublicLayoutWrapper` port them `PageTabs` noi o day man hinh nhu UI goc.
- Cac trang home/chung-cu/phan-khu tiep tuc dung data he thong hien co, nhung bo cuc la bo cuc port tu UI moi.
- Cac phan thua cua UI goc duoc giu o muc vua du de user co the tu chinh/xoa tiep.

## 3. Files da thay doi

Frontend:

```text
FE/src/app/layout.tsx
FE/src/app/public-vinhomes.css
FE/src/app/phan-khu/page.tsx
FE/src/app/phan-khu/[slug]/page.tsx
FE/src/components/public-layout.tsx
FE/src/components/chat-widget.tsx
FE/src/components/contact-form.tsx
FE/src/components/footer.tsx
FE/src/components/header.tsx
FE/src/components/public/static-vinhomes-page.tsx
FE/src/data/navbar.ts
FE/src/data/public-vinhomes.ts
```

Tai lieu:

```text
docs/reports/version-0.9.7-nextjs-public-ui-rebuild.md
docs/reports/README.md
docs/PROJECT_MAP_FOR_AI_AGENTS.md
```

## 4. Kiem thu da chay

Build frontend:

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
GET http://127.0.0.1:3000/                    -> 200
GET http://127.0.0.1:3000/chung-cu            -> 200
GET http://127.0.0.1:3000/phan-khu            -> 200
GET http://127.0.0.1:3000/phan-khu/the-zenpark -> 200
```

Text render checks:

- Home render duoc `Vinhomes Ocean Park`, `Dai do thi`, `Nhan tu van`.
- Chung cu render duoc `Chung cu Vinhomes Ocean Park`, `Bang gia tham khao`, `The Zenpark`.
- The Zenpark render duoc `Can ho The Zenpark`, `Vuon Nhat`, `Bang gia tham khao`.

Sau lan lam lai theo feedback:

- `npm run build` tiep tuc pass.
- Source/build output co cac block UI port tu folder goc:
  - `op-hero-slider`
  - `op-pricing-grid`
  - `op-overview`
  - `op-floor-grid`
  - `op-page-tabs`

## 5. Gioi han va luu y

- Chua chup screenshot bang browser noi bo vi browser surface trong phien nay khong kha dung.
- Build va HTTP render da pass, nhung van nen QA thu cong tren trinh duyet that cho:
  - desktop;
  - mobile;
  - dropdown/mega menu;
  - chat open/close;
  - quick actions;
  - form contact;
  - form lead trong chat.
- Neu backend API dang tat, cac route public van render; chat/contact se can backend de submit that.
- Trang admin khong nam trong pham vi UI rebuild nay. CSS public co style chung nhung khong thay doi nghiep vu admin.

## 6. Huong dan test thu cong

Chay frontend local:

```powershell
cd FE
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Mo:

```text
http://127.0.0.1:3000
http://127.0.0.1:3000/chung-cu
http://127.0.0.1:3000/phan-khu
http://127.0.0.1:3000/phan-khu/the-zenpark
```

Can kiem tra:

1. Header sticky, mega menu va mobile menu.
2. Hero image va text khong bi tran tren mobile.
3. Card image load tu `FE/public/media_files`.
4. Bang gia scroll ngang tot tren mobile.
5. Contact form gui dung payload.
6. Chat widget:
   - guest con 5 tin;
   - quick action gui duoc message;
   - login link dung;
   - gap Sales mo form;
   - tao ticket neu backend dang chay.

## 7. Ket luan

Phien ban 0.9.7 da chuyen public UI sang bo giao dien Next.js moi, dong bo hon voi folder tham chieu nhung van giu kien truc san pham hien tai. Public pages khong con phu thuoc vao component hard-code cu, chat widget co giao dien rieng phu hop voi thiet ke moi, va cac route chinh da build/render thanh cong.

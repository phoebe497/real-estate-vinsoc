'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {
  ChevronRight,
  Phone,
  Building2,
  Layers,
  MapPin,
} from 'lucide-react';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import { chungCuData } from '@/data/navigation';

// Hero Slider for Chung Cu
function ChungCuHero() {
  const slides = chungCuData.heroSlider;

  return (
    <section className="relative h-[60vh] md:h-[75vh] overflow-hidden">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: `url(${slides[0].image})`,
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-r from-navy-900/95 via-navy-900/70 to-transparent" />
      <div className="absolute inset-0 flex items-center">
        <div className="container-custom">
          <div className="max-w-2xl">
            <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white mb-4 leading-tight animate-slideUp">
              {slides[0].heading}
            </h2>
            <p className="text-lg md:text-xl text-[#FFCF0E] font-semibold mb-8">
              {slides[0].subheading}
            </p>
            <Link
              href={slides[0].ctaLink}
              className="btn-primary inline-flex items-center gap-2 text-lg"
            >
              {slides[0].ctaText}
              <ChevronRight size={20} />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}

// Subdivision Overview
function SubdivisionOverview() {
  const images = [
    '/media_files/trang-chu_chung_cu/the-zurich-93ab80b535d4.jpg',
    '/media_files/trang-chu_chung_cu/khu-sapphire-cc8ee2ebd78e.jpg',
    '/media_files/trang-chu_chung_cu/chung-cu-vinhomes-ocean-park-36a9d7315c87.jpg',
  ];
  const [currentImage, setCurrentImage] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentImage((prev) => (prev + 1) % images.length);
    }, 4000);
    return () => clearInterval(timer);
  }, [images.length]);

  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-12 items-center">
          {/* Left Text - 40% */}
          <div className="lg:col-span-2">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-navy-900 mb-6 leading-tight">
              {chungCuData.intro.heading}
            </h1>
            <p className="text-gray-600 mb-6 leading-relaxed text-sm md:text-base">
              {chungCuData.intro.description}
            </p>
            <div className="flex items-center gap-4">
              <Link href="#pricing" className="btn-primary inline-flex items-center gap-2">
                Xem bảng giá
                <ChevronRight size={16} />
              </Link>
              <Link href="#register" className="btn-secondary inline-flex items-center gap-2">
                Đăng ký thăm nhà mẫu
                <Phone size={16} />
              </Link>
            </div>
          </div>

          {/* Right Gallery - 60% */}
          <div className="lg:col-span-3">
            <div className="relative h-[400px] rounded-2xl overflow-hidden shadow-2xl">
              {images.map((img, index) => (
                <div
                  key={index}
                  className={`absolute inset-0 transition-opacity duration-700 ${
                    index === currentImage ? 'opacity-100' : 'opacity-0'
                  }`}
                >
                  <Image
                    src={img}
                    alt={`Chung cư Vinhomes Ocean Park ${index + 1}`}
                    fill
                    className="object-cover"
                  />
                </div>
              ))}
              <div className="absolute bottom-4 left-4 flex gap-2">
                {images.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentImage(index)}
                    className={`w-2 h-2 rounded-full transition-all duration-300 ${
                      index === currentImage
                        ? 'bg-[#FFCF0E] w-6'
                        : 'bg-white/60 hover:bg-white'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Pricing Matrix
function PricingMatrix() {
  return (
    <section id="pricing" className="section-padding bg-navy-900">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-4">
            DIỆN TÍCH VÀ <span className="text-[#FFCF0E]">GIÁ BÁN</span>
          </h2>
          <p className="text-gray-400">Giá tham khảo cho các loại căn hộ tại Vinhomes Ocean Park</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full max-w-3xl mx-auto">
            <thead>
              <tr className="bg-navy-700">
                <th className="text-left px-6 py-4 text-[#FFCF0E] font-semibold">Loại căn</th>
                <th className="text-center px-6 py-4 text-[#FFCF0E] font-semibold">Diện tích</th>
                <th className="text-right px-6 py-4 text-[#FFCF0E] font-semibold">Giá bán</th>
              </tr>
            </thead>
            <tbody>
              {chungCuData.pricingData.map((item, index) => (
                <tr key={index} className="border-t border-navy-600 hover:bg-navy-800 transition-colors">
                  <td className="px-6 py-4 text-white font-medium">{item.type}</td>
                  <td className="px-6 py-4 text-center text-gray-400">{item.area}</td>
                  <td className="px-6 py-4 text-right text-[#FFCF0E] font-semibold">{item.price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="text-center mt-8">
          <Link href="#register" className="btn-primary inline-flex items-center gap-2 text-lg">
            <Phone size={20} />
            Đăng ký thăm nhà mẫu
          </Link>
        </div>
      </div>
    </section>
  );
}

// Registration Form
function RegistrationForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
    apartmentType: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Cảm ơn bạn đã đăng ký! Chúng tôi sẽ liên hệ sớm.');
    setFormData({ name: '', email: '', phone: '', message: '', apartmentType: '' });
  };

  return (
    <section id="register" className="section-padding bg-gray-100">
      <div className="container-custom">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-navy-900 mb-3">
              ĐĂNG KÝ THĂM NHÀ MẪU
            </h2>
            <p className="text-gray-600">
              Để lại thông tin, chuyên viên tư vấn sẽ liên hệ hỗ trợ bạn
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="bg-white rounded-2xl shadow-xl p-6 md:p-8"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <input
                type="text"
                placeholder="Họ và tên"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg text-navy-900 placeholder-gray-400 focus:outline-none focus:border-[#FFCF0E] focus:ring-1 focus:ring-[#FFCF0E] transition-all duration-300"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg text-navy-900 placeholder-gray-400 focus:outline-none focus:border-[#FFCF0E] focus:ring-1 focus:ring-[#FFCF0E] transition-all duration-300"
                required
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <input
                type="tel"
                placeholder="Số điện thoại"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg text-navy-900 placeholder-gray-400 focus:outline-none focus:border-[#FFCF0E] focus:ring-1 focus:ring-[#FFCF0E] transition-all duration-300"
                required
              />
              <select
                value={formData.apartmentType}
                onChange={(e) => setFormData({ ...formData, apartmentType: e.target.value })}
                className="w-full px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg text-navy-900 focus:outline-none focus:border-[#FFCF0E] focus:ring-1 focus:ring-[#FFCF0E] transition-all duration-300"
              >
                <option value="">Chọn loại căn hộ</option>
                <option value="studio">Studio (25 - 41m²)</option>
                <option value="1br">1 ngủ (35 - 49m²)</option>
                <option value="1br+">1 ngủ + 1 (43 - 52m²)</option>
                <option value="2br">2 ngủ (53 - 75m²)</option>
                <option value="2br+">2 ngủ + 1 (63 - 80m²)</option>
                <option value="3br">3 ngủ (73 - 105m²)</option>
              </select>
            </div>
            <textarea
              placeholder="Nhu cầu chi tiết"
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="w-full px-4 py-3 bg-gray-100 border border-gray-200 rounded-lg text-navy-900 placeholder-gray-400 focus:outline-none focus:border-[#FFCF0E] focus:ring-1 focus:ring-[#FFCF0E] transition-all duration-300 h-32 mb-4 resize-none"
            />
            <button
              type="submit"
              className="btn-primary w-full text-lg flex items-center justify-center gap-2"
            >
              <Phone size={20} />
              Đăng ký ngay
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}

// Subdivision Technical Profile
function TechnicalProfile() {
  const subdivisions = [
    { name: 'The Sapphire', buildings: '20 tòa', units: '~8.000 căn' },
    { name: 'The Ocean View', buildings: '21 tòa', units: '~10.000 căn' },
    { name: 'The Metropolitan', buildings: '18 tòa', units: '~12.000 căn' },
    { name: 'Masteri Waterfront', buildings: '7 tòa', units: '~3.000 căn' },
  ];

  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-navy-900 mb-8 text-center">
          TỔNG QUAN CHUNG CƯ <span className="text-[#FFCF0E]">VINHOMES OCEAN PARK</span>
        </h2>

        <div className="bg-gray-50 rounded-2xl p-6 md:p-8 mb-10">
          <p className="text-gray-600 mb-6 text-center">
            Tổng cộng <span className="text-[#FFCF0E] font-bold">66 tòa căn hộ</span> đã và đang
            được xây dựng tại Vinhomes Ocean Park
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {subdivisions.map((item, index) => (
              <div key={index} className="bg-white rounded-xl p-4 text-center shadow-md card-hover">
                <Building2 className="text-[#FFCF0E] mx-auto mb-2" size={24} />
                <h4 className="font-bold text-navy-900 text-sm md:text-base mb-1">
                  {item.name}
                </h4>
                <p className="text-gray-500 text-xs">{item.buildings}</p>
                <p className="text-gray-600 text-xs">{item.units}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// Location Map with Hotspots
function LocationMap() {
  const [activeMapPoint, setActiveMapPoint] = useState(1);
  const mapPoints = [
    {
      id: 1,
      name: 'The Sapphire',
      desc: 'Cụm căn hộ quy mô lớn tại lõi phía Tây Nam',
      href: '/chung-cu#sapphire',
      position: 'left-[35%] top-[51%]',
    },
    {
      id: 2,
      name: 'The Ocean View',
      desc: 'Cụm căn hộ phía Bắc, kết nối tầm nhìn rộng',
      href: '/phan-khu/the-zenpark',
      position: 'left-[45%] top-[22%]',
    },
    {
      id: 3,
      name: 'The Metropolitan',
      desc: 'Cụm căn hộ cao cấp phía Tây dự án',
      href: '/phan-khu/the-zurich',
      position: 'left-[19%] top-[37%]',
    },
    {
      id: 4,
      name: 'Masteri Waterfront',
      desc: 'Cụm căn hộ cao cấp gần hồ trung tâm',
      href: '/chung-cu#masteri',
      position: 'left-[43%] top-[43%]',
    },
  ];

  return (
    <section className="section-padding bg-gray-100">
      <div className="container-custom">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-navy-900 mb-8 text-center">
          VỊ TRÍ CÁC PHÂN KHU CHUNG CƯ
        </h2>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Map Visual */}
          <div className="relative h-[300px] overflow-hidden rounded-2xl bg-navy-900 shadow-lg md:h-[400px]">
            <Image
              src="/media_files/trang-chu_chung_cu/cac-phan-khu-chung-cu-vinhomes-ocean-park-cc2bbf8969bc.jpg"
              alt="Vị trí các phân khu chung cư Vinhomes Ocean Park"
              fill
              className="object-cover"
            />
            <div className="absolute inset-0 bg-navy-900/10" />
            {mapPoints.map((point) => (
              <button
                key={point.id}
                onClick={() => setActiveMapPoint(point.id)}
                className={`group absolute ${point.position} -translate-x-1/2 -translate-y-1/2 transition-all duration-300 ${
                  activeMapPoint === point.id ? 'z-20 scale-110' : 'z-10 hover:scale-105'
                }`}
              >
                <span
                  className={`flex h-11 w-11 items-center justify-center rounded-full border-2 border-white text-sm font-bold shadow-xl transition-all duration-300 ${
                    activeMapPoint === point.id
                      ? 'bg-[#FFCF0E] text-navy-900'
                      : 'bg-navy-900/85 text-white hover:bg-[#FFCF0E] hover:text-navy-900'
                  }`}
                >
                  {point.id}
                </span>
                <span className="absolute left-1/2 top-12 hidden -translate-x-1/2 whitespace-nowrap rounded bg-white/95 px-3 py-1 text-xs font-semibold text-navy-900 shadow-lg group-hover:block md:block">
                  {point.name}
                </span>
              </button>
            ))}
          </div>

          {/* Active Point Info */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            {mapPoints.map((point) => (
              <div
                key={point.id}
                className={`transition-opacity duration-300 ${
                  activeMapPoint === point.id ? 'opacity-100' : 'opacity-0 absolute'
                }`}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-[#FFCF0E] rounded-full flex items-center justify-center text-navy-900 font-bold text-xl">
                    {point.id}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-navy-900">{point.name}</h3>
                    <p className="text-gray-500 text-sm">{point.desc}</p>
                  </div>
                </div>
                <Link
                  href={point.href}
                  className="btn-primary inline-flex items-center gap-2"
                >
                  Xem chi tiết
                  <ChevronRight size={16} />
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// Subdivision Spotlights
function SubdivisionSpotlights() {
  const subdivisions = [
    {
      id: 'sapphire',
      href: '/chung-cu#sapphire',
      data: chungCuData.subdivisions.sapphire,
      image: '/media_files/trang-chu_chung_cu/khu-sapphire-cc8ee2ebd78e.jpg',
      floorPlans: [
        { type: 'Studio', area: '27 - 30m²' },
        { type: '1 ngủ', area: '35 - 40m²' },
        { type: '2 ngủ', area: '50 - 65m²' },
        { type: '3 ngủ', area: '75 - 90m²' },
      ],
    },
    {
      id: 'ocean-view',
      href: '/phan-khu/the-zenpark',
      data: chungCuData.subdivisions.oceanView,
      image: '/media_files/trang-chu_chung_cu/phoi-canh-the-ocean-view-0a3f5bb16b7b.jpg',
      floorPlans: [
        { type: 'Studio', area: '30 - 35m²' },
        { type: '1 ngủ', area: '38 - 45m²' },
        { type: '2 ngủ', area: '55 - 70m²' },
      ],
    },
    {
      id: 'metropolitan',
      href: '/phan-khu/the-zurich',
      data: chungCuData.subdivisions.metropolitan,
      image: '/media_files/trang-chu_chung_cu/the-metropolitan-vinhomes-ocean-park-64cb319d14e4.jpg',
      floorPlans: [
        { type: '1 ngủ', area: '40 - 50m²' },
        { type: '2 ngủ', area: '60 - 80m²' },
        { type: '3 ngủ', area: '85 - 105m²' },
      ],
    },
    {
      id: 'masteri',
      href: '/chung-cu#masteri',
      data: chungCuData.subdivisions.masteri,
      image: '/media_files/trang-chu_chung_cu/masteri-waterfront-a5cdd3d2ac12.jpg',
      floorPlans: [
        { type: '1 ngủ', area: '45 - 55m²' },
        { type: '2 ngủ', area: '65 - 85m²' },
        { type: '3 ngủ', area: '95 - 120m²' },
        { type: 'Duplex', area: '150 - 250m²' },
      ],
    },
  ];

  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        {subdivisions.map((sub, index) => (
          <div
            key={sub.id}
            id={sub.id}
            className={`mb-16 last:mb-0 ${index % 2 === 1 ? 'bg-gray-50 rounded-2xl p-6 md:p-10' : ''}`}
          >
            <div
              className={`grid grid-cols-1 lg:grid-cols-2 gap-8 ${index % 2 === 1 ? '' : 'items-center'}`}
            >
              {/* Image */}
              <div className={`${index % 2 === 1 ? 'order-2' : 'order-1'}`}>
                <div className="relative rounded-xl overflow-hidden shadow-lg h-[300px] md:h-[400px]">
                  <Image
                    src={sub.image}
                    alt={sub.data.name}
                    fill
                    className="object-cover"
                  />
                  <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2">
                    <p className="text-navy-900 font-bold">{sub.data.buildings}</p>
                    <p className="text-gray-500 text-xs">{sub.data.units}</p>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className={`${index % 2 === 1 ? 'order-1' : 'order-2'}`}>
                <h3 className="text-2xl md:text-3xl font-bold text-navy-900 mb-2">
                  PHÂN KHU {sub.data.name}
                </h3>
                <p className="text-[#FFCF0E] font-semibold mb-4">{sub.data.subtitle}</p>
                <p className="text-gray-600 mb-6 leading-relaxed">{sub.data.description}</p>

                {/* Floor Plans Table */}
                <div className="mb-6">
                  <h4 className="font-semibold text-navy-800 mb-3 flex items-center gap-2">
                    <Layers size={18} className="text-[#FFCF0E]" />
                    Mặt bằng căn hộ:
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {sub.floorPlans.map((plan, i) => (
                      <div key={i} className="flex justify-between items-center bg-gray-100 px-3 py-2 rounded text-sm">
                        <span className="text-navy-900 font-medium">{plan.type}</span>
                        <span className="text-gray-500">{plan.area}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <Link
                  href={sub.href}
                  className="btn-primary inline-flex items-center gap-2"
                >
                  Xem chi tiết
                  <ChevronRight size={16} />
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

// Main Component
export default function ChungCuContent() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <ChungCuHero />
        <SubdivisionOverview />
        <PricingMatrix />
        <RegistrationForm />
        <TechnicalProfile />
        <LocationMap />
        <SubdivisionSpotlights />
      </main>
      <Footer />
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {
  ChevronLeft,
  ChevronRight,
  MapPin,
  Building2,
  Waves,
  TreePine,
  Sparkles,
  GraduationCap,
  HeartPulse,
  ShoppingBag,
  Bus,
  Shield,
  Phone,
  Building,
} from 'lucide-react';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import { homePageData } from '@/data/navigation';

// Hero Slider Component
function HeroSlider() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const slides = homePageData.heroSlider;

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [slides.length]);

  return (
    <section className="relative h-[70vh] md:h-[85vh] overflow-hidden">
      {slides.map((slide, index) => (
        <div
          key={slide.id}
          className={`absolute inset-0 hero-slide ${
            index === currentSlide ? 'opacity-100 z-10' : 'opacity-0 z-0'
          }`}
        >
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url(${slide.image})` }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-navy-900/95 via-navy-900/70 to-transparent" />
          <div className="absolute inset-0 flex items-center">
            <div className="container-custom">
              <div className="max-w-2xl animate-slideUp">
                <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white mb-4 leading-tight">
                  {slide.heading}
                </h2>
                <p className="text-lg md:text-xl text-[#FFCF0E] font-semibold mb-8">
                  {slide.subheading}
                </p>
                <Link
                  href={slide.ctaLink}
                  className="btn-primary inline-flex items-center gap-2 text-lg"
                >
                  {slide.ctaText}
                  <ChevronRight size={20} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Navigation Arrows */}
      <button
        onClick={() => setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length)}
        className="absolute left-4 top-1/2 -translate-y-1/2 z-20 w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/40 transition-all duration-300"
      >
        <ChevronLeft size={24} />
      </button>
      <button
        onClick={() => setCurrentSlide((prev) => (prev + 1) % slides.length)}
        className="absolute right-4 top-1/2 -translate-y-1/2 z-20 w-12 h-12 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/40 transition-all duration-300"
      >
        <ChevronRight size={24} />
      </button>

      {/* Dots */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex gap-3">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`w-3 h-3 rounded-full transition-all duration-300 ${
              index === currentSlide ? 'bg-[#FFCF0E] w-8' : 'bg-white/50 hover:bg-white/80'
            }`}
          />
        ))}
      </div>
    </section>
  );
}

// Project Intro Section
function ProjectIntro() {
  const [currentImage, setCurrentImage] = useState(0);
  const images = [
    '/media_files/trang-chu_chung_cu/toan-canh-vinhomes-ocean-park-dfb2a557e258.jpg',
    '/media_files/trang-chu_chung_cu/khu-sapphire-cc8ee2ebd78e.jpg',
    '/media_files/trang-chu_chung_cu/khu-o-thi-vinhomes-ocean-park-3d6bad9000e7.jpg',
    '/media_files/trang-chu_chung_cu/bien-nhan-tao-7ce2acccf7b0.jpg',
  ];

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
          <div className="lg:col-span-2 animate-slideUp">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-navy-900 mb-6 leading-tight">
              {homePageData.projectIntro.heading}
            </h1>
            {homePageData.projectIntro.paragraphs.map((p, index) => (
              <p
                key={index}
                className="text-gray-600 mb-4 leading-relaxed text-sm md:text-base"
              >
                {p}
              </p>
            ))}
            <ul className="space-y-3 mt-6">
              {homePageData.projectIntro.bullets.map((bullet, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="w-2 h-2 bg-[#FFCF0E] rounded-full mt-2 flex-shrink-0" />
                  <span className="text-gray-700 text-sm md:text-base">{bullet}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Right Images - 60% */}
          <div className="lg:col-span-3">
            <div className="relative h-[400px] md:h-[500px] rounded-2xl overflow-hidden shadow-2xl">
              {images.map((img, index) => (
                <div
                  key={index}
                  className={`absolute inset-0 transition-opacity duration-700 ${
                    index === currentImage ? 'opacity-100' : 'opacity-0'
                  }`}
                >
                  <Image
                    src={img}
                    alt={`Vinhomes Ocean Park ${index + 1}`}
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

// Pricing Cards Section
function PricingCards() {
  return (
    <section className="section-padding bg-navy-900">
      <div className="container-custom">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 - Policy */}
          <div className="bg-navy-800 rounded-xl overflow-hidden card-hover">
            <div className="bg-navy-700 px-6 py-4">
              <h3 className="text-[#FFCF0E] font-bold text-lg">CHÍNH SÁCH ƯU ĐÃI</h3>
            </div>
            <div className="p-6">
              <p className="text-gray-300 mb-6 text-sm leading-relaxed">
                Chính sách bán hàng mỗi phân khu và từng giai đoạn mở bán sẽ khác nhau.
                Quý khách hàng xin vui lòng liên hệ hotline để được hỗ trợ chuyên sâu.
              </p>
              <button className="btn-primary w-full">Tư vấn chuyên sâu</button>
            </div>
          </div>

          {/* Card 2 - Apartments */}
          <div className="bg-navy-800 rounded-xl overflow-hidden card-hover">
            <div className="bg-navy-700 px-6 py-4">
              <h3 className="text-[#FFCF0E] font-bold text-lg">CHUNG CƯ</h3>
            </div>
            <div className="p-6">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-400 text-xs">
                    <th className="text-left pb-3">Loại căn</th>
                    <th className="text-center pb-3">Diện tích</th>
                    <th className="text-right pb-3">Giá</th>
                  </tr>
                </thead>
                <tbody>
                  {homePageData.pricingData.apartments.slice(0, 4).map((item, index) => (
                    <tr key={index} className="border-t border-navy-600">
                      <td className="py-2 text-white">{item.type}</td>
                      <td className="py-2 text-center text-gray-400">{item.area}</td>
                      <td className="py-2 text-right text-[#FFCF0E]">{item.price}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <Link
                href="/chung-cu"
                className="btn-primary w-full mt-4 inline-flex items-center justify-center gap-2"
              >
                Xem chi tiết khu Chung cư
                <ChevronRight size={16} />
              </Link>
            </div>
          </div>

          {/* Card 3 - Villas */}
          <div className="bg-navy-800 rounded-xl overflow-hidden card-hover">
            <div className="bg-navy-700 px-6 py-4">
              <h3 className="text-[#FFCF0E] font-bold text-lg">QUỸ CHUYỂN NHƯỢNG BIỆT THỰ</h3>
            </div>
            <div className="p-6">
              <div className="space-y-2 text-sm">
                {homePageData.pricingData.villas.map((item, index) => (
                  <div key={index} className="flex justify-between items-center py-1">
                    <span className="text-white">{item.type}</span>
                    <span className="text-gray-400 text-xs">{item.area}</span>
                    <span className="text-[#FFCF0E]">{item.price}</span>
                  </div>
                ))}
              </div>
              <p className="text-gray-500 text-xs italic mt-4 mb-4 leading-relaxed">
                * Lưu ý: Quỹ căn CĐT đã bán hết từ năm 2019, giá bán trên là giá chuyển
                nhượng và có thể thay đổi tùy theo thời điểm...
              </p>
              <Link
                href="/phan-khu"
                className="btn-primary w-full inline-flex items-center justify-center gap-2"
              >
                Xem danh sách phân khu
                <ChevronRight size={16} />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Project Overview Section
function ProjectOverview() {
  const data = homePageData.projectOverview;
  const overviewItems = [
    { label: 'Tên dự án', value: data.name },
    { label: 'Chủ đầu tư', value: data.investor },
    { label: 'Vị trí dự án', value: data.location },
    { label: 'Đơn vị quản lý', value: data.management },
    { label: 'Tổng diện tích', value: data.totalArea },
    { label: 'Mật độ xây dựng', value: data.constructionDensity },
    { label: 'Các loại hình phát triển', value: data.developmentTypes },
    { label: 'Quy mô', value: data.scale },
    { label: 'Thời gian khởi công', value: data.groundbreaking },
    { label: 'Thời gian bàn giao', value: data.handover },
    { label: 'Hình thức sở hữu', value: data.ownership },
  ];

  return (
    <section
      className="relative section-padding"
      style={{
        backgroundImage:
          'url(/media_files/trang-chu_chung_cu/toan-canh-vinhomes-ocean-park-dfb2a557e258.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="absolute inset-0 bg-navy-900/90" />
      <div className="container-custom relative z-10">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-8 text-center">
          TỔNG QUAN <span className="text-[#FFCF0E]">VINHOMES OCEAN PARK</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {overviewItems.map((item, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-sm rounded-lg p-5 border border-white/10"
            >
              <p className="text-[#FFCF0E] text-sm font-medium mb-1">{item.label}</p>
              <p className="text-white font-medium">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// Location Section
function LocationSection() {
  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* Left - Text */}
          <div>
            <h2 className="text-2xl md:text-3xl font-bold text-navy-900 mb-6">
              VỊ TRÍ <span className="text-[#FFCF0E]">VINHOMES OCEAN PARK</span>
            </h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Vinhomes Ocean Park tọa lạc tại xã Đa Tốn, Kiêu Kỵ, huyện Gia Lâm, Hà Nội.
              Vị trí chiến lược kết nối trực tiếp cao tốc Hà Nội - Hải Phòng, trung tâm
              thủ đô và các tỉnh lân cận.
            </p>
            <div className="space-y-4 mb-6">
              <h4 className="font-semibold text-navy-800 flex items-center gap-2">
                <MapPin className="text-[#FFCF0E]" size={18} />
                Vị trí địa lý:
              </h4>
              <ul className="space-y-2 ml-6">
                {homePageData.locationDetails.neighbors.map((item, index) => (
                  <li key={index} className="text-gray-600 text-sm flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-[#FFCF0E] rounded-full mt-2 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold text-navy-800 flex items-center gap-2">
                <Building2 className="text-[#FFCF0E]" size={18} />
                Kết nối giao thông:
              </h4>
              <ul className="space-y-2 ml-6">
                {homePageData.locationDetails.connectivity.map((item, index) => (
                  <li key={index} className="text-gray-600 text-sm flex items-start gap-2">
                    <span className="w-1.5 h-1.5 bg-[#FFCF0E] rounded-full mt-2 flex-shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Right - Map Placeholder */}
          <div className="relative">
            <div className="h-[400px] lg:h-full bg-gray-200 rounded-xl overflow-hidden shadow-lg">
              <iframe
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d14899.826572628477!2d105.93724121333123!3d20.99437502366235!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135af4a6ec55c7d%3A0xad450dcc7630508c!2zVmluaG9tZXMgT2NlYW4gUGFyaywgR2lhIEzDom0sIEjDoCBO4buZaSwgVmnhu4d0IE5hbQ!5e0!3m2!1svi!2s!4v1783146142349!5m2!1svi!2s"
                width="100%"
                height="100%"
                style={{ border: 0 }}
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                title="Vinhomes Ocean Park Location"
              />
            </div>
            <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-4">
              <div className="flex items-center gap-2">
                <MapPin className="text-[#FFCF0E]" size={20} />
                <div>
                  <p className="font-semibold text-navy-900 text-sm">Vinhomes Ocean Park</p>
                  <p className="text-gray-500 text-xs">Gia Lâm, Hà Nội</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Master Plan Section
function MasterPlanSection() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-navy-900 mb-4">
            TỔNG MẶT BẰNG <span className="text-[#FFCF0E]">DỰ ÁN</span>
          </h2>
          <p className="text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Với tổng diện tích 420ha, Vinhomes Ocean Park được mệnh danh là &quot;Quận
            Ocean&quot; - đại đô thị văn minh, hiện đại theo mô hình Singapore, bao gồm
            khu căn hộ cao tầng, khu biệt thự ven hồ, khu shophouse và hệ tiện ích
            quốc tế đẳng cấp.
          </p>
        </div>

        {/* Master Plan Image */}
        <div className="relative rounded-2xl overflow-hidden shadow-2xl">
          <div className="relative h-[400px] md:h-[600px]">
            <Image
              src="/media_files/trang-chu_chung_cu/tong-mat-bang-vinhomes-ocean-park-158f3f494941.jpg"
              alt="Tổng mặt bằng Vinhomes Ocean Park"
              fill
              className="object-cover"
            />
          </div>
          <div className="absolute inset-0 bg-gradient-to-t from-navy-900/80 via-transparent to-transparent" />

          {/* Legend */}
          <div className="absolute bottom-6 left-6 right-6 md:right-auto">
            <div className="bg-white/95 backdrop-blur-sm rounded-xl p-6 shadow-xl max-w-md">
              <h4 className="font-bold text-navy-900 mb-4">Phân khu chính:</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-500 rounded" />
                  <span className="text-gray-700">Khu căn hộ cao tầng</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded" />
                  <span className="text-gray-700">Khu biệt thự ven hồ</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-[#FFCF0E] rounded" />
                  <span className="text-gray-700">Khu Shophouse</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-cyan-400 rounded" />
                  <span className="text-gray-700">Hồ điều hòa 24,5ha</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Amenities Section - Pearl Lake & Artificial Beach
function AmenitiesSection() {
  return (
    <section className="section-padding bg-white">
      {/* Pearl Lake */}
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-16">
          <div>
            <h3 className="text-2xl md:text-3xl font-bold text-navy-900 mb-4 flex items-center gap-3">
              <Waves className="text-cyan-500" size={32} />
              {homePageData.amenities.pearlLake.title}
            </h3>
            <p className="text-gray-600 leading-relaxed">
              {homePageData.amenities.pearlLake.description}
            </p>
          </div>
          <div className="relative rounded-xl overflow-hidden shadow-xl h-[300px] md:h-[400px]">
            <Image
              src="/media_files/trang-chu_chung_cu/bai-cat-trang-ho-ngoc-trai-de4f19d707d3.jpg"
              alt="Hồ Ngọc Trai"
              fill
              className="object-cover"
            />
            <div className="absolute top-6 right-6 bg-white/90 backdrop-blur-sm rounded-lg px-4 py-2">
              <p className="text-navy-900 font-bold text-lg">24,5ha</p>
              <p className="text-gray-500 text-xs">Diện tích hồ</p>
            </div>
          </div>
        </div>
      </div>

      {/* Artificial Beach */}
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="order-2 lg:order-1 relative rounded-xl overflow-hidden shadow-xl h-[300px] md:h-[400px]">
            <Image
              src="/media_files/trang-chu_chung_cu/bien-nhan-tao-7ce2acccf7b0.jpg"
              alt="Biển nhân tạo"
              fill
              className="object-cover"
            />
            <div className="absolute top-6 left-6 bg-white/90 backdrop-blur-sm rounded-lg px-4 py-2">
              <p className="text-navy-900 font-bold text-lg">6,1ha</p>
              <p className="text-gray-500 text-xs">Biển nhân tạo Crystal Lagoons®</p>
            </div>
          </div>
          <div className="order-1 lg:order-2">
            <h3 className="text-2xl md:text-3xl font-bold text-navy-900 mb-4 flex items-center gap-3">
              <Sparkles className="text-[#FFCF0E]" size={32} />
              {homePageData.amenities.artificialBeach.title}
            </h3>
            <p className="text-gray-600 leading-relaxed">
              {homePageData.amenities.artificialBeach.description}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

// Services & Amenities Overview
function ServicesOverview() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-navy-900 text-center mb-12">
          TIỆN ÍCH VÀ DỊCH VỤ <span className="text-[#FFCF0E]">ĐẲNG CẤP</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Entertainment & Security */}
          <div className="bg-white rounded-2xl overflow-hidden shadow-lg card-hover">
            <div className="h-48 relative">
              <Image
                src="/media_files/trang-chu_chung_cu/he-thong-tien-ich-ang-cap-vinhomes-ocean-park-2c7f6e656275.jpg"
                alt="Tiện ích giải trí"
                fill
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-navy-900/80 to-transparent" />
              <h4 className="absolute bottom-4 left-6 text-white font-bold text-xl flex items-center gap-2">
                <TreePine className="text-[#FFCF0E]" />
                Tiện ích giải trí và an ninh
              </h4>
            </div>
            <div className="p-6">
              <ul className="grid grid-cols-2 gap-3">
                {homePageData.amenities.entertainment.map((item, index) => (
                  <li key={index} className="flex items-center gap-2 text-gray-600 text-sm">
                    <span className="w-1.5 h-1.5 bg-[#FFCF0E] rounded-full" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Services */}
          <div className="bg-white rounded-2xl overflow-hidden shadow-lg card-hover">
            <div className="h-48 relative">
              <Image
                src="/media_files/trang-chu_chung_cu/ket-noi-vung-vinhomes-ocean-park-2c1c095ee981.jpg"
                alt="Y tế giáo dục"
                fill
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-navy-900/80 to-transparent" />
              <h4 className="absolute bottom-4 left-6 text-white font-bold text-xl flex items-center gap-2">
                <HeartPulse className="text-[#FFCF0E]" />
                Y tế, giáo dục, mua sắm và giao thông
              </h4>
            </div>
            <div className="p-6">
              <ul className="space-y-3">
                {[
                  { icon: GraduationCap, text: 'VinUni - Đại học đẳng cấp quốc tế' },
                  { icon: Building, text: 'Vinschool - Hệ thống giáo dục chất lượng cao' },
                  { icon: HeartPulse, text: 'Vinmec - Bệnh viện đa khoa quốc tế' },
                  { icon: ShoppingBag, text: 'Vincom - Trung tâm thương mại' },
                  { icon: Bus, text: 'VinBus - Hệ thống xe buýt điện' },
                  { icon: Shield, text: 'Hệ thống an ninh 24/7' },
                ].map((item, index) => (
                  <li key={index} className="flex items-center gap-3 text-gray-600 text-sm">
                    <item.icon size={16} className="text-[#FFCF0E]" />
                    {item.text}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// Lead Form Section
function LeadForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Cảm ơn bạn đã đăng ký! Chúng tôi sẽ liên hệ sớm.');
    setFormData({ name: '', email: '', phone: '', message: '' });
  };

  return (
    <section
      className="relative section-padding"
      style={{
        backgroundImage:
          'url(/media_files/trang-chu_chung_cu/chung-cu-vinhomes-ocean-park-36a9d7315c87.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="absolute inset-0 bg-navy-900/95" />
      <div className="container-custom relative z-10">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-3">
              ĐĂNG KÝ NHẬN THÔNG TIN DỰ ÁN
            </h2>
            <p className="text-gray-300 text-sm md:text-base">
              (Bảng giá gốc, chính sách chiết khấu, vay vốn 0%, thăm quan nhà mẫu và tư
              vấn chuyên sâu)
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="bg-navy-800/50 backdrop-blur-sm rounded-2xl p-6 md:p-8 border border-white/10"
          >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <input
                type="text"
                placeholder="Họ và tên"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="form-input"
                required
              />
              <input
                type="tel"
                placeholder="Số điện thoại"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="form-input"
                required
              />
            </div>
            <textarea
              placeholder="Nhu cầu chi tiết"
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="form-input h-32 mb-4 resize-none"
            />
            <button
              type="submit"
              className="btn-primary w-full text-lg flex items-center justify-center gap-2"
            >
              <Phone size={20} />
              Gửi ngay
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}

// Main HomePage Component
export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <HeroSlider />
        <ProjectIntro />
        <PricingCards />
        <ProjectOverview />
        <LocationSection />
        <MasterPlanSection />
        <AmenitiesSection />
        <ServicesOverview />
        <LeadForm />
      </main>
      <Footer />
    </div>
  );
}

'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  Award,
  Building,
  Building2,
  Calendar,
  ChevronRight,
  Home,
  Layers,
  MapPin,
  Phone,
  SquareIcon,
  TreePine,
} from 'lucide-react';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import type { Subdivision } from '@/data/subdivisions';

const statIcons = [Building2, Layers, Home, TreePine, SquareIcon, Calendar];

export default function SubdivisionDetail({ subdivision }: { subdivision: Subdivision }) {
  const [activeBuilding, setActiveBuilding] = useState(subdivision.buildings[0]?.id ?? '');
  const activeBuildingData =
    subdivision.buildings.find((item) => item.id === activeBuilding) ?? subdivision.buildings[0];

  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <section className="relative h-[70vh] overflow-hidden">
          <Image
            src={subdivision.heroImage}
            alt={subdivision.name}
            fill
            priority
            className="object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-navy-900/80 via-navy-900/45 to-navy-900/95" />
          <div className="absolute inset-0 flex flex-col justify-end">
            <div className="container-custom pb-12">
              <nav className="mb-4 flex items-center gap-2 text-sm text-white/80">
                <Link href="/" className="hover:text-[#FFCF0E] transition-colors">
                  Trang chủ
                </Link>
                <ChevronRight size={14} />
                <Link href="/chung-cu" className="hover:text-[#FFCF0E] transition-colors">
                  Chung cư
                </Link>
                <ChevronRight size={14} />
                <Link href="/phan-khu" className="hover:text-[#FFCF0E] transition-colors">
                  Phân khu
                </Link>
                <ChevronRight size={14} />
                <span className="text-[#FFCF0E]">{subdivision.name}</span>
              </nav>

              <p className="mb-3 inline-flex rounded bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[#FFCF0E] backdrop-blur-sm">
                {subdivision.group}
              </p>
              <h1 className="mb-3 text-4xl font-bold text-white md:text-5xl lg:text-6xl">
                {subdivision.name}
              </h1>
              <p className="text-lg font-semibold text-[#FFCF0E] md:text-xl">
                {subdivision.subtitle}
              </p>

              <div className="mt-6 flex flex-wrap gap-4">
                {subdivision.stats.slice(0, 3).map((item) => (
                  <div key={item.label} className="rounded-lg bg-white/10 px-4 py-2 backdrop-blur-sm">
                    <p className="font-bold text-[#FFCF0E]">{item.value}</p>
                    <p className="text-xs text-white/80">{item.label}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="py-12 bg-gray-50">
          <div className="container-custom">
            <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
              <div className="rounded-2xl bg-navy-900 p-6 md:p-8">
                <h2 className="mb-4 text-2xl font-bold text-white">
                  TỔNG QUAN <span className="text-[#FFCF0E]">PHÂN KHU</span>
                </h2>
                <p className="mb-6 text-sm leading-relaxed text-gray-300 md:text-base">
                  {subdivision.description}
                </p>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {subdivision.highlights.map((item) => (
                    <div key={item} className="flex items-start gap-3 rounded-lg bg-navy-800 p-3">
                      <Award className="mt-0.5 flex-shrink-0 text-[#FFCF0E]" size={18} />
                      <span className="text-sm text-white">{item}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-6 rounded-lg bg-navy-800 p-4">
                  <p className="text-sm text-gray-400">
                    * Giá bán và chính sách ưu đãi có thể thay đổi theo từng thời điểm.
                    Vui lòng liên hệ phòng kinh doanh để được tư vấn bảng giá mới nhất.
                  </p>
                </div>
              </div>

              <div className="rounded-2xl bg-white p-6 shadow-lg md:p-8">
                <h3 className="mb-6 text-xl font-bold text-navy-900">DIỆN TÍCH & GIÁ BÁN</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-gray-200">
                        <th className="pb-3 text-left font-medium text-gray-600">Loại căn</th>
                        <th className="pb-3 text-center font-medium text-gray-600">Diện tích</th>
                        <th className="pb-3 text-right font-medium text-gray-600">Giá bán</th>
                      </tr>
                    </thead>
                    <tbody>
                      {subdivision.pricing.map((item) => (
                        <tr key={item.type} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                          <td className="py-3 font-medium text-navy-900">{item.type}</td>
                          <td className="py-3 text-center text-gray-500">{item.area}</td>
                          <td className="py-3 text-right font-semibold text-[#b39009]">{item.price}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <Link href="#register" className="btn-primary mt-6 inline-flex w-full items-center justify-center gap-2">
                  <Phone size={18} />
                  Đăng ký tư vấn
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="py-12 bg-white">
          <div className="container-custom">
            <h2 className="mb-8 text-center text-2xl font-bold text-navy-900 md:text-3xl">
              THÔNG SỐ <span className="text-[#FFCF0E]">PHÂN KHU</span>
            </h2>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
              {subdivision.stats.map((item, index) => {
                const Icon = statIcons[index % statIcons.length];
                return (
                  <div key={item.label} className="card-hover rounded-xl bg-gray-50 p-4 text-center">
                    <Icon className="mx-auto mb-2 text-[#FFCF0E]" size={24} />
                    <p className="mb-1 text-xs text-gray-500">{item.label}</p>
                    <p className="text-sm font-semibold text-navy-900">{item.value}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="py-12 bg-gray-100">
          <div className="container-custom">
            <h2 className="mb-8 text-2xl font-bold text-navy-900 md:text-3xl">
              VỊ TRÍ VÀ KẾT NỐI
            </h2>
            <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
              <div className="relative h-[350px] overflow-hidden rounded-2xl bg-navy-900 shadow-lg">
                <Image src={subdivision.cardImage} alt={`${subdivision.name} vị trí`} fill className="object-cover opacity-55" />
                <div className="absolute inset-0 bg-navy-900/40" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <MapPin className="mx-auto mb-3 text-[#FFCF0E]" size={42} />
                    <p className="text-xl font-bold text-white">{subdivision.name}</p>
                    <p className="text-sm text-gray-300">{subdivision.group}</p>
                  </div>
                </div>
              </div>
              <div className="rounded-2xl bg-white p-6 shadow-lg">
                <h3 className="mb-4 font-semibold text-navy-900">
                  Kết nối giao thông & tiện ích lân cận
                </h3>
                <div className="space-y-3">
                  {subdivision.connectivity.map((item) => (
                    <div key={item} className="flex items-center gap-3">
                      <div className="h-2 w-2 rounded-full bg-[#FFCF0E]" />
                      <span className="text-sm text-gray-600">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-12 bg-white">
          <div className="container-custom">
            <h2 className="mb-8 text-2xl font-bold text-navy-900 md:text-3xl">
              MẶT BẰNG CÁC TÒA
            </h2>
            <div className="mb-8 flex flex-wrap gap-2 border-b border-gray-200 pb-4">
              {subdivision.buildings.map((building) => (
                <button
                  key={building.id}
                  onClick={() => setActiveBuilding(building.id)}
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-all duration-300 ${
                    activeBuilding === building.id
                      ? 'bg-[#FFCF0E] text-navy-900'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {building.name}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
              <div className="rounded-2xl bg-gray-50 p-6">
                <h3 className="mb-3 text-xl font-bold text-navy-900">{activeBuildingData?.name}</h3>
                <p className="text-gray-600">{activeBuildingData?.description}</p>
                <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
                  {subdivision.pricing.slice(0, 4).map((item) => (
                    <div key={item.type} className="rounded-lg bg-white px-4 py-3 shadow-sm">
                      <p className="font-medium text-navy-900">{item.type}</p>
                      <p className="text-sm text-gray-500">{item.area}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="relative h-[350px] overflow-hidden rounded-xl bg-gray-100">
                <Image src={subdivision.gallery[0]?.image ?? subdivision.cardImage} alt={subdivision.name} fill className="object-cover" />
                <div className="absolute bottom-4 left-4 right-4 rounded-lg bg-white/90 p-3 backdrop-blur-sm">
                  <p className="font-semibold text-navy-900">{subdivision.name}</p>
                  <p className="text-sm text-gray-500">Mặt bằng tham khảo, vui lòng liên hệ để nhận bản cập nhật chi tiết.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-12 bg-gray-50">
          <div className="container-custom">
            <h2 className="mb-8 text-2xl font-bold text-navy-900 md:text-3xl">
              TIỆN ÍCH & KHÔNG GIAN SỐNG
            </h2>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
              {subdivision.gallery.map((item) => (
                <article key={item.title} className="card-hover overflow-hidden rounded-xl bg-white shadow-lg">
                  <div className="relative h-44">
                    <Image src={item.image} alt={item.title} fill className="object-cover" />
                  </div>
                  <div className="p-4">
                    <h3 className="mb-1 font-semibold text-navy-900">{item.title}</h3>
                    <p className="text-sm text-gray-500">{item.description}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="register" className="py-12 bg-navy-900">
          <div className="container-custom">
            <div className="mx-auto max-w-2xl">
              <div className="mb-8 text-center">
                <h2 className="mb-3 text-2xl font-bold text-white md:text-3xl">
                  ĐĂNG KÝ NHẬN THÔNG TIN {subdivision.name}
                </h2>
                <p className="text-gray-400">
                  Để lại thông tin, chuyên viên tư vấn sẽ liên hệ hỗ trợ bạn tận tâm
                </p>
              </div>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  alert('Cảm ơn bạn đã đăng ký! Chúng tôi sẽ liên hệ sớm.');
                }}
                className="rounded-2xl border border-white/10 bg-navy-800/50 p-6 backdrop-blur-sm"
              >
                <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                  <input type="text" placeholder="Họ và tên" className="form-input" required />
                  <input type="tel" placeholder="Số điện thoại" className="form-input" required />
                </div>
                <input type="email" placeholder="Email" className="form-input mb-4" required />
                <textarea
                  placeholder="Nhu cầu chi tiết (Loại căn, ngân sách, thời gian mua...)"
                  className="form-input mb-4 h-28 resize-none"
                />
                <button type="submit" className="btn-primary flex w-full items-center justify-center gap-2 text-lg">
                  <Phone size={20} />
                  Đăng ký ngay
                </button>
              </form>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}

'use client';

import Image from 'next/image';
import Link from 'next/link';
import { ChevronRight, Layers, MapPin, Phone } from 'lucide-react';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import { subdivisions } from '@/data/subdivisions';

export default function PhanKhuContent() {
  const featured = subdivisions[0];

  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <section className="relative h-[62vh] overflow-hidden">
          <Image
            src={featured.heroImage}
            alt="Các phân khu Vinhomes Ocean Park"
            fill
            priority
            className="object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-navy-900/95 via-navy-900/70 to-transparent" />
          <div className="absolute inset-0 flex items-center">
            <div className="container-custom">
              <div className="max-w-2xl">
                <nav className="mb-4 flex items-center gap-2 text-sm text-white/80">
                  <Link href="/" className="hover:text-[#FFCF0E] transition-colors">
                    Trang chủ
                  </Link>
                  <ChevronRight size={14} />
                  <span className="text-[#FFCF0E]">Phân khu</span>
                </nav>
                <h1 className="mb-4 text-3xl font-bold leading-tight text-white md:text-5xl lg:text-6xl">
                  CÁC PHÂN KHU CĂN HỘ
                </h1>
                <p className="mb-8 text-lg font-semibold text-[#FFCF0E] md:text-xl">
                  Vinhomes Ocean Park
                </p>
                <Link href="#subdivisions" className="btn-primary inline-flex items-center gap-2 text-lg">
                  Xem danh sách
                  <ChevronRight size={20} />
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="section-padding bg-gray-50">
          <div className="container-custom">
            <div className="grid grid-cols-1 items-center gap-8 lg:grid-cols-5 lg:gap-12">
              <div className="lg:col-span-2">
                <h2 className="mb-6 text-3xl font-bold leading-tight text-navy-900 md:text-4xl">
                  HỆ SINH THÁI PHÂN KHU CĂN HỘ
                </h2>
                <p className="mb-6 text-sm leading-relaxed text-gray-600 md:text-base">
                  Các phân khu căn hộ tại Vinhomes Ocean Park được tổ chức theo nhiều
                  cụm phong cách khác nhau, từ The Ocean View, The Metropolitan đến
                  các dòng sản phẩm cao cấp như The Senique Hanoi. Mỗi phân khu có
                  câu chuyện thiết kế, tiện ích và nhóm tòa riêng.
                </p>
                <div className="flex flex-wrap gap-3">
                  <Link href="/chung-cu" className="btn-secondary inline-flex items-center gap-2 border-navy-900/30 text-navy-900 hover:bg-navy-900 hover:text-white">
                    Tổng quan chung cư
                    <Layers size={16} />
                  </Link>
                  <Link href="#register" className="btn-primary inline-flex items-center gap-2">
                    Nhận tư vấn
                    <Phone size={16} />
                  </Link>
                </div>
              </div>
              <div className="lg:col-span-3">
                <div className="relative h-[420px] overflow-hidden rounded-2xl shadow-2xl">
                  <Image src={subdivisions[1].cardImage} alt="Phân khu căn hộ" fill className="object-cover" />
                  <div className="absolute bottom-4 left-4 rounded-lg bg-white/90 px-4 py-3 shadow-lg backdrop-blur-sm">
                    <p className="font-bold text-navy-900">{subdivisions.length} phân khu</p>
                    <p className="text-xs text-gray-500">Nhiều lựa chọn căn hộ theo từng phong cách sống</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="subdivisions" className="section-padding bg-white">
          <div className="container-custom">
            <div className="mb-12 text-center">
              <h2 className="mb-4 text-2xl font-bold text-navy-900 md:text-3xl lg:text-4xl">
                DANH SÁCH <span className="text-[#FFCF0E]">PHÂN KHU</span>
              </h2>
              <p className="mx-auto max-w-3xl text-gray-600">
                Khám phá các phân khu căn hộ nổi bật, mỗi khu sở hữu phong cách
                thiết kế, vị trí và hệ tiện ích riêng trong đại đô thị.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {subdivisions.map((item) => (
                <article key={item.slug} className="card-hover overflow-hidden rounded-2xl bg-white shadow-lg">
                  <div className="relative h-56">
                    <Image src={item.cardImage} alt={item.name} fill className="object-cover" />
                    <div className="absolute inset-0 bg-gradient-to-t from-navy-900/85 via-transparent to-transparent" />
                    <div className="absolute bottom-4 left-4 right-4">
                      <p className="mb-2 inline-flex rounded bg-white/15 px-3 py-1 text-xs font-semibold text-[#FFCF0E] backdrop-blur-sm">
                        {item.group}
                      </p>
                      <h3 className="text-2xl font-bold text-white">{item.name}</h3>
                    </div>
                  </div>
                  <div className="p-6">
                    <p className="mb-4 text-sm font-semibold text-[#b39009]">{item.subtitle}</p>
                    <p className="mb-5 line-clamp-3 text-sm leading-relaxed text-gray-600">
                      {item.description}
                    </p>
                    <div className="mb-5 flex items-center gap-2 text-sm text-gray-500">
                      <MapPin size={16} className="text-[#FFCF0E]" />
                      <span>{item.status}</span>
                    </div>
                    <Link href={`/phan-khu/${item.slug}`} className="btn-primary inline-flex w-full items-center justify-center gap-2">
                      Xem chi tiết
                      <ChevronRight size={16} />
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="register" className="section-padding bg-navy-900">
          <div className="container-custom">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="mb-3 text-2xl font-bold text-white md:text-3xl">
                CẦN TƯ VẤN CHỌN PHÂN KHU?
              </h2>
              <p className="mb-8 text-gray-400">
                Để lại thông tin, chuyên viên tư vấn sẽ hỗ trợ chọn phân khu phù hợp
                theo ngân sách và nhu cầu ở thực hoặc đầu tư.
              </p>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  alert('Cảm ơn bạn đã đăng ký! Chúng tôi sẽ liên hệ sớm.');
                }}
                className="rounded-2xl border border-white/10 bg-navy-800/50 p-6 text-left backdrop-blur-sm"
              >
                <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                  <input type="text" placeholder="Họ và tên" className="form-input" required />
                  <input type="tel" placeholder="Số điện thoại" className="form-input" required />
                </div>
                <input type="email" placeholder="Email" className="form-input mb-4" required />
                <textarea placeholder="Nhu cầu quan tâm" className="form-input mb-4 h-28 resize-none" />
                <button type="submit" className="btn-primary flex w-full items-center justify-center gap-2 text-lg">
                  <Phone size={20} />
                  Gửi thông tin
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

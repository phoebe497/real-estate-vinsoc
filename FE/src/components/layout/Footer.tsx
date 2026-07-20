import Link from 'next/link';
import { Phone, Mail, MapPin, Share2, Camera, Play } from 'lucide-react';
import { footerData } from '@/data/navigation';

export default function Footer() {
  return (
    <footer className="bg-navy-900 text-white">
      {/* Main Footer */}
      <div className="container-custom py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 lg:gap-16">
          {/* About Column */}
          <div>
            <h3 className="text-lg font-bold text-[#FFCF0E] mb-4 tracking-wide">
              {footerData.about.title}
            </h3>
            <div className="space-y-4">
              {footerData.about.items.map((item, index) => (
                <p key={index} className="text-gray-300 text-sm leading-relaxed">
                  {item}
                </p>
              ))}
            </div>

            {/* Social Links */}
            <div className="mt-6 flex items-center gap-4">
              <a
                href="tel:0946666086"
                className="w-10 h-10 bg-navy-700 rounded-full flex items-center justify-center hover:bg-[#FFCF0E] transition-colors duration-300 group"
              >
                <Share2 size={18} className="group-hover:text-navy-900" />
              </a>
              <a
                href="mailto:vinhomeoceanpark.hn@gmail.com"
                className="w-10 h-10 bg-navy-700 rounded-full flex items-center justify-center hover:bg-[#FFCF0E] transition-colors duration-300 group"
              >
                <Camera size={18} className="group-hover:text-navy-900" />
              </a>
              <a
                href="/phan-khu"
                className="w-10 h-10 bg-navy-700 rounded-full flex items-center justify-center hover:bg-[#FFCF0E] transition-colors duration-300 group"
              >
                <Play size={18} className="group-hover:text-navy-900" />
              </a>
            </div>
          </div>

          {/* Contact Column */}
          <div>
            <h3 className="text-lg font-bold text-[#FFCF0E] mb-4 tracking-wide">
              {footerData.contact.title}
            </h3>
            <div className="space-y-4">
              {footerData.contact.items.map((item, index) => (
                <div key={index} className="flex items-start gap-3">
                  {item.label === 'Hotline' && (
                    <Phone size={18} className="text-[#FFCF0E] mt-1 flex-shrink-0" />
                  )}
                  {item.label === 'Email' && (
                    <Mail size={18} className="text-[#FFCF0E] mt-1 flex-shrink-0" />
                  )}
                  {item.label === 'Địa chỉ' && (
                    <MapPin size={18} className="text-[#FFCF0E] mt-1 flex-shrink-0" />
                  )}
                  <div>
                    <span className="text-gray-400 text-sm block">{item.label}:</span>
                    <span className="text-white font-medium">{item.value}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Links */}
            <div className="mt-6 grid grid-cols-2 gap-3">
              <Link
                href="/"
                className="text-gray-300 hover:text-[#FFCF0E] text-sm transition-colors duration-200"
              >
                Trang chủ
              </Link>
              <Link
                href="/chung-cu"
                className="text-gray-300 hover:text-[#FFCF0E] text-sm transition-colors duration-200"
              >
                Chung cư
              </Link>
              <Link
                href="/phan-khu"
                className="text-gray-300 hover:text-[#FFCF0E] text-sm transition-colors duration-200"
              >
                Phân khu
              </Link>
              <Link
                href="/phan-khu/the-zenpark"
                className="text-gray-300 hover:text-[#FFCF0E] text-sm transition-colors duration-200"
              >
                The Zenpark
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Copyright */}
      <div className="border-t border-navy-700">
        <div className="container-custom py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-gray-400 text-sm text-center md:text-left">
              © 2024 Copyright. All rights reserved. Designed by{' '}
              <span className="text-[#FFCF0E]">005Team</span>
            </p>
            <p className="text-gray-500 text-xs">
              Website được phát triển bởi Phòng Kinh Doanh
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}

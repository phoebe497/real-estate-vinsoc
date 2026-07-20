'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronDown, Menu, X, Phone } from 'lucide-react';
import { navigationItems } from '@/data/navigation';
import Image from "next/image";

export default function Header() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setActiveDropdown(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    setIsMobileMenuOpen(false);
    setActiveDropdown(null);
  }, [pathname]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-navy-900/95 backdrop-blur-md shadow-lg py-2'
          : 'bg-transparent py-4'
      }`}
    >
      <div className="container-custom">
        <div className="flex items-center justify-between">
            {/* Logo / Avatar */}
            <Link href="/" className="flex items-center gap-3">
              <div className="flex items-center">
                <Image
                  src="/media_files/advisor-avatar.jpg"
                  alt="Advisor Avatar"
                  width={40}
                  height={40}
                  className="rounded-full object-cover"
                />

                <div className="ml-3">
                  <span className="text-white font-bold text-lg leading-tight block">
                    VINHOMES
                  </span>
                  <span className="text-[#FFCF0E] text-xs font-medium tracking-wider">
                    OCEAN PARK
                  </span>
                </div>
              </div>
            </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-1" ref={dropdownRef}>
            {navigationItems.map((item) => (
              <div
                key={item.name}
                className="relative"
                onMouseEnter={() => item.submenu && setActiveDropdown(item.name)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <Link
                  href={item.href}
                  className={`relative flex items-center gap-1 px-4 py-2 text-sm font-medium transition-colors duration-200
                    ${
                      pathname === item.href
                        ? 'text-[#FFCF0E]'
                        : 'text-white hover:text-[#FFCF0E]'
                    }`}
                >
                  {item.name}
                  {item.submenu && (
                    <ChevronDown
                      size={14}
                      className={`transition-transform duration-200 ${activeDropdown === item.name ? 'rotate-180' : ''}`}
                    />
                  )}
                  <span className={`absolute bottom-0 left-0 w-full h-0.5 bg-[#FFCF0E] transform scale-x-0 transition-transform duration-300 origin-left ${
                    pathname === item.href ? 'scale-x-100' : ''
                  }`} />
                </Link>

                {/* Dropdown Menu */}
                {item.submenu && activeDropdown === item.name && (
                  <div className="absolute top-full left-0 mt-0 w-56 bg-navy-800/95 backdrop-blur-md rounded-lg shadow-xl overflow-hidden animate-slideDown">
                    <div className="py-2">
                      {item.submenu.map((subItem) => (
                        <Link
                          key={subItem.name}
                          href={subItem.href}
                          className="block px-4 py-3 text-sm text-white hover:bg-navy-700 hover:text-[#FFCF0E] transition-colors duration-200"
                        >
                          {subItem.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </nav>

          {/* Hotline & CTA */}
          <div className="hidden lg:flex items-center gap-4">
            <a
              href="tel:0946666086"
              className="flex items-center gap-2 text-[#FFCF0E] font-semibold"
            >
              <Phone size={18} />
              <span>0946.666.086</span>
            </a>
            <button className="btn-primary">Đăng ký tư vấn</button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden text-white p-2"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="lg:hidden mt-4 pb-4 animate-slideDown">
            <nav className="flex flex-col gap-2">
              {navigationItems.map((item) => (
                <div key={item.name}>
                  <button
                    onClick={() =>
                      setActiveDropdown(activeDropdown === item.name ? null : item.name)
                    }
                    className="flex items-center justify-between w-full px-4 py-3 text-white hover:bg-navy-700 rounded-lg transition-colors duration-200"
                  >
                    <Link
                      href={item.href}
                      className={`font-medium ${
                        pathname === item.href ? 'text-[#FFCF0E]' : ''
                      }`}
                    >
                      {item.name}
                    </Link>
                    {item.submenu && (
                      <ChevronDown
                        size={14}
                        className={`transition-transform duration-200 text-[#FFCF0E] ${
                          activeDropdown === item.name ? 'rotate-180' : ''
                        }`}
                      />
                    )}
                  </button>
                  {item.submenu && activeDropdown === item.name && (
                    <div className="ml-4 mt-2 space-y-1">
                      {item.submenu.map((subItem) => (
                        <Link
                          key={subItem.name}
                          href={subItem.href}
                          className="block px-4 py-2 text-sm text-gray-300 hover:text-[#FFCF0E] transition-colors duration-200"
                        >
                          {subItem.name}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div className="pt-4 border-t border-navy-700 mt-4">
                <a
                  href="tel:0946666086"
                  className="flex items-center gap-2 px-4 py-3 text-[#FFCF0E] font-semibold"
                >
                  <Phone size={18} />
                  <span>0946.666.086</span>
                </a>
                <button className="w-full btn-primary mt-2">Đăng ký tư vấn</button>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}

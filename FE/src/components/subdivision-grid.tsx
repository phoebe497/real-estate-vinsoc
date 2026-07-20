import Image from 'next/image';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { subdivisions } from '@/data/subdivisions';

export function SubdivisionGrid({ limit }: { limit?: number }) {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
      {subdivisions.slice(0, limit ?? subdivisions.length).map((item) => (
        <article className="card-hover overflow-hidden rounded-2xl bg-white shadow-lg" key={item.slug}>
          <div className="relative h-48">
            <Image src={item.cardImage} alt={item.name} fill className="object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-navy-900/80 to-transparent" />
            <h3 className="absolute bottom-4 left-4 text-xl font-bold text-white">{item.name}</h3>
          </div>
          <div className="p-5">
            <span className="mb-3 inline-flex rounded bg-gray-100 px-3 py-1 text-xs font-semibold text-[#b39009]">
              {item.status}
            </span>
            <p className="mb-4 line-clamp-3 text-sm leading-relaxed text-gray-600">
              {item.description}
            </p>
            <Link href={`/phan-khu/${item.slug}`} className="inline-flex items-center gap-2 font-semibold text-navy-900 hover:text-[#b39009]">
              Xem chi tiết
              <ChevronRight size={16} />
            </Link>
          </div>
        </article>
      ))}
    </div>
  );
}

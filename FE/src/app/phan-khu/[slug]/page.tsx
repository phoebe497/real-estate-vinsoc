import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import SubdivisionDetail from '@/components/subdivision/SubdivisionDetail';
import { getSubdivisionBySlug, subdivisions } from '@/data/subdivisions';

interface PageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return subdivisions.map((subdivision) => ({
    slug: subdivision.slug,
  }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const subdivision = getSubdivisionBySlug(slug);

  if (!subdivision) {
    return {
      title: 'Phân khu không tồn tại - Vinhomes Ocean Park',
    };
  }

  return {
    title: `${subdivision.name} - Vinhomes Ocean Park`,
    description: subdivision.description,
  };
}

export default async function SubdivisionPage({ params }: PageProps) {
  const { slug } = await params;
  const subdivision = getSubdivisionBySlug(slug);

  if (!subdivision) {
    notFound();
  }

  return <SubdivisionDetail subdivision={subdivision} />;
}

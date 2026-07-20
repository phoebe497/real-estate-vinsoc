import type { Metadata } from 'next';
import ChungCuContent from './ChungCuContent';

export const metadata: Metadata = {
  title: 'Chung Cư Vinhomes Ocean Park - Giá từ 1,3 tỷ/căn',
  description: '66 tòa căn hộ cao cấp tại Vinhomes Ocean Park. Giá từ 1,3 tỷ/căn. The Sapphire, The Ocean View, The Metropolitan, Masteri Waterfront.',
};

export default function ChungCuPage() {
  return <ChungCuContent />;
}

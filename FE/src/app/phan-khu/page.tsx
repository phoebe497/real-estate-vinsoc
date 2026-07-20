import type { Metadata } from 'next';
import PhanKhuContent from './PhanKhuContent';

export const metadata: Metadata = {
  title: 'Phân Khu - Vinhomes Ocean Park',
  description: 'Chi tiết các phân khu căn hộ cao cấp tại Vinhomes Ocean Park.',
};

export default function PhanKhuPage() {
  return <PhanKhuContent />;
}

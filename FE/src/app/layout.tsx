import type { Metadata } from 'next';
import './globals.css';
import './admin.css';
import './admin-extra.css';
import './conversation.css';

import { ChatWidget } from '@/components/chat-widget';

export const metadata: Metadata = {
  title: 'Vinhomes Ocean Park - Đại đô thị ven hồ đẳng cấp Singapore',
  description:
    'Vinhomes Ocean Park là dự án Đại đô thị văn minh, hiện đại được quy hoạch theo mô hình sinh thái phong cách Singapore. Với hồ điều hòa 24,5ha và biển hồ giữa lòng thành phố.',
  keywords: 'Vinhomes Ocean Park, Gia Lâm, chung cư, biệt thự, căn hộ, Hà Nội',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-montserrat antialiased">
        {children}
        <ChatWidget />
      </body>
    </html>
  );
}

import { ReactNode } from 'react';
import './globals.css';

export const metadata = {
  title: 'GLIS v2.0 - Ghana Legal Intelligence System',
  description: 'Interactive dashboard for legal case analysis and document generation',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

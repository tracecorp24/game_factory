import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { ToastContainer } from '@/components/ui/ToastContainer';

export const metadata: Metadata = {
  title: 'CreativeForge Intelligence Studio v3.0 Pro',
  description: 'Production-Grade Multimodal Autonomous Game Creative Intelligence Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0a0d14] text-neutral-100 antialiased min-h-screen flex selection:bg-apple-blue/30 selection:text-white">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto relative bg-[#0a0d14]">
            {children}
          </main>
        </div>
        <ToastContainer />
      </body>
    </html>
  );
}

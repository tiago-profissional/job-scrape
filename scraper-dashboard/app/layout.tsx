import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link"; // Importe o Link para navegação sem recarregar

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Scraper Dashboard",
  description: "Monitoramento de automação e dados raspados",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-[#FFF5EA]"> {/* Adicionei a cor de fundo global */}
        
        {/* Adicione uma estrutura de navegação (nav) DENTRO do body */}
        <nav className="bg-[#191815] text-white p-4 shadow-md flex gap-6 justify-center">
          <Link href="/" className="hover:text-[#F1B435] font-semibold">Início</Link>
          <Link href="/dashboard" className="hover:text-[#F1B435] font-semibold">Dashboard</Link>
          <Link href="/tracker" className="hover:text-[#F1B435] font-semibold">Monitor do Robô</Link>
        </nav>

        {/* O conteúdo das páginas entra aqui */}
        <main className="flex-1">
          {children}
        </main>

      </body>
    </html>
  );
}
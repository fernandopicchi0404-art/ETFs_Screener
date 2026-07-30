import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "ETF Screener",
  description: "Painel de acompanhamento de ETFs e métricas fundamentais",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <Navigation />
        <main className="mx-auto max-w-[90rem] px-4 py-8">{children}</main>
      </body>
    </html>
  );
}

import Link from "next/link";

const links = [
  { href: "/", label: "Resumo ETFs" },
  { href: "/ativos", label: "Todos os Ativos" },
];

export default function Navigation() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">
            ETF Screener
          </p>
          <h1 className="text-lg font-semibold text-slate-900">Painel de Acompanhamento</h1>
        </div>
        <nav className="flex gap-2">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-brand-50 hover:text-brand-700"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

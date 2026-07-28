import { coverageColor, formatPct } from "@/lib/format";

interface MetricCardProps {
  label: string;
  value: string;
  hint?: string;
}

export function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-400">{hint}</p> : null}
    </div>
  );
}

export function CoverageBar({ value }: { value: number | null }) {
  const width = value ? Math.min(value, 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-20 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full ${coverageColor(value)}`} style={{ width: `${width}%` }} />
      </div>
      <span className="text-sm text-slate-600">{formatPct(value, 0)}</span>
    </div>
  );
}

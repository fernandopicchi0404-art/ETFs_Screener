"use client";

import {
  EtfPremises,
} from "@/lib/expectedReturn";

interface PremiseInputProps {
  value: number;
  onChange: (value: number) => void;
  ariaLabel: string;
}

/** Input numérico em %; clique não navega a linha da tabela. */
export function PremiseInput({ value, onChange, ariaLabel }: PremiseInputProps) {
  return (
    <input
      type="number"
      step="0.1"
      value={Number.isFinite(value) ? value : ""}
      aria-label={ariaLabel}
      onClick={(event) => event.stopPropagation()}
      onMouseDown={(event) => event.stopPropagation()}
      onChange={(event) => {
        const parsed = Number(event.target.value);
        if (Number.isFinite(parsed)) onChange(parsed);
      }}
      className="w-20 rounded border border-slate-300 px-2 py-1 text-right text-sm tabular-nums"
    />
  );
}

interface PremisesControlsProps {
  ticker: string;
  premises: EtfPremises;
  onChange: (next: Partial<EtfPremises>) => void;
  layout?: "inline" | "stack";
}

export function PremisesControls({
  ticker,
  premises,
  onChange,
  layout = "inline",
}: PremisesControlsProps) {
  const wrapper =
    layout === "stack" ? "flex flex-col gap-3" : "flex flex-wrap items-center gap-3";

  return (
    <div className={wrapper} onClick={(e) => e.stopPropagation()}>
      <label className="flex items-center gap-2 text-sm text-slate-600">
        <span className="whitespace-nowrap">Inflação %</span>
        <PremiseInput
          value={premises.inflationPct}
          ariaLabel={`Inflação de ${ticker}`}
          onChange={(inflationPct) => onChange({ inflationPct })}
        />
      </label>
      <label className="flex items-center gap-2 text-sm text-slate-600">
        <span className="whitespace-nowrap">Cresc. real %</span>
        <PremiseInput
          value={premises.realGrowthPct}
          ariaLabel={`Crescimento real de ${ticker}`}
          onChange={(realGrowthPct) => onChange({ realGrowthPct })}
        />
      </label>
    </div>
  );
}

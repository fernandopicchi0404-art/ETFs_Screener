import EtfListClient from "@/components/EtfListClient";
import { listEtfSummaries, listRegions } from "@/lib/queries";

export const dynamic = "force-dynamic";

export default function HomePage() {
  const etfs = listEtfSummaries();
  const regions = listRegions();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Resumo dos ETFs</h2>
        <p className="mt-1 text-slate-600">
          Compare ROE, earnings yield e dividend yield dos ETFs do universo curado.
        </p>
      </div>
      <EtfListClient initialEtfs={etfs} regions={regions} />
    </div>
  );
}

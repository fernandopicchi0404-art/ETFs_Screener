import EtfListClient from "@/components/EtfListClient";
import { getEtfs, getRegions } from "@/lib/api";

export default async function HomePage() {
  const [etfs, regionsData] = await Promise.all([
    getEtfs().catch(() => []),
    getRegions().catch(() => ({ regions: [] })),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Resumo dos ETFs</h2>
        <p className="mt-1 text-slate-600">
          Compare ROE, earnings yield e dividend yield dos ETFs do universo curado.
        </p>
      </div>
      <EtfListClient initialEtfs={etfs} regions={regionsData.regions} />
    </div>
  );
}

import AssetListClient from "@/components/AssetListClient";
import { getAssets, getSectors } from "@/lib/api";

export default async function AssetsPage() {
  const [assets, sectorsData] = await Promise.all([
    getAssets().catch(() => []),
    getSectors().catch(() => ({ sectors: [] })),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Todos os Ativos</h2>
        <p className="mt-1 text-slate-600">
          Lista alfabética de empresas com métricas fundamentais coletadas.
        </p>
      </div>
      <AssetListClient initialAssets={assets} sectors={sectorsData.sectors} />
    </div>
  );
}

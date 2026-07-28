import AssetListClient from "@/components/AssetListClient";
import { listAssets, listSectors } from "@/lib/queries";

export const dynamic = "force-dynamic";

export default function AssetsPage() {
  const assets = listAssets();
  const sectors = listSectors();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">Todos os Ativos</h2>
        <p className="mt-1 text-slate-600">
          Lista alfabética de empresas com métricas fundamentais coletadas.
        </p>
      </div>
      <AssetListClient initialAssets={assets} sectors={sectors} />
    </div>
  );
}

import { NextResponse } from "next/server";
import { getEtfDetail } from "@/lib/queries";

export const dynamic = "force-dynamic";

export async function GET(
  _request: Request,
  context: { params: Promise<{ ticker: string }> },
) {
  const { ticker } = await context.params;
  const etf = getEtfDetail(ticker);
  if (!etf) {
    return NextResponse.json({ detail: `ETF não encontrado: ${ticker}` }, { status: 404 });
  }
  return NextResponse.json(etf);
}

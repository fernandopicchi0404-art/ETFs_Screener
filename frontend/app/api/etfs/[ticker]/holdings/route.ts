import { NextRequest, NextResponse } from "next/server";
import { listEtfHoldings } from "@/lib/queries";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ ticker: string }> },
) {
  const { ticker } = await context.params;
  const { searchParams } = request.nextUrl;
  const all = searchParams.get("all") === "true";
  const limitParam = searchParams.get("limit");
  const limit = all ? null : limitParam ? Number(limitParam) : 10;
  return NextResponse.json(listEtfHoldings(ticker, limit));
}

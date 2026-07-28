import { NextRequest, NextResponse } from "next/server";
import { listEtfSummaries } from "@/lib/queries";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const data = listEtfSummaries({
    region: searchParams.get("region") ?? undefined,
    priority: searchParams.get("priority") ?? undefined,
    search: searchParams.get("search") ?? undefined,
    sortBy: searchParams.get("sort_by") ?? searchParams.get("sortBy") ?? "ticker",
    sortDir: searchParams.get("sort_dir") ?? searchParams.get("sortDir") ?? "asc",
  });
  return NextResponse.json(data);
}

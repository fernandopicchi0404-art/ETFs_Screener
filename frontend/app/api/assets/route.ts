import { NextRequest, NextResponse } from "next/server";
import { listAssets } from "@/lib/queries";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const data = listAssets({
    country: searchParams.get("country") ?? undefined,
    sector: searchParams.get("sector") ?? undefined,
    quality: searchParams.get("quality") ?? undefined,
    search: searchParams.get("search") ?? undefined,
    sortBy: searchParams.get("sort_by") ?? searchParams.get("sortBy") ?? "name",
    sortDir: searchParams.get("sort_dir") ?? searchParams.get("sortDir") ?? "asc",
  });
  return NextResponse.json(data);
}

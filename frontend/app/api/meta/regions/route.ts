import { NextResponse } from "next/server";
import { listRegions } from "@/lib/queries";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({ regions: listRegions(), sectors: [] });
}

import { NextResponse } from "next/server";
import { listSectors } from "@/lib/queries";

export const dynamic = "force-dynamic";

export async function GET() {
  return NextResponse.json({ regions: [], sectors: listSectors() });
}

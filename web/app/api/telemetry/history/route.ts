/**
 * GET /api/telemetry/history?limit=120
 * Returns the last N telemetry records (default 120 ≈ 24 s at 200 ms).
 */
import { NextRequest, NextResponse } from "next/server";
import { getHistory } from "../../../lib/store";

const CORS = { "Access-Control-Allow-Origin": "*" };

export async function GET(req: NextRequest) {
  const limitParam = req.nextUrl.searchParams.get("limit");
  const limit = limitParam ? Math.min(Math.max(parseInt(limitParam, 10), 1), 600) : 120;
  const history = getHistory(limit);
  return NextResponse.json(history, { headers: CORS });
}

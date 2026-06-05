/**
 * GET /api/telemetry/latest
 * Returns the most recent telemetry record.
 */
import { NextResponse } from "next/server";
import { getLatest } from "../../../lib/store";

const CORS = { "Access-Control-Allow-Origin": "*" };

export async function GET() {
  const latest = getLatest();
  if (!latest) {
    return NextResponse.json({ error: "No data yet" }, { status: 404, headers: CORS });
  }
  return NextResponse.json(latest, { headers: CORS });
}

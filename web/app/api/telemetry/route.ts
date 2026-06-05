/**
 * POST /api/telemetry
 * Receives a JSON telemetry payload from the ESP32.
 * Requires header: x-api-key: <API_KEY>
 *
 * GET /api/telemetry
 * Returns the latest single record (for quick health check).
 */
import { NextRequest, NextResponse } from "next/server";
import { addRecord, getLatest, TelemetryRecord } from "../../lib/store";
import { isAuthorized } from "../../lib/auth";

// Allow cross-origin requests so the dashboard can run on a different port
const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, x-api-key",
};

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS });
}

export async function POST(req: NextRequest) {
  // Auth check
  if (!isAuthorized(req.headers)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401, headers: CORS });
  }

  let body: Partial<TelemetryRecord>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400, headers: CORS });
  }

  // Validate required fields
  const required: (keyof TelemetryRecord)[] = [
    "timestamp", "voltage", "motor_current", "battery_current",
    "rpm", "duty", "mosfet_temp",
  ];
  for (const field of required) {
    if (body[field] === undefined || body[field] === null) {
      return NextResponse.json(
        { error: `Missing field: ${field}` },
        { status: 422, headers: CORS }
      );
    }
  }

  const record: TelemetryRecord = {
    timestamp:       Number(body.timestamp),
    voltage:         Number(body.voltage),
    motor_current:   Number(body.motor_current),
    battery_current: Number(body.battery_current),
    rpm:             Number(body.rpm),
    duty:            Number(body.duty),
    mosfet_temp:     Number(body.mosfet_temp),
    server_ts:       Date.now(),
  };

  addRecord(record);

  return NextResponse.json({ ok: true }, { status: 201, headers: CORS });
}

export async function GET() {
  const latest = getLatest();
  if (!latest) {
    return NextResponse.json({ error: "No data yet" }, { status: 404, headers: CORS });
  }
  return NextResponse.json(latest, { headers: CORS });
}

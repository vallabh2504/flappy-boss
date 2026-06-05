/**
 * In-memory telemetry store.
 * On Vercel serverless this resets between cold starts, which is acceptable
 * for live dashboards. Swap for a DB (Upstash Redis, PlanetScale, etc.)
 * if you need persistence across restarts.
 */

export interface TelemetryRecord {
  timestamp: number;      // ms since ESP32 boot
  voltage: number;        // V
  motor_current: number;  // A
  battery_current: number;// A
  rpm: number;            // electrical RPM
  duty: number;           // 0.0 – 1.0
  mosfet_temp: number;    // °C
  server_ts: number;      // Unix epoch ms (added by server)
}

// Keep last 600 samples ≈ 2 minutes at 200 ms interval
const MAX_HISTORY = 600;

// Use a module-level variable so it survives multiple requests within the
// same serverless function instance (warm invocations).
declare global {
  // eslint-disable-next-line no-var
  var __telemetryHistory: TelemetryRecord[] | undefined;
}

if (!global.__telemetryHistory) {
  global.__telemetryHistory = [];
}

export function addRecord(record: TelemetryRecord): void {
  global.__telemetryHistory!.push(record);
  if (global.__telemetryHistory!.length > MAX_HISTORY) {
    global.__telemetryHistory!.shift(); // drop oldest
  }
}

export function getLatest(): TelemetryRecord | null {
  const h = global.__telemetryHistory!;
  return h.length > 0 ? h[h.length - 1] : null;
}

export function getHistory(limit = 120): TelemetryRecord[] {
  const h = global.__telemetryHistory!;
  return h.slice(-limit);
}

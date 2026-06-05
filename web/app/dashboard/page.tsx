"use client";

/**
 * VESC Telemetry Dashboard
 * ─────────────────────────
 * Polls /api/telemetry/latest every 500 ms for the live card values.
 * Polls /api/telemetry/history every 1000 ms for chart data.
 *
 * Charts rendered with Recharts (no canvas required, SSR-safe).
 */

import { useEffect, useState, useCallback } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

// ─── Types ───────────────────────────────────────────────────────────────────

interface TelemetryRecord {
  timestamp: number;
  voltage: number;
  motor_current: number;
  battery_current: number;
  rpm: number;
  duty: number;
  mosfet_temp: number;
  server_ts: number;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmt(val: number | undefined, decimals = 1): string {
  if (val === undefined || val === null) return "–";
  return val.toFixed(decimals);
}

// Convert electrical RPM to mechanical RPM (divide by motor pole pairs).
// Adjust POLE_PAIRS to match your motor; 7 is common for outrunners.
const POLE_PAIRS = 7;
function elecToMechRpm(elec: number) {
  return Math.round(elec / POLE_PAIRS);
}

// ─── Stat Card ───────────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  unit,
  color = "text-accent",
}: {
  label: string;
  value: string;
  unit: string;
  color?: string;
}) {
  return (
    <div className="rounded-2xl bg-gray-900 border border-gray-800 p-5 flex flex-col gap-1 shadow-lg">
      <span className="text-xs font-semibold uppercase tracking-widest text-gray-500">
        {label}
      </span>
      <span className={`text-4xl font-bold tabular-nums ${color}`}>{value}</span>
      <span className="text-sm text-gray-400">{unit}</span>
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [latest, setLatest] = useState<TelemetryRecord | null>(null);
  const [history, setHistory] = useState<TelemetryRecord[]>([]);
  const [status, setStatus] = useState<"waiting" | "live" | "error">("waiting");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // The base URL is injected at build time via an env var so the same build
  // works locally (http://localhost:3000) and on Vercel (your domain).
  // NEXT_PUBLIC_ prefix makes it available in the browser bundle.
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

  const fetchLatest = useCallback(async () => {
    try {
      const res = await fetch(`${base}/api/telemetry/latest`, { cache: "no-store" });
      if (res.ok) {
        const data: TelemetryRecord = await res.json();
        setLatest(data);
        setStatus("live");
        setLastUpdated(new Date());
      } else if (res.status === 404) {
        setStatus("waiting");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  }, [base]);

  const fetchHistory = useCallback(async () => {
    try {
      // Fetch last 120 samples (≈24 s at 200 ms interval) for charts
      const res = await fetch(`${base}/api/telemetry/history?limit=120`, {
        cache: "no-store",
      });
      if (res.ok) {
        const data: TelemetryRecord[] = await res.json();
        setHistory(data);
      }
    } catch {
      // Non-critical; just keep the old history
    }
  }, [base]);

  useEffect(() => {
    fetchLatest();
    fetchHistory();

    const latestTimer = setInterval(fetchLatest, 500);
    const historyTimer = setInterval(fetchHistory, 1000);

    return () => {
      clearInterval(latestTimer);
      clearInterval(historyTimer);
    };
  }, [fetchLatest, fetchHistory]);

  // Format chart x-axis: seconds ago
  const chartData = history.map((r) => ({
    t: r.server_ts,
    voltage: r.voltage,
    motor_current: r.motor_current,
    battery_current: r.battery_current,
    rpm: elecToMechRpm(r.rpm),
    duty_pct: +(r.duty * 100).toFixed(1),
    mosfet_temp: r.mosfet_temp,
  }));

  const statusBadge = {
    waiting: "bg-yellow-500/20 text-yellow-400 border-yellow-700",
    live: "bg-green-500/20 text-green-400 border-green-700",
    error: "bg-red-500/20 text-red-400 border-red-700",
  }[status];

  const statusLabel = {
    waiting: "Waiting for data…",
    live: "Live",
    error: "Connection error",
  }[status];

  return (
    <main className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
            VESC Telemetry
          </h1>
          <p className="text-sm text-gray-500 mt-1">ESP32 → UART → Cloud → Dashboard</p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`text-xs font-semibold px-3 py-1 rounded-full border ${statusBadge}`}
          >
            {statusLabel}
          </span>
          {lastUpdated && (
            <span className="text-xs text-gray-600 hidden md:block">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <StatCard
          label="Battery Voltage"
          value={fmt(latest?.voltage)}
          unit="V"
          color="text-cyan-400"
        />
        <StatCard
          label="Motor Current"
          value={fmt(latest?.motor_current)}
          unit="A"
          color="text-orange-400"
        />
        <StatCard
          label="Battery Current"
          value={fmt(latest?.battery_current)}
          unit="A"
          color="text-yellow-400"
        />
        <StatCard
          label="Speed (mech)"
          value={latest ? String(elecToMechRpm(latest.rpm)) : "–"}
          unit="RPM"
          color="text-green-400"
        />
        <StatCard
          label="Duty Cycle"
          value={latest ? fmt(latest.duty * 100) : "–"}
          unit="%"
          color="text-purple-400"
        />
        <StatCard
          label="MOSFET Temp"
          value={fmt(latest?.mosfet_temp)}
          unit="°C"
          color={
            (latest?.mosfet_temp ?? 0) > 70 ? "text-red-400" : "text-blue-400"
          }
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Voltage over time */}
        <ChartCard title="Battery Voltage (V)">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="t" hide />
            <YAxis domain={["auto", "auto"]} stroke="#6b7280" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#111827", border: "1px solid #374151" }}
              labelFormatter={() => ""}
              formatter={(v: number) => [`${v.toFixed(2)} V`, "Voltage"]}
            />
            <Line
              type="monotone"
              dataKey="voltage"
              stroke="#22d3ee"
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          </LineChart>
        </ChartCard>

        {/* Current over time */}
        <ChartCard title="Current (A)">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="t" hide />
            <YAxis domain={["auto", "auto"]} stroke="#6b7280" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#111827", border: "1px solid #374151" }}
              labelFormatter={() => ""}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9ca3af" }} />
            <Line
              type="monotone"
              dataKey="motor_current"
              name="Motor"
              stroke="#f97316"
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="battery_current"
              name="Battery"
              stroke="#facc15"
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          </LineChart>
        </ChartCard>

        {/* RPM over time */}
        <ChartCard title="Mechanical RPM">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="t" hide />
            <YAxis domain={["auto", "auto"]} stroke="#6b7280" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#111827", border: "1px solid #374151" }}
              labelFormatter={() => ""}
              formatter={(v: number) => [`${v} RPM`, "Speed"]}
            />
            <Line
              type="monotone"
              dataKey="rpm"
              stroke="#4ade80"
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          </LineChart>
        </ChartCard>

        {/* Duty + Temp */}
        <ChartCard title="Duty Cycle (%) & MOSFET Temp (°C)">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="t" hide />
            <YAxis yAxisId="left" domain={[0, 100]} stroke="#6b7280" tick={{ fontSize: 11 }} />
            <YAxis yAxisId="right" orientation="right" domain={["auto", "auto"]} stroke="#6b7280" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "#111827", border: "1px solid #374151" }}
              labelFormatter={() => ""}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: "#9ca3af" }} />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="duty_pct"
              name="Duty %"
              stroke="#c084fc"
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="mosfet_temp"
              name="Temp °C"
              stroke="#60a5fa"
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          </LineChart>
        </ChartCard>
      </div>

      <footer className="mt-10 text-center text-xs text-gray-700">
        VESC Telemetry Dashboard · data via ESP32 UART bridge · polling 500 ms
      </footer>
    </main>
  );
}

// ─── Chart wrapper ────────────────────────────────────────────────────────────

function ChartCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactElement;
}) {
  return (
    <div className="rounded-2xl bg-gray-900 border border-gray-800 p-5 shadow-lg">
      <h2 className="text-sm font-semibold text-gray-400 mb-4 uppercase tracking-wider">
        {title}
      </h2>
      <ResponsiveContainer width="100%" height={200}>
        {children}
      </ResponsiveContainer>
    </div>
  );
}

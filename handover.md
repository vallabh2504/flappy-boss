# Handover Log — ESP32 VESC Redundancy Telematics

> This file is updated by each agent at the end of their work unit so any
> developer (human or AI) picking up the project can understand exactly what
> was done, what decisions were made, and what remains.

---

## Session 1 — Initial build (2026-06-05)

### Agent roster

| Agent | Role |
|-------|------|
| FirmwareDev | ESP32 Arduino firmware |
| BackendDev  | Next.js API routes + in-memory store |
| FrontendDev | React dashboard, Recharts charts, Tailwind |
| DevOps      | Git/GitHub runbook, Vercel deployment guide |

---

### What was built

#### FirmwareDev — `firmware/esp32_firmware.ino`

- Arduino sketch for ESP32 DevKit (Arduino core).
- Uses **VescUart** (SolidGeek) on `Serial2` (GPIO16 RX, GPIO17 TX) at 115200 baud.
- Reads: `inpVoltage`, `avgMotorCurrent`, `avgInputCurrent`, `rpm`, `dutyCycleNow`, `tempMosfet`.
- Connects to Wi-Fi; sends HTTPS POST to `/api/telemetry` every 200 ms.
- Auth via `x-api-key` header.
- All credentials are `const char*` at the top of the file — clearly marked for user to fill in.
- Uses `WiFiClientSecure` with `setInsecure()` for dev; commented note to use root CA in prod.
- Libraries required: VescUart, ArduinoJson ≥ 6.x (both from Library Manager).

**Key decisions:**
- `setInsecure()` chosen over bundling a root CA so the sketch is simpler for first-time users. Users can upgrade by pasting their CA cert.
- 200 ms send interval chosen to match VESC's typical telemetry update rate without flooding the network.

---

#### BackendDev — `web/app/api/telemetry/`

Files created:
- `route.ts` — `POST /api/telemetry` (ingest + auth) and `GET /api/telemetry` (latest alias).
- `latest/route.ts` — `GET /api/telemetry/latest`.
- `history/route.ts` — `GET /api/telemetry/history?limit=N` (default 120, max 600).
- `app/lib/store.ts` — Module-level in-memory ring buffer (max 600 records). Uses `global.__telemetryHistory` so warm serverless invocations share state.
- `app/lib/auth.ts` — Validates `x-api-key` header against `API_KEY` env var; fails-safe (rejects) if env var unset.

**Key decisions:**
- In-memory store chosen for zero-dependency simplicity. Noted in code that Upstash Redis / PlanetScale / SQLite are drop-in replacements.
- CORS headers on every response so the dashboard can be served from any origin during development.
- 422 returned for missing fields rather than 400 (semantic: request understood but unprocessable).

---

#### FrontendDev — `web/app/dashboard/page.tsx`

- `"use client"` React component with two polling loops:
  - `/api/telemetry/latest` every 500 ms → 6 stat cards.
  - `/api/telemetry/history?limit=120` every 1 s → 4 Recharts `LineChart` panels.
- Charts: Voltage, Current (motor + battery overlay), Mechanical RPM, Duty % + MOSFET Temp (dual Y-axis).
- `isAnimationActive={false}` on all lines to prevent jitter during rapid updates.
- `POLE_PAIRS = 7` constant converts electrical → mechanical RPM; noted for user adjustment.
- MOSFET temp card turns red above 70 °C as a visual fault indicator.
- Status badge: `waiting` (yellow) / `live` (green) / `error` (red).
- Tailwind dark theme (`bg-gray-950`) with colored accent per metric.
- Fully responsive: 2-col mobile → 6-col stat cards on desktop; 1-col → 2-col charts.

**Key decisions:**
- Recharts chosen over Chart.js — React-native, no imperative canvas refs needed, SSR-compatible.
- Polling over WebSocket — simpler, survives Vercel's serverless (no persistent connection needed); WebSocket upgrade is straightforward later via a dedicated WS server.
- `NEXT_PUBLIC_API_BASE_URL` used as base so the same build targets localhost in dev and the Vercel URL in prod without a redeploy.

---

#### DevOps — README_TELEMETRY.md

Complete runbook covering:
1. Hardware wiring table (VESC ↔ ESP32 pin mapping).
2. Arduino IDE library installation + firmware flash steps.
3. Local dev server setup with `curl` test command.
4. Git push procedure (PAT in remote URL, not in code).
5. Vercel project creation: root directory = `web`, env vars table.
6. Telemetry fields reference table.
7. "How to add more fields" guide (firmware → store type → dashboard card/chart).
8. Environment variables reference table with security note.

---

### File tree produced

```
firmware/
  esp32_firmware.ino

web/
  app/
    api/
      telemetry/
        route.ts           ← POST ingest + GET latest alias
        latest/route.ts    ← GET /api/telemetry/latest
        history/route.ts   ← GET /api/telemetry/history
    lib/
      store.ts             ← in-memory ring buffer
      auth.ts              ← API key validator
    dashboard/
      page.tsx             ← live dashboard UI
    globals.css
    layout.tsx
    page.tsx               ← redirects / → /dashboard
  .env.local.example
  .gitignore
  next.config.js
  package.json
  postcss.config.js
  tailwind.config.ts
  tsconfig.json

README_TELEMETRY.md
handover.md               ← this file
```

---

### What remains / next steps

| Priority | Task |
|----------|------|
| User    | Fill in `WIFI_SSID`, `WIFI_PASSWORD`, `API_BASE_URL`, `API_KEY` in firmware |
| User    | Wire ESP32 to VESC (5 solder points) |
| User    | Flash firmware; verify Serial Monitor output |
| User    | `cd web && npm install && npm run dev` to test locally |
| User    | Push to GitHub, create Vercel project, set env vars, deploy |
| Future  | Swap in-memory store for Upstash Redis for persistence across cold starts |
| Future  | Add WebSocket push from server → browser to eliminate polling latency |
| Future  | Add `tempMotor`, `wattHours`, `ampHours`, fault codes to telemetry |
| Future  | Add VESC fault code decoding and alert banner in dashboard |
| Future  | Replace `setInsecure()` with pinned root CA cert for production security |
| Future  | Add authentication to the dashboard page (currently public read) |

---

### Known limitations

- **In-memory store** resets on Vercel cold starts. For a low-traffic deployment this means up to a few minutes of history may be lost. Not a problem for live monitoring; is a problem for post-hoc analysis.
- **`setInsecure()` TLS** accepts any certificate — acceptable for a private dashboard, not for production over untrusted networks.
- **No fault/error decoding** — the VescUart library exposes `mc_fault_code`; it is not yet included in the payload or dashboard.
- **Pole pairs hardcoded** to 7 in the dashboard; must be changed to match the actual motor.

---

*Log maintained by the FirmwareDev / BackendDev / FrontendDev / DevOps agent team.*

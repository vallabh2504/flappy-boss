# ESP32 VESC Redundancy Telematics

End-to-end telemetry stack: **VESC motor controller → ESP32 (UART) → HTTPS → Next.js API → Live Dashboard**

---

## Repository layout

```
.
├── firmware/
│   └── esp32_firmware.ino   # Arduino sketch for ESP32
└── web/                     # Next.js 14 app (dashboard + API)
    ├── app/
    │   ├── api/telemetry/   # POST (ingest) + GET latest + GET history
    │   ├── dashboard/       # Live telemetry UI
    │   ├── lib/             # In-memory store, auth helper
    │   ├── layout.tsx
    │   └── page.tsx         # Root → redirects to /dashboard
    ├── .env.local.example
    ├── package.json
    └── tailwind.config.ts
```

---

## 1. Hardware wiring

| VESC pad | ESP32 pin |
|----------|-----------|
| 5 V      | VIN       |
| GND      | GND       |
| TX       | GPIO 16 (Serial2 RX) |
| RX       | GPIO 17 (Serial2 TX) |

> **VESC Tool** → App Settings → App to use: **UART**, UART baud: **115200**

---

## 2. Flash the ESP32

1. Install **Arduino IDE 2.x** + ESP32 board support (Espressif Systems).
2. Install libraries via *Sketch → Include Library → Manage Libraries*:
   - **VescUart** by SolidGeek
   - **ArduinoJson** by Benoît Blanchon (v6.x)
3. Open `firmware/esp32_firmware.ino`.
4. Edit the six `const char*` variables at the top of the file:
   - `WIFI_SSID`, `WIFI_PASSWORD` — your network credentials
   - `API_BASE_URL` — your Vercel deployment URL (e.g. `https://your-app.vercel.app`)
   - `API_KEY` — a long random string (same value you will set in Vercel)
5. Select *Tools → Board → ESP32 Dev Module* and the correct COM port.
6. Click **Upload**.
7. Open Serial Monitor (115200 baud) to verify `[WiFi] Connected` and `[TX] {...}` lines.

---

## 3. Run the dashboard locally

```bash
cd web
cp .env.local.example .env.local
# Edit .env.local: set API_KEY to the same value you used in firmware
npm install
npm run dev
# Open http://localhost:3000
```

The ESP32 must be on the same Internet (or you can test by POSTing fake data):

```bash
curl -X POST http://localhost:3000/api/telemetry \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"timestamp":1000,"voltage":42.1,"motor_current":5.2,"battery_current":4.8,"rpm":3500,"duty":0.35,"mosfet_temp":38.2}'
```

---

## 4. Push to GitHub

```bash
# One-time setup (replace with your PAT in the URL)
git clone https://github.com/Bharadhwajreddy/ESP32_RedundancyTelematics.git
cd ESP32_RedundancyTelematics

# Copy firmware and web folders into the cloned repo, then:
git add firmware/ web/ README_TELEMETRY.md
git commit -m "feat: initial VESC telemetry stack"
git push origin main
```

If you want to use a PAT without storing it in your shell history:

```bash
git remote set-url origin https://<YOUR_PAT>@github.com/Bharadhwajreddy/ESP32_RedundancyTelematics.git
git push origin main
```

---

## 5. Deploy to Vercel

### Step-by-step

1. Go to [vercel.com](https://vercel.com) → **Add New Project**.
2. Import the **ESP32_RedundancyTelematics** GitHub repository.
3. Set **Root Directory** to `web` (Vercel needs to find `package.json`).
4. In **Environment Variables**, add:

   | Key | Value |
   |-----|-------|
   | `API_KEY` | (same random string you put in firmware) |
   | `NEXT_PUBLIC_API_BASE_URL` | *(leave blank — Vercel sets this automatically via its domain)* |

5. Click **Deploy**.
6. Copy the deployment URL (e.g. `https://your-app.vercel.app`).
7. Paste that URL into `API_BASE_URL` in your firmware, re-flash the ESP32.

### Verify

```bash
curl https://your-app.vercel.app/api/telemetry/latest
# Should return {"error":"No data yet"} until the ESP32 sends a packet
```

---

## 6. Telemetry fields

| Field | Source | Unit |
|-------|--------|------|
| `voltage` | `vesc.data.inpVoltage` | V |
| `motor_current` | `vesc.data.avgMotorCurrent` | A |
| `battery_current` | `vesc.data.avgInputCurrent` | A |
| `rpm` | `vesc.data.rpm` | Electrical RPM |
| `duty` | `vesc.data.dutyCycleNow` | 0.0 – 1.0 |
| `mosfet_temp` | `vesc.data.tempMosfet` | °C |

To add more fields (e.g. `tempMotor`, `wattHours`):
1. Add to the JSON doc in `esp32_firmware.ino`.
2. Add to `TelemetryRecord` in `web/app/lib/store.ts`.
3. Add a card or chart line in `web/app/dashboard/page.tsx`.

---

## Environment variables reference

| Variable | Where | Purpose |
|----------|-------|---------|
| `API_KEY` | `.env.local` + Vercel | Auth token for ESP32 → API |
| `NEXT_PUBLIC_API_BASE_URL` | `.env.local` + Vercel | API base URL for browser fetch |

**Never commit `.env.local` or put secrets in code.**

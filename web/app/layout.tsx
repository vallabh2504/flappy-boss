import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VESC Telemetry Dashboard",
  description: "Live motor controller telemetry from ESP32 + VESC",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

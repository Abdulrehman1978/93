import { NextResponse } from "next/server";
import type { HealthStatus } from "@sambal/contracts";

const START_TIME = Date.now();

export async function GET() {
  const uptimeSeconds = Math.round((Date.now() - START_TIME) / 1000);
  const nowIso = new Date().toISOString();

  const healthData: HealthStatus = {
    status: "ok",
    service: "SAMBAL Next.js PWA Web Shell",
    version: "0.1.0",
    timestamp: nowIso,
    uptime_seconds: uptimeSeconds,
    dependencies: {
      frontend_runtime: {
        status: "healthy",
        details: "Next.js 16 Active-LTS App Router operational",
      },
    },
  };

  return NextResponse.json(healthData, {
    status: 200,
    headers: {
      "Cache-Control": "no-store, max-age=0",
      "X-Service-Name": "sambal-web",
    },
  });
}

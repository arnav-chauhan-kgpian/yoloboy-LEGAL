import { NextResponse } from "next/server";

export async function GET() {
  const backend = process.env.BACKEND_URL ?? "(not set — using http://localhost:8000)";
  let backendHealth: unknown = null;
  try {
    const r = await fetch(`${process.env.BACKEND_URL ?? "http://localhost:8000"}/api/health`, { cache: "no-store" });
    backendHealth = await r.json();
  } catch (e) {
    backendHealth = String(e);
  }
  return NextResponse.json({ backend_url: backend, backend_health: backendHealth });
}

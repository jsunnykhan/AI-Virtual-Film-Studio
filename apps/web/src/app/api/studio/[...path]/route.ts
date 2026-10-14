import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Root output directory of the repo
const REPO_OUTPUT_DIR = path.resolve(process.cwd(), "../../output");

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  const pathParts = resolvedParams.path || [];
  const endpoint = pathParts.join("/");

  // 1. Try to fetch from FastAPI backend first
  try {
    const backendRes = await fetch(`${BACKEND_URL}/${endpoint}`, {
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
    });
    if (backendRes.ok) {
      const data = await backendRes.json();
      return NextResponse.json(data);
    }
  } catch (err) {
    // Backend offline / unreachable, fallback to disk
  }

  // 2. Resilient fallback: read directly from repo files
  if (endpoint === "studio/catalog" || endpoint === "catalog") {
    const catalogFile = path.join(REPO_OUTPUT_DIR, "studio_catalog.json");
    if (fs.existsSync(catalogFile)) {
      try {
        const raw = fs.readFileSync(catalogFile, "utf-8");
        const list = JSON.parse(raw);
        return NextResponse.json({ total_productions: list.length, catalog: list });
      } catch (e) {}
    }
    return NextResponse.json({ total_productions: 0, catalog: [] });
  }

  if (endpoint === "workflows/creative/catalog" || endpoint === "creative/catalog") {
    const creativeFile = path.join(REPO_OUTPUT_DIR, "creative_concepts.json");
    if (fs.existsSync(creativeFile)) {
      try {
        const raw = fs.readFileSync(creativeFile, "utf-8");
        const list = JSON.parse(raw);
        return NextResponse.json({ total_concepts: list.length, catalog: list });
      } catch (e) {}
    }
    return NextResponse.json({ total_concepts: 0, catalog: [] });
  }

  if (endpoint === "studio/status") {
    const catalogFile = path.join(REPO_OUTPUT_DIR, "studio_catalog.json");
    let count = 0;
    let lastItem: any = null;
    if (fs.existsSync(catalogFile)) {
      try {
        const list = JSON.parse(fs.readFileSync(catalogFile, "utf-8"));
        count = list.length;
        if (count > 0) lastItem = list[list.length - 1];
      } catch (e) {}
    }

    return NextResponse.json({
      studio_active_24_7: true,
      paused: false,
      current_project_id: lastItem ? lastItem.project_id : null,
      current_project_title: lastItem ? lastItem.title : "Standby / Cooldown",
      current_stage: "autonomous_engine_standby",
      cycle_count: count,
      successful_productions: count,
      failed_productions: 0,
      started_at: lastItem?.produced_at || new Date().toISOString(),
      last_completed_at: lastItem?.produced_at || null,
      last_error: null,
      catalog_path: catalogFile,
    });
  }

  if (endpoint.startsWith("studio/projects/")) {
    const projectId = pathParts[pathParts.length - 1];
    const projectFile = path.join(REPO_OUTPUT_DIR, "projects", `${projectId}.json`);
    if (fs.existsSync(projectFile)) {
      try {
        const raw = fs.readFileSync(projectFile, "utf-8");
        return NextResponse.json({ project_id: projectId, state: JSON.parse(raw) });
      } catch (e) {}
    }
    // Check if in catalog
    const catalogFile = path.join(REPO_OUTPUT_DIR, "studio_catalog.json");
    if (fs.existsSync(catalogFile)) {
      try {
        const list = JSON.parse(fs.readFileSync(catalogFile, "utf-8"));
        const match = list.find((item: any) => item.project_id === projectId);
        if (match) return NextResponse.json({ project_id: projectId, state: match });
      } catch (e) {}
    }
    return NextResponse.json({ error: "Project not found" }, { status: 404 });
  }

  return NextResponse.json({ error: "Endpoint not found" }, { status: 404 });
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  const pathParts = resolvedParams.path || [];
  const endpoint = pathParts.join("/");
  const body = await req.json().catch(() => ({}));

  try {
    const backendRes = await fetch(`${BACKEND_URL}/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return NextResponse.json(await backendRes.json());
  } catch (err: any) {
    return NextResponse.json(
      { message: `Action '${endpoint}' simulated (Backend starting or port mismatch)`, status: { studio_active_24_7: true } },
      { status: 200 }
    );
  }
}

export const API_BASE_URL =
  typeof window !== "undefined"
    ? "/api/studio"
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StudioStatus {
  studio_active_24_7: boolean;
  paused: boolean;
  current_project_id: string | null;
  current_project_title: string | null;
  current_stage: string;
  cycle_count: number;
  successful_productions: number;
  failed_productions: number;
  started_at: string | null;
  last_completed_at: string | null;
  last_error: string | null;
  catalog_path: string;
}

export interface CatalogItem {
  cycle_number?: number;
  project_id: string;
  title: string;
  format: string;
  genre?: string[] | string;
  logline?: string;
  runtime_decided_by_ai?: string | number | null;
  scene_video_path?: string | null;
  final_movie_path?: string | null;
  clearance_verdict?: string;
  produced_at: string;
  total_render_duration_seconds?: number;
  status: string;
  creative_workflow?: string;
}

export interface CreativeConceptItem {
  project_id: string;
  title: string;
  format: string;
  genre: string[];
  logline: string;
  series_premise: string;
  core_theme: string;
  characters_count: number;
  critic_verdict: string;
  executive_approved: boolean;
  research_completed: boolean;
  status: string;
  created_at: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  role: string;
  node: string;
}

export interface DepartmentInfo {
  id: string;
  name: string;
  agents: AgentInfo[];
}

export async function fetchStudioStatus(): Promise<StudioStatus> {
  const res = await fetch(`${API_BASE_URL}/studio/status`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch status: ${res.statusText}`);
  return res.json();
}

export async function fetchStudioCatalog(): Promise<{ total_productions: number; catalog: CatalogItem[] }> {
  const res = await fetch(`${API_BASE_URL}/studio/catalog`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch catalog: ${res.statusText}`);
  return res.json();
}

export async function fetchCreativeCatalog(): Promise<{ total_concepts: number; catalog: CreativeConceptItem[] }> {
  const res = await fetch(`${API_BASE_URL}/workflows/creative/catalog`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch creative catalog: ${res.statusText}`);
  return res.json();
}

export async function fetchStudioAgents(): Promise<{ departments: DepartmentInfo[] }> {
  const res = await fetch(`${API_BASE_URL}/studio/agents`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch agents: ${res.statusText}`);
  return res.json();
}

export async function fetchProjectDetails(projectId: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/studio/projects/${projectId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch project details: ${res.statusText}`);
  return res.json();
}

export async function studioStart(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/studio/start`, { method: "POST" });
  return res.json();
}

export async function studioPause(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/studio/pause`, { method: "POST" });
  return res.json();
}

export async function studioResume(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/studio/resume`, { method: "POST" });
  return res.json();
}

export async function studioRestart(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/studio/restart`, { method: "POST" });
  return res.json();
}

export async function studioStop(): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/studio/stop`, { method: "POST" });
  return res.json();
}

export async function triggerMovieWorkflow(payload: {
  user_request?: string;
  format?: string;
  target_duration_minutes?: number | null;
  max_iterations?: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/workflows/movie`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function triggerCreativeWorkflow(payload: {
  user_request?: string;
  max_iterations?: number;
}): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/workflows/creative`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

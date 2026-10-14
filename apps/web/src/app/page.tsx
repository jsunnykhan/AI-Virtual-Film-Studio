"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Film,
  Workflow,
  Bot,
  Sparkles,
  Clapperboard,
  Activity,
  RefreshCw,
  Search,
  Filter,
} from "lucide-react";
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AppSidebar } from "@/components/studio/AppSidebar";
import { StatsRibbon } from "@/components/studio/StatsRibbon";
import { CatalogView } from "@/components/studio/CatalogView";
import { WorkflowsView } from "@/components/studio/WorkflowsView";
import { ProjectDetailSheet } from "@/components/studio/ProjectDetailSheet";
import { NewProductionModal } from "@/components/studio/NewProductionModal";
import { NewCreativeModal } from "@/components/studio/NewCreativeModal";
import {
  fetchStudioStatus,
  fetchStudioCatalog,
  fetchCreativeCatalog,
  fetchProjectDetails,
  StudioStatus,
  CatalogItem,
  CreativeConceptItem,
} from "@/lib/api";

export default function StudioHomePage() {
  const [status, setStatus] = useState<StudioStatus | null>(null);
  const [productions, setProductions] = useState<CatalogItem[]>([]);
  const [concepts, setConcepts] = useState<CreativeConceptItem[]>([]);
  const [activeTab, setActiveTab] = useState<"catalog" | "workflows" | "departments">("catalog");

  // Inspection Drawer & Modal State
  const [selectedProject, setSelectedProject] = useState<CatalogItem | CreativeConceptItem | null>(null);
  const [fullProjectState, setFullProjectState] = useState<any | null>(null);
  const [isProjectLoading, setIsProjectLoading] = useState(false);
  const [isNewProductionOpen, setIsNewProductionOpen] = useState(false);
  const [isNewCreativeOpen, setIsNewCreativeOpen] = useState(false);

  // Load studio data
  const loadData = useCallback(async () => {
    try {
      const [statusRes, catalogRes, creativeRes] = await Promise.allSettled([
        fetchStudioStatus(),
        fetchStudioCatalog(),
        fetchCreativeCatalog(),
      ]);

      if (statusRes.status === "fulfilled") setStatus(statusRes.value);
      if (catalogRes.status === "fulfilled") setProductions(catalogRes.value.catalog || []);
      if (creativeRes.status === "fulfilled") setConcepts(creativeRes.value.catalog || []);
    } catch (err) {
      console.warn("Studio data polling error:", err);
    }
  }, []);

  // Polling every 4 seconds for continuous 24/7 background updates
  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 4000);
    return () => clearInterval(interval);
  }, [loadData]);

  // Handle selecting a project -> slides in ProjectDetailSheet from right to left
  const handleSelectProject = async (item: CatalogItem | CreativeConceptItem) => {
    setSelectedProject(item);
    setIsProjectLoading(true);
    setFullProjectState(null);

    try {
      const details = await fetchProjectDetails(item.project_id);
      setFullProjectState(details?.state || details);
    } catch (err) {
      // Fallback: item itself has metadata
      setFullProjectState(item);
    } finally {
      setIsProjectLoading(false);
    }
  };

  const isActive = status?.studio_active_24_7 && !status?.paused;
  const isPaused = status?.studio_active_24_7 && status?.paused;

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-screen w-full bg-[#07080d] text-slate-100 font-sans selection:bg-amber-500/30 selection:text-amber-200">
        {/* Left Collapsible App Sidebar (sidebar-07 pattern) */}
        <AppSidebar
          status={status}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          catalogCount={productions.length}
          conceptsCount={concepts.length}
          onRefresh={loadData}
          onOpenNewProduction={() => setIsNewProductionOpen(true)}
          onOpenNewCreative={() => setIsNewCreativeOpen(true)}
        />

        {/* Main Content Inset */}
        <SidebarInset className="flex-1 flex flex-col min-w-0 bg-[#07080d]">
          {/* Top Sticky Command Header */}
          <header className="sticky top-0 z-30 flex h-14 shrink-0 items-center justify-between gap-4 border-b border-white/10 bg-[#080a13]/85 backdrop-blur-md px-5">
            <div className="flex items-center gap-3">
              <SidebarTrigger
                id="btn-toggle-sidebar"
                className="text-slate-400 hover:text-white hover:bg-white/5"
              />
              <Separator orientation="vertical" className="h-4 bg-white/10" />
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400">Studio</span>
                <span className="text-white/30">/</span>
                <span className="font-semibold text-white font-outfit capitalize">
                  {activeTab === "catalog"
                    ? "Film & Series Catalog"
                    : activeTab === "workflows"
                    ? "24-Agent Workflow Graph"
                    : "Departments & System Policies"}
                </span>
              </div>
            </div>

            {/* Right Status Pill & Quick Controls */}
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2.5 bg-black/40 border border-white/10 rounded-full px-3 py-1 text-xs">
                <span className="relative flex h-2 w-2">
                  {isActive ? (
                    <>
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </>
                  ) : isPaused ? (
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                  ) : (
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-slate-500"></span>
                  )}
                </span>
                <span className="font-semibold uppercase tracking-wider text-[11px] text-slate-200">
                  {isActive ? "24/7 Loop Active" : isPaused ? "Loop Paused" : "Engine Standby"}
                </span>
                <span className="text-white/20">|</span>
                <span className="text-[11px] text-amber-300 font-mono">
                  Cycle #{status?.cycle_count ?? 0}
                </span>
              </div>

              <Button
                id="btn-header-produce"
                size="sm"
                className="h-8 text-xs bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-semibold shadow-md shadow-amber-500/20"
                onClick={() => setIsNewProductionOpen(true)}
              >
                <Clapperboard className="h-3.5 w-3.5 mr-1.5" />
                Produce Movie
              </Button>

              <Button
                id="btn-header-refresh"
                size="sm"
                variant="ghost"
                className="h-8 w-8 p-0 text-slate-400 hover:text-white"
                onClick={loadData}
                title="Refresh Studio State"
              >
                <RefreshCw className="h-3.5 w-3.5" />
              </Button>
            </div>
          </header>

          {/* Main Content Area */}
          <div className="flex-1 p-6 space-y-6 max-w-7xl w-full mx-auto">
            {/* Live Metrics Ribbon */}
            <StatsRibbon
              status={status}
              totalProductions={productions.length}
              totalConcepts={concepts.length}
            />

            {/* Dynamic View Content */}
            {activeTab === "catalog" && (
              <CatalogView
                productions={productions}
                concepts={concepts}
                onSelectProject={handleSelectProject}
              />
            )}

            {activeTab === "workflows" && <WorkflowsView />}

            {activeTab === "departments" && <DepartmentsDirectoryView />}
          </div>
        </SidebarInset>
      </div>

      {/* Right-to-Left Slide-over Sheet (replacing centered modal) */}
      <ProjectDetailSheet
        item={selectedProject}
        isOpen={selectedProject !== null}
        onClose={() => setSelectedProject(null)}
        fullState={fullProjectState}
        isLoading={isProjectLoading}
      />

      {/* Launcher Modals */}
      <NewProductionModal
        isOpen={isNewProductionOpen}
        onClose={() => setIsNewProductionOpen(false)}
        onSuccess={loadData}
      />

      <NewCreativeModal
        isOpen={isNewCreativeOpen}
        onClose={() => setIsNewCreativeOpen(false)}
        onSuccess={loadData}
      />
    </SidebarProvider>
  );
}

// 24 Agents Directory
function DepartmentsDirectoryView() {
  const departments = [
    {
      name: "1. Executive Department",
      color: "border-amber-500/30 text-amber-300",
      agents: [
        { name: "Executive Producer", role: "Commercial viability, greenlight, runtime & duration decision, high-level strategy." },
        { name: "Production Manager", role: "Resource allocation, scheduling, milestones, and department budgets." },
      ],
    },
    {
      name: "2. Creative Development",
      color: "border-purple-500/30 text-purple-300",
      agents: [
        { name: "Idea Generator", role: "Unassisted narrative ideation, premise sparks, and core protagonist hooks." },
        { name: "Idea Critic", role: "Originality auditing, episode engine testing, and revision recommendations." },
        { name: "Concept Developer", role: "Refined series blueprint, character relationship matrix, and season arc." },
        { name: "Research Agent", role: "Scientific grounding, cultural authenticity, and reference bible creation." },
      ],
    },
    {
      name: "3. Story & Screenwriting",
      color: "border-blue-500/30 text-blue-300",
      agents: [
        { name: "Story Architect", role: "5-act structure, emotional beat sheets, and sequence pacing." },
        { name: "World Designer", role: "Comprehensive world bible, lore, geography, and societal laws." },
        { name: "Character Designer", role: "Physical traits, costume specifications, voice profile, and motivation." },
        { name: "Screenwriter", role: "Full screenplay scenes with sluglines, action description, and dialogue." },
        { name: "Script Editor", role: "Dialogue polish, subtext enhancement, and dramatic rhythm adjustment." },
      ],
    },
    {
      name: "4. Directing & Art",
      color: "border-emerald-500/30 text-emerald-300",
      agents: [
        { name: "Director", role: "Tonal vision, performance cadence, blocking notes, and visual subtext." },
        { name: "Cinematographer", role: "Lens selection, camera motion, aspect ratio, and lighting setups." },
        { name: "Production Designer", role: "Architectural sets, environment textures, prop bibles, and color palettes." },
        { name: "Storyboard Artist", role: "Frame-by-frame visual blocking, action vectors, and transitions." },
        { name: "Shot Planner", role: "Calculates shot lists, timings, camera rigs, and render complexity." },
      ],
    },
    {
      name: "5. Audio Department",
      color: "border-pink-500/30 text-pink-300",
      agents: [
        { name: "Voice Director", role: "Voice casting specs, performance cadence, and TTS emotional prompts." },
        { name: "Music & Sound Designer", role: "Soundtrack scoring motifs, foley cue sheets, and ambient soundscapes." },
      ],
    },
    {
      name: "6. Generation & Rendering",
      color: "border-cyan-500/30 text-cyan-300",
      agents: [
        { name: "Prompt Engineer", role: "High-fidelity positive/negative prompts, LoRA weights, and checkpoints." },
        { name: "Generation Supervisor", role: "ComfyUI workflow parameters, CFG scales, sampler steps, and seeds." },
      ],
    },
    {
      name: "7. Post-Production",
      color: "border-yellow-500/30 text-yellow-300",
      agents: [
        { name: "Editor", role: "Scene pacing, montage cutting, shot sequencing, and scene transitions." },
        { name: "Finishing Supervisor", role: "Color grading LUTs, audio LUFS mastering, and FFmpeg assembly profile." },
      ],
    },
    {
      name: "8. Quality & Release",
      color: "border-rose-500/30 text-rose-300",
      agents: [
        { name: "Continuity QC Agent", role: "Visual continuity auditing, prop tracking, and character consistency." },
        { name: "Rights Delivery Reviewer", role: "Copyright clearance, trademark check, and worldwide release certification." },
      ],
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {departments.map((dept, idx) => (
        <div key={idx} className={`glass-panel p-5 rounded-xl border ${dept.color}`}>
          <h3 className={`text-sm font-bold font-outfit uppercase tracking-wider mb-3 ${dept.color}`}>
            {dept.name}
          </h3>
          <div className="space-y-2">
            {dept.agents.map((agent, aIdx) => (
              <div key={aIdx} className="bg-black/30 p-2.5 rounded-lg border border-white/5 space-y-0.5">
                <div className="font-semibold text-xs text-white">{agent.name}</div>
                <div className="text-[11px] text-slate-400">{agent.role}</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

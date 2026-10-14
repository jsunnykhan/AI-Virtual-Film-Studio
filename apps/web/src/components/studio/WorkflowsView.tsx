"use client";

import React, { useState } from "react";
import {
  Layers,
  ArrowRight,
  Sparkles,
  Bot,
  Film,
  Camera,
  Music,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  Workflow,
  Info,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface WorkflowStep {
  id: string;
  name: string;
  department: string;
  role: string;
  tools: string[];
}

const MOVIE_PIPELINE: WorkflowStep[] = [
  { id: "idea_generator", name: "Idea Generator", department: "Creative", role: "Conceives original premise, themes, and protagonist hooks", tools: ["creative_ideas.get", "movie_bible.search"] },
  { id: "executive_producer", name: "Executive Producer", department: "Executive", role: "Evaluates commercial viability, decides runtime dynamically, greenlights production", tools: ["budget_calculator", "market_trends"] },
  { id: "idea_critic", name: "Idea Critic", department: "Creative", role: "Critiques premise, originality, episode engine, identifies revision requests", tools: ["creative_ideas.search", "movie_bible.search"] },
  { id: "concept_developer", name: "Concept Developer", department: "Creative", role: "Develops full series blueprint, characters, episode engine, and season arc", tools: ["character_canon.get", "concept_bible.upsert"] },
  { id: "research_agent", name: "Research Agent", department: "Creative", role: "Grounds narrative authenticity, scientific concepts, and visual references", tools: ["web_research", "canon_knowledge.search"] },
  { id: "production_manager", name: "Production Manager", department: "Executive", role: "Allocates resources, schedule, department budget, and shot milestones", tools: ["schedule_tracker", "resource_allocator"] },
  { id: "story_architect", name: "Story Architect", department: "Story", role: "Constructs 5-act narrative framework, emotional beats, and pacing", tools: ["story_structure_engine"] },
  { id: "world_designer", name: "World Designer", department: "Story", role: "Drafts comprehensive world bible, societal rules, environments, geography", tools: ["world_bible.upsert", "lore_checker"] },
  { id: "character_designer", name: "Character Designer", department: "Story", role: "Creates visual profiles, wardrobe, voice cadence, emotional engine", tools: ["character_bible.upsert"] },
  { id: "screenwriter", name: "Screenwriter", department: "Story", role: "Writes full Hollywood screenplay scenes with sluglines, actions, and dialogue", tools: ["screenplay_formatter"] },
  { id: "script_editor", name: "Script Editor", department: "Story", role: "Polishes dialogue rhythm, subtext, dramatic tension, and pacing", tools: ["script_polish_engine"] },
  { id: "director", name: "Director", department: "Directing", role: "Establishes tonal vision, actor performance direction, and visual subtext", tools: ["directorial_notes.upsert"] },
  { id: "cinematographer", name: "Cinematographer", department: "Directing", role: "Designs lighting schemes, lens packages, aspect ratio, and camera rigs", tools: ["lens_calculator", "lighting_bible"] },
  { id: "production_designer", name: "Production Designer", department: "Directing", role: "Architects sets, color schemes, prop bibles, and environment textures", tools: ["art_department_bible"] },
  { id: "storyboard_artist", name: "Storyboard Artist", department: "Directing", role: "Draws visual camera blocking, transitions, keyframes, and action vectors", tools: ["storyboard_engine"] },
  { id: "shot_planner", name: "Shot Planner", department: "Directing", role: "Calculates shot lists, timings, camera motion, and render complexity", tools: ["shot_list.upsert"] },
  { id: "voice_director", name: "Voice Director", department: "Audio", role: "Defines voice casting specs, cadence, emotion tags, and TTS prompts", tools: ["tts_voice_generator"] },
  { id: "music_sound_designer", name: "Music & Sound Designer", department: "Audio", role: "Scores thematic soundtrack motifs, foley cue sheets, and ambient soundscapes", tools: ["audio_cue_sheet.upsert"] },
  { id: "prompt_engineer", name: "Prompt Engineer", department: "Generation", role: "Engineers high-fidelity ComfyUI positive/negative prompts, LoRAs, checkpoints", tools: ["prompt_matrix_builder"] },
  { id: "generation_supervisor", name: "Generation Supervisor", department: "Generation", role: "Supervises ComfyUI workflow parameters, CFG scales, sampler steps, seeds", tools: ["comfyui_runner"] },
  { id: "editor", name: "Editor", department: "Post-Production", role: "Sequences shots, manages pacing cuts, montage flow, and scene transitions", tools: ["timeline_assembler"] },
  { id: "finishing_supervisor", name: "Finishing Supervisor", department: "Post-Production", role: "Applies master color grading LUTs, audio LUFS mastering, FFmpeg assembly specs", tools: ["ffmpeg_transcoder"] },
  { id: "continuity_qc", name: "Continuity QC Agent", department: "Quality", role: "Audits visual consistency, character wardrobe tracking, and lighting checks", tools: ["qc_validator"] },
  { id: "rights_delivery", name: "Rights Reviewer", department: "Quality", role: "Legal copyright clearance, trademark audit, worldwide release certification", tools: ["clearance_verifier"] },
];

export function WorkflowsView() {
  const [activeWorkflow, setActiveWorkflow] = useState<"movie" | "creative" | "scene">("movie");
  const [selectedStep, setSelectedStep] = useState<WorkflowStep>(MOVIE_PIPELINE[0]);

  const pipeline =
    activeWorkflow === "movie"
      ? MOVIE_PIPELINE
      : activeWorkflow === "creative"
      ? MOVIE_PIPELINE.slice(0, 5)
      : MOVIE_PIPELINE.slice(15, 22);

  return (
    <div className="space-y-6">
      {/* Workflow Selector Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-panel p-4 rounded-xl border border-white/5">
        <div>
          <h2 className="text-base font-bold font-outfit text-white flex items-center gap-2">
            <Workflow className="h-4 w-4 text-amber-400" />
            Studio Multi-Department Orchestration
          </h2>
          <p className="text-xs text-slate-400">
            LangGraph state machine coordinating 24 agents across linear &amp; conditional feedback loops.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            id="btn-wf-movie"
            size="sm"
            variant={activeWorkflow === "movie" ? "default" : "ghost"}
            className={`text-xs h-8 ${activeWorkflow === "movie" ? "bg-amber-500 text-black font-semibold hover:bg-amber-400" : "text-slate-400"}`}
            onClick={() => {
              setActiveWorkflow("movie");
              setSelectedStep(MOVIE_PIPELINE[0]);
            }}
          >
            Full Movie Pipeline (24 Agents)
          </Button>
          <Button
            id="btn-wf-creative"
            size="sm"
            variant={activeWorkflow === "creative" ? "default" : "ghost"}
            className={`text-xs h-8 ${activeWorkflow === "creative" ? "bg-purple-500 text-white font-semibold hover:bg-purple-400" : "text-slate-400"}`}
            onClick={() => {
              setActiveWorkflow("creative");
              setSelectedStep(MOVIE_PIPELINE[0]);
            }}
          >
            Creative Ideation (5 Agents)
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Pipeline Visual DAG */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-xl border border-white/5 space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-400 font-semibold uppercase tracking-wider border-b border-white/5 pb-3">
            <span>Execution Sequence ({pipeline.length} Nodes)</span>
            <span>Click any node to inspect</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-h-[600px] overflow-y-auto pr-1">
            {pipeline.map((step, idx) => {
              const isSelected = selectedStep.id === step.id;
              return (
                <div
                  key={step.id}
                  id={`wf-node-${step.id}`}
                  onClick={() => setSelectedStep(step)}
                  className={`p-3 rounded-lg border text-xs cursor-pointer transition-all flex items-start gap-3 ${
                    isSelected
                      ? "bg-amber-500/15 border-amber-500/40 text-white shadow-lg shadow-amber-500/10"
                      : "bg-white/[0.02] border-white/5 text-slate-300 hover:bg-white/[0.05] hover:border-white/10"
                  }`}
                >
                  <div className="h-6 w-6 rounded-md bg-white/5 border border-white/10 flex items-center justify-center shrink-0 font-mono text-[10px] text-amber-400 font-bold">
                    {idx + 1}
                  </div>
                  <div className="space-y-1 min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1">
                      <span className="font-bold text-white truncate">{step.name}</span>
                      <Badge variant="outline" className="text-[9px] px-1 py-0 border-white/10 text-slate-400">
                        {step.department}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-slate-400 line-clamp-1">
                      {step.role}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 1 Col: Agent Deep Inspector */}
        <div className="glass-panel p-5 rounded-xl border border-white/5 space-y-4">
          <div className="flex items-center justify-between text-xs text-amber-300 font-semibold uppercase tracking-wider border-b border-white/5 pb-3">
            <span>Agent Node Spec</span>
            <Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30 text-[10px]">
              Active Node
            </Badge>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-bold font-outfit text-white">
                {selectedStep.name}
              </h3>
              <Badge variant="outline" className="text-xs text-cyan-300 border-cyan-500/30 mt-1">
                Department: {selectedStep.department}
              </Badge>
            </div>

            <div className="space-y-1.5 text-xs">
              <span className="font-bold text-slate-400 uppercase tracking-wider text-[10px] block">
                Primary Studio Responsibility
              </span>
              <p className="text-slate-200 leading-relaxed bg-black/30 p-3 rounded-lg border border-white/5">
                {selectedStep.role}
              </p>
            </div>

            <div className="space-y-1.5 text-xs">
              <span className="font-bold text-slate-400 uppercase tracking-wider text-[10px] block">
                Allowed Tools &amp; Memory Access
              </span>
              <div className="flex flex-wrap gap-1.5">
                {selectedStep.tools.map((t) => (
                  <code
                    key={t}
                    className="bg-purple-950/40 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded text-[10px] font-mono"
                  >
                    {t}
                  </code>
                ))}
              </div>
            </div>

            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs space-y-1 text-amber-200/90">
              <div className="flex items-center gap-1.5 font-semibold text-amber-300">
                <Info className="h-3.5 w-3.5" />
                Autonomous Graph Behavior
              </div>
              <p className="text-[11px] text-slate-300">
                In the 24/7 autonomous loop, this agent triggers automatically when the previous department finishes. Output state is persisted into PostgreSQL vector memory.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

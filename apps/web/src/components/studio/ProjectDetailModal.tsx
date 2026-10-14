"use client";

import React, { useState } from "react";
import {
  X,
  Film,
  Bot,
  CheckCircle,
  Clock,
  Sparkles,
  FileText,
  Video,
  Music,
  Camera,
  Layers,
  Palette,
  ShieldCheck,
  Code,
  Copy,
  Check,
  AlertCircle,
  Cpu,
} from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CatalogItem, CreativeConceptItem } from "@/lib/api";

interface ProjectDetailModalProps {
  item: CatalogItem | CreativeConceptItem | null;
  isOpen: boolean;
  onClose: () => void;
  fullState: any | null;
  isLoading: boolean;
}

const AGENTS_LIST = [
  // Executive
  { id: "executive_producer", name: "Executive Producer", dept: "Executive", icon: ShieldCheck, stateKey: "final_decision" },
  { id: "production_manager", name: "Production Manager", dept: "Executive", icon: Clock, stateKey: "production_plan" },
  // Creative
  { id: "idea_generator", name: "Idea Generator", dept: "Creative Dev", icon: Sparkles, stateKey: "idea" },
  { id: "idea_critic", name: "Idea Critic", dept: "Creative Dev", icon: AlertCircle, stateKey: "critique" },
  { id: "concept_developer", name: "Concept Developer", dept: "Creative Dev", icon: Layers, stateKey: "concept" },
  { id: "research_agent", name: "Research Agent", dept: "Creative Dev", icon: FileText, stateKey: "research" },
  // Story
  { id: "story_architect", name: "Story Architect", dept: "Story & Script", icon: Layers, stateKey: "story_architecture" },
  { id: "world_designer", name: "World Designer", dept: "Story & Script", icon: Palette, stateKey: "world_design" },
  { id: "character_designer", name: "Character Designer", dept: "Story & Script", icon: Bot, stateKey: "character_design" },
  { id: "screenwriter", name: "Screenwriter", dept: "Story & Script", icon: FileText, stateKey: "screenplay" },
  { id: "script_editor", name: "Script Editor", dept: "Story & Script", icon: FileText, stateKey: "script_edit" },
  // Directing & Art
  { id: "director", name: "Director", dept: "Directing & Art", icon: Film, stateKey: "directorial_vision" },
  { id: "cinematographer", name: "Cinematographer", dept: "Directing & Art", icon: Camera, stateKey: "cinematography" },
  { id: "production_designer", name: "Production Designer", dept: "Directing & Art", icon: Palette, stateKey: "production_design" },
  { id: "storyboard_artist", name: "Storyboard Artist", dept: "Directing & Art", icon: Video, stateKey: "storyboard" },
  { id: "shot_planner", name: "Shot Planner", dept: "Directing & Art", icon: Film, stateKey: "shot_plan" },
  // Audio
  { id: "voice_director", name: "Voice Director", dept: "Audio", icon: Bot, stateKey: "voice_direction" },
  { id: "music_sound_designer", name: "Music & Sound", dept: "Audio", icon: Music, stateKey: "music_sound_design" },
  // Generation
  { id: "prompt_engineer", name: "Prompt Engineer", dept: "Generation", icon: Cpu, stateKey: "prompts" },
  { id: "generation_supervisor", name: "Gen Supervisor", dept: "Generation", icon: Cpu, stateKey: "render_supervision" },
  // Post
  { id: "editor", name: "Editor", dept: "Post-Production", icon: Film, stateKey: "editor" },
  { id: "finishing_supervisor", name: "Finishing Supervisor", dept: "Post-Production", icon: Video, stateKey: "finishing_supervisor" },
  // QC
  { id: "continuity_qc", name: "Continuity QC", dept: "Quality & QC", icon: ShieldCheck, stateKey: "continuity_qc" },
  { id: "rights_delivery", name: "Rights Reviewer", dept: "Quality & QC", icon: ShieldCheck, stateKey: "rights_clearance" },
];

export function ProjectDetailModal({
  item,
  isOpen,
  onClose,
  fullState,
  isLoading,
}: ProjectDetailModalProps) {
  const [selectedAgentId, setSelectedAgentId] = useState<string>("executive_producer");
  const [copied, setCopied] = useState(false);

  if (!item) return null;

  const currentAgent = AGENTS_LIST.find((a) => a.id === selectedAgentId) || AGENTS_LIST[0];
  const agentData = fullState ? fullState[currentAgent.stateKey] : null;
  const agentOutput = agentData?.output || agentData;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(fullState || item, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-5xl h-[88vh] flex flex-col p-0 gap-0 bg-[#090b14] border-white/10 text-slate-100 overflow-hidden shadow-2xl">
        {/* Header */}
        <DialogHeader className="p-5 border-b border-white/10 bg-white/[0.02] flex flex-row items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <Badge
                variant="outline"
                className="bg-amber-500/10 text-amber-300 border-amber-500/30 uppercase text-[10px] tracking-wider font-semibold"
              >
                {item.format}
              </Badge>
              {"runtime_decided_by_ai" in item && item.runtime_decided_by_ai && (
                <Badge
                  variant="outline"
                  className="bg-cyan-500/10 text-cyan-300 border-cyan-500/30 text-[10px]"
                >
                  AI Runtime: {String(item.runtime_decided_by_ai)}
                </Badge>
              )}
              {"clearance_verdict" in item && item.clearance_verdict && (
                <Badge
                  variant="outline"
                  className="bg-emerald-500/10 text-emerald-300 border-emerald-500/30 text-[10px]"
                >
                  {String(item.clearance_verdict).replace(/_/g, " ")}
                </Badge>
              )}
              <span className="text-xs text-slate-400">ID: {item.project_id}</span>
            </div>
            <DialogTitle className="text-2xl font-bold font-outfit text-white tracking-tight">
              {item.title}
            </DialogTitle>
            {item.logline && (
              <p className="text-xs text-slate-300 mt-1 max-w-2xl line-clamp-2">
                {item.logline}
              </p>
            )}
          </div>
        </DialogHeader>

        {/* Modal Main Body Tabs */}
        <Tabs defaultValue="agents" className="flex-1 flex flex-col min-h-0">
          <div className="px-5 border-b border-white/10 bg-black/20 flex items-center justify-between">
            <TabsList className="bg-transparent h-10 p-0 gap-6">
              <TabsTrigger
                value="agents"
                id="tab-agents-output"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-amber-400 data-[state=active]:text-amber-300 rounded-none h-10 px-1 text-xs font-medium text-slate-400"
              >
                <Bot className="h-3.5 w-3.5 mr-1.5" />
                24 Agents&apos; Outputs
              </TabsTrigger>
              <TabsTrigger
                value="script"
                id="tab-screenplay"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-amber-400 data-[state=active]:text-amber-300 rounded-none h-10 px-1 text-xs font-medium text-slate-400"
              >
                <FileText className="h-3.5 w-3.5 mr-1.5" />
                Screenplay &amp; Scenes
              </TabsTrigger>
              <TabsTrigger
                value="raw"
                id="tab-raw-json"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-amber-400 data-[state=active]:text-amber-300 rounded-none h-10 px-1 text-xs font-medium text-slate-400"
              >
                <Code className="h-3.5 w-3.5 mr-1.5" />
                Full State JSON
              </TabsTrigger>
            </TabsList>

            <Button
              size="sm"
              variant="ghost"
              className="h-7 text-[11px] text-slate-400 hover:text-white"
              onClick={handleCopyJson}
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3 mr-1 text-emerald-400" /> Copied
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3 mr-1" /> Copy JSON
                </>
              )}
            </Button>
          </div>

          {/* TAB 1: 24 AGENTS' OUTPUTS */}
          <TabsContent value="agents" className="flex-1 flex m-0 min-h-0 overflow-hidden">
            {/* Agent Sidebar Navigation */}
            <div className="w-64 border-r border-white/10 bg-black/30 flex flex-col">
              <div className="p-3 border-b border-white/5 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Studio Departments (24 Agents)
              </div>
              <ScrollArea className="flex-1">
                <div className="p-2 space-y-1">
                  {AGENTS_LIST.map((agent) => {
                    const isSelected = selectedAgentId === agent.id;
                    const hasData = fullState && Boolean(fullState[agent.stateKey]);
                    const Icon = agent.icon;
                    return (
                      <button
                        key={agent.id}
                        id={`btn-select-agent-${agent.id}`}
                        onClick={() => setSelectedAgentId(agent.id)}
                        className={`w-full text-left px-2.5 py-2 rounded-lg text-xs flex items-center justify-between transition-all ${
                          isSelected
                            ? "bg-amber-500/20 text-amber-200 border border-amber-500/30"
                            : "text-slate-300 hover:bg-white/5 hover:text-white"
                        }`}
                      >
                        <div className="flex items-center gap-2 truncate">
                          <Icon className={`h-3.5 w-3.5 shrink-0 ${isSelected ? "text-amber-400" : "text-slate-400"}`} />
                          <span className="truncate">{agent.name}</span>
                        </div>
                        {hasData && (
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shrink-0" title="Output Generated" />
                        )}
                      </button>
                    );
                  })}
                </div>
              </ScrollArea>
            </div>

            {/* Agent Output Details */}
            <div className="flex-1 flex flex-col min-h-0 bg-[#090b14]/70">
              <div className="p-4 border-b border-white/10 bg-white/[0.01] flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white font-outfit">
                      {currentAgent.name}
                    </h3>
                    <Badge variant="outline" className="text-[10px] bg-white/5 border-white/10 text-slate-300">
                      {currentAgent.dept}
                    </Badge>
                    {agentData?.success && (
                      <Badge className="bg-emerald-500/20 text-emerald-300 border-emerald-500/30 text-[10px]">
                        Success
                      </Badge>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    State Key: <code className="text-amber-300">{currentAgent.stateKey}</code>
                  </p>
                </div>
              </div>

              <ScrollArea className="flex-1 p-5">
                {isLoading ? (
                  <div className="py-20 text-center text-slate-400 text-xs">
                    Loading agent dossier...
                  </div>
                ) : !agentData ? (
                  <div className="py-16 text-center text-slate-400">
                    <AlertCircle className="h-8 w-8 mx-auto text-slate-500 mb-2" />
                    <p className="text-sm font-semibold">No direct state snapshot recorded for {currentAgent.name}</p>
                    <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                      This agent output is synthesized in the project catalog record or was bypassed during this production cycle.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4 text-xs">
                    {/* Render Formatted Output according to agent type */}
                    <AgentRenderView agentId={currentAgent.id} output={agentOutput} />
                  </div>
                )}
              </ScrollArea>
            </div>
          </TabsContent>

          {/* TAB 2: SCREENPLAY */}
          <TabsContent value="script" className="flex-1 p-6 m-0 overflow-auto bg-[#07080e]">
            {fullState?.screenplay?.output ? (
              <div className="max-w-2xl mx-auto space-y-6 font-mono text-xs text-slate-200 bg-black/60 p-8 rounded-xl border border-white/10 shadow-xl">
                <div className="text-center border-b border-white/10 pb-4 mb-6">
                  <h2 className="text-lg font-bold uppercase tracking-widest text-amber-400">
                    {item.title}
                  </h2>
                  <p className="text-[11px] text-slate-400 mt-1">
                    Written by AI Screenwriter &bull; AI Movie Studio Production
                  </p>
                </div>

                {fullState.screenplay.output.scenes ? (
                  fullState.screenplay.output.scenes.map((scene: any, idx: number) => (
                    <div key={idx} className="space-y-3 pt-4 border-t border-white/5">
                      <div className="font-bold text-amber-300 tracking-wider">
                        SCENE {scene.scene_number || idx + 1}: {scene.slugline || scene.heading || "INT. UNKNOWN - DAY"}
                      </div>
                      {scene.action_description && (
                        <p className="text-slate-300 leading-relaxed italic">
                          {scene.action_description}
                        </p>
                      )}
                      {scene.dialogue && scene.dialogue.map((d: any, dIdx: number) => (
                        <div key={dIdx} className="text-center pt-2">
                          <div className="font-bold text-white tracking-widest uppercase">
                            {d.character_name || d.character}
                          </div>
                          {d.parenthetical && (
                            <div className="text-slate-400 text-[10px]">({d.parenthetical})</div>
                          )}
                          <div className="text-slate-200 mt-1 max-w-md mx-auto">
                            &ldquo;{d.line || d.dialogue}&rdquo;
                          </div>
                        </div>
                      ))}
                    </div>
                  ))
                ) : (
                  <pre className="whitespace-pre-wrap leading-relaxed">
                    {JSON.stringify(fullState.screenplay.output, null, 2)}
                  </pre>
                )}
              </div>
            ) : (
              <div className="py-20 text-center text-slate-400">
                <FileText className="h-8 w-8 mx-auto text-slate-600 mb-2" />
                <p className="text-sm font-semibold">No full screenplay transcript found for this record</p>
                <p className="text-xs text-slate-500 mt-1">
                  Full screenplays are generated during the complete movie workflow run.
                </p>
              </div>
            )}
          </TabsContent>

          {/* TAB 3: RAW STATE JSON */}
          <TabsContent value="raw" className="flex-1 p-4 m-0 overflow-auto bg-[#07080e]">
            <pre className="text-[11px] font-mono text-emerald-400 bg-black/80 p-4 rounded-lg border border-white/5 overflow-auto max-h-full">
              {JSON.stringify(fullState || item, null, 2)}
            </pre>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

// Subcomponent to format and render various agent outputs nicely
function AgentRenderView({ agentId, output }: { agentId: string; output: any }) {
  if (!output) {
    return <div className="text-slate-400">No structured output payload recorded.</div>;
  }

  // Fallback if output is string or simple
  if (typeof output !== "object") {
    return (
      <div className="bg-black/40 p-4 rounded-lg border border-white/10 font-mono text-xs">
        {String(output)}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Key-Value Summary Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {Object.entries(output).map(([key, val]) => {
          if (Array.isArray(val) || typeof val === "object") return null;
          return (
            <div key={key} className="glass-panel p-3 rounded-lg border border-white/5">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                {key.replace(/_/g, " ")}
              </span>
              <span className="text-xs font-medium text-slate-100 mt-0.5 block break-words">
                {String(val)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Arrays or Nested Objects Render */}
      {Object.entries(output).map(([key, val]) => {
        if (!Array.isArray(val) && typeof val !== "object") return null;
        return (
          <div key={key} className="glass-panel p-4 rounded-lg border border-white/5 space-y-2">
            <span className="text-[11px] font-bold text-amber-300 uppercase tracking-wider block">
              {key.replace(/_/g, " ")}
            </span>
            {Array.isArray(val) ? (
              <div className="space-y-2">
                {val.map((item, idx) => (
                  <div key={idx} className="bg-black/30 p-2.5 rounded border border-white/5 text-slate-200">
                    {typeof item === "object" ? (
                      <pre className="text-[11px] font-mono text-slate-300 whitespace-pre-wrap">
                        {JSON.stringify(item, null, 2)}
                      </pre>
                    ) : (
                      <span>&bull; {String(item)}</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <pre className="text-[11px] font-mono bg-black/30 p-2.5 rounded text-slate-300 whitespace-pre-wrap">
                {JSON.stringify(val, null, 2)}
              </pre>
            )}
          </div>
        );
      })}
    </div>
  );
}

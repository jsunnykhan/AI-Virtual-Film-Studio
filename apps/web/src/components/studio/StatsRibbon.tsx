"use client";

import React from "react";
import { Film, CheckCircle2, Bot, Clock, AlertTriangle, Clapperboard } from "lucide-react";
import { StudioStatus } from "@/lib/api";

interface StatsRibbonProps {
  status: StudioStatus | null;
  totalProductions: number;
  totalConcepts: number;
}

export function StatsRibbon({
  status,
  totalProductions,
  totalConcepts,
}: StatsRibbonProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      {/* Total Productions */}
      <div className="glass-panel rounded-xl p-3.5 border border-white/5 relative overflow-hidden group">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium">Productions</span>
          <Film className="h-4 w-4 text-amber-400" />
        </div>
        <div className="text-2xl font-bold text-white font-outfit">
          {totalProductions}
        </div>
        <div className="text-[11px] text-slate-400 mt-0.5">
          Master releases in catalog
        </div>
        <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-amber-500/10 rounded-full blur-xl group-hover:bg-amber-500/20 transition-all"></div>
      </div>

      {/* Autonomous Cycles */}
      <div className="glass-panel rounded-xl p-3.5 border border-white/5 relative overflow-hidden group">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium">Loop Cycles</span>
          <Clapperboard className="h-4 w-4 text-cyan-400" />
        </div>
        <div className="text-2xl font-bold text-white font-outfit">
          #{status?.cycle_count ?? 0}
        </div>
        <div className="text-[11px] text-cyan-300/80 mt-0.5">
          {status?.successful_productions ?? 0} successful / {status?.failed_productions ?? 0} retried
        </div>
        <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-cyan-500/10 rounded-full blur-xl group-hover:bg-cyan-500/20 transition-all"></div>
      </div>

      {/* Active Studio Project */}
      <div className="glass-panel rounded-xl p-3.5 border border-white/5 relative overflow-hidden group">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium">Current Project</span>
          <Clock className="h-4 w-4 text-emerald-400" />
        </div>
        <div className="text-sm font-bold text-white truncate font-outfit" title={status?.current_project_title || "None"}>
          {status?.current_project_title || "Idle / Cooldown"}
        </div>
        <div className="text-[11px] text-emerald-300/80 truncate mt-1" title={status?.current_project_id || "Standby"}>
          {status?.current_project_id ? `${status.current_project_id.slice(0, 16)}...` : "Awaiting next cycle"}
        </div>
        <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-emerald-500/10 rounded-full blur-xl group-hover:bg-emerald-500/20 transition-all"></div>
      </div>

      {/* Creative Concepts */}
      <div className="glass-panel rounded-xl p-3.5 border border-white/5 relative overflow-hidden group">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium">Creative Concepts</span>
          <CheckCircle2 className="h-4 w-4 text-purple-400" />
        </div>
        <div className="text-2xl font-bold text-white font-outfit">
          {totalConcepts}
        </div>
        <div className="text-[11px] text-purple-300/80 mt-0.5">
          Blueprints developed
        </div>
        <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-purple-500/10 rounded-full blur-xl group-hover:bg-purple-500/20 transition-all"></div>
      </div>

      {/* Online Agents */}
      <div className="glass-panel rounded-xl p-3.5 border border-white/5 relative overflow-hidden group col-span-2 md:col-span-1">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-medium">Studio Agents</span>
          <Bot className="h-4 w-4 text-pink-400" />
        </div>
        <div className="text-2xl font-bold text-white font-outfit">
          24 / 24
        </div>
        <div className="text-[11px] text-pink-300/80 mt-0.5">
          8 Departments active
        </div>
        <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-pink-500/10 rounded-full blur-xl group-hover:bg-pink-500/20 transition-all"></div>
      </div>
    </div>
  );
}

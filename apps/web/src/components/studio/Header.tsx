"use client";

import React, { useState } from "react";
import {
  Film,
  Play,
  Pause,
  RotateCw,
  Square,
  Sparkles,
  Clapperboard,
  RefreshCw,
  Activity,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  studioStart,
  studioPause,
  studioResume,
  studioRestart,
  studioStop,
  StudioStatus,
} from "@/lib/api";

interface HeaderProps {
  status: StudioStatus | null;
  onRefresh: () => void;
  onOpenNewProduction: () => void;
  onOpenNewCreative: () => void;
}

export function Header({
  status,
  onRefresh,
  onOpenNewProduction,
  onOpenNewCreative,
}: HeaderProps) {
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleAction = async (
    name: string,
    fn: () => Promise<any>
  ) => {
    try {
      setActionLoading(name);
      await fn();
      setTimeout(onRefresh, 500);
    } catch (err) {
      console.error(`Failed to ${name}:`, err);
    } finally {
      setActionLoading(null);
    }
  };

  const isActive = status?.studio_active_24_7 && !status?.paused;
  const isPaused = status?.studio_active_24_7 && status?.paused;

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-[#090b12]/90 backdrop-blur-md px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Brand & Studio Title */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20 border border-amber-400/30">
            <Film className="h-5 w-5 text-black" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white font-outfit">
                AI Virtual Film Studio
              </h1>
              <Badge
                id="studio-mode-badge"
                variant="outline"
                className="bg-amber-500/10 text-amber-300 border-amber-500/30 text-xs px-2 py-0.5"
              >
                24/7 Autonomous
              </Badge>
            </div>
            <p className="text-xs text-slate-400">
              Autonomous Hollywood Pipeline &bull; 24 Specialized Agents &bull; Continuous Loop
            </p>
          </div>
        </div>

        {/* Real-Time Live Status Pill */}
        <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-full px-4 py-1.5 text-xs">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              {isActive ? (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </>
              ) : isPaused ? (
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
              ) : (
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-slate-500"></span>
              )}
            </span>
            <span className="font-semibold uppercase tracking-wider text-slate-200">
              {isActive ? "Engine Active (24/7)" : isPaused ? "Engine Paused" : "Engine Idle"}
            </span>
          </div>

          <span className="text-white/20">|</span>

          <div className="flex items-center gap-1.5 text-slate-300">
            <Activity className="h-3.5 w-3.5 text-amber-400" />
            <span className="truncate max-w-[200px]" title={status?.current_stage || "idle"}>
              Stage: <strong className="text-amber-300">{status?.current_stage || "standby"}</strong>
            </span>
          </div>

          <span className="text-white/20">|</span>

          <div className="text-slate-300">
            Cycle: <strong className="text-white">#{status?.cycle_count ?? 0}</strong>
          </div>
        </div>

        {/* Engine Controls & Actions */}
        <div className="flex items-center gap-2 flex-wrap">
          {/* Controls: Start / Pause / Resume / Restart / Stop */}
          <div className="flex items-center bg-black/40 border border-white/10 rounded-lg p-1 gap-1">
            {!status?.studio_active_24_7 ? (
              <Button
                id="btn-start-studio"
                size="sm"
                variant="ghost"
                className="h-8 px-2.5 text-xs text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 font-medium"
                onClick={() => handleAction("start", studioStart)}
                disabled={actionLoading !== null}
              >
                <Play className="h-3.5 w-3.5 mr-1 fill-emerald-500" />
                Start
              </Button>
            ) : status?.paused ? (
              <Button
                id="btn-resume-studio"
                size="sm"
                variant="ghost"
                className="h-8 px-2.5 text-xs text-cyan-400 hover:text-cyan-300 hover:bg-cyan-500/10 font-medium"
                onClick={() => handleAction("resume", studioResume)}
                disabled={actionLoading !== null}
              >
                <Play className="h-3.5 w-3.5 mr-1 fill-cyan-500" />
                Resume
              </Button>
            ) : (
              <Button
                id="btn-pause-studio"
                size="sm"
                variant="ghost"
                className="h-8 px-2.5 text-xs text-amber-400 hover:text-amber-300 hover:bg-amber-500/10 font-medium"
                onClick={() => handleAction("pause", studioPause)}
                disabled={actionLoading !== null}
              >
                <Pause className="h-3.5 w-3.5 mr-1" />
                Pause
              </Button>
            )}

            <Button
              id="btn-restart-studio"
              size="sm"
              variant="ghost"
              className="h-8 px-2 text-xs text-purple-400 hover:text-purple-300 hover:bg-purple-500/10 font-medium"
              onClick={() => handleAction("restart", studioRestart)}
              disabled={actionLoading !== null}
              title="Restart 24/7 Engine"
            >
              <RotateCw className="h-3.5 w-3.5" />
            </Button>

            {status?.studio_active_24_7 && (
              <Button
                id="btn-stop-studio"
                size="sm"
                variant="ghost"
                className="h-8 px-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 font-medium"
                onClick={() => handleAction("stop", studioStop)}
                disabled={actionLoading !== null}
                title="Stop 24/7 Engine"
              >
                <Square className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>

          {/* Trigger New Actions */}
          <Button
            id="btn-open-creative"
            size="sm"
            variant="outline"
            className="h-8 text-xs bg-indigo-500/10 border-indigo-500/30 text-indigo-300 hover:bg-indigo-500/20 hover:text-indigo-200"
            onClick={onOpenNewCreative}
          >
            <Sparkles className="h-3.5 w-3.5 mr-1 text-indigo-400" />
            New Concept
          </Button>

          <Button
            id="btn-open-production"
            size="sm"
            className="h-8 text-xs bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-semibold shadow-md shadow-amber-500/20"
            onClick={onOpenNewProduction}
          >
            <Clapperboard className="h-3.5 w-3.5 mr-1" />
            Produce Movie / Series
          </Button>

          <Button
            id="btn-refresh-status"
            size="sm"
            variant="ghost"
            className="h-8 w-8 p-0 text-slate-400 hover:text-white"
            onClick={onRefresh}
            title="Refresh Studio State"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
    </header>
  );
}

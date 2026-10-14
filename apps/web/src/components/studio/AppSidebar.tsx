"use client";

import React, { useState } from "react";
import {
  Film,
  Sparkles,
  Workflow,
  Bot,
  Play,
  Pause,
  RotateCw,
  Square,
  Clapperboard,
  Activity,
  Layers,
  Database,
  Cpu,
  Server,
  Radio,
} from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarRail,
} from "@/components/ui/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  studioStart,
  studioPause,
  studioResume,
  studioRestart,
  studioStop,
  StudioStatus,
} from "@/lib/api";

interface AppSidebarProps {
  status: StudioStatus | null;
  activeTab: "catalog" | "workflows" | "departments";
  setActiveTab: (tab: "catalog" | "workflows" | "departments") => void;
  catalogCount: number;
  conceptsCount: number;
  onRefresh: () => void;
  onOpenNewProduction: () => void;
  onOpenNewCreative: () => void;
}

export function AppSidebar({
  status,
  activeTab,
  setActiveTab,
  catalogCount,
  conceptsCount,
  onRefresh,
  onOpenNewProduction,
  onOpenNewCreative,
}: AppSidebarProps) {
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleAction = async (name: string, fn: () => Promise<any>) => {
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
    <Sidebar collapsible="icon" className="border-r border-white/10 bg-[#070911]">
      {/* Studio Brand Header */}
      <SidebarHeader className="border-b border-white/10 p-4">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20 border border-amber-400/30 shrink-0">
            <Film className="h-5 w-5 text-black" />
          </div>
          <div className="flex flex-col min-w-0 group-data-[collapsible=icon]:hidden">
            <span className="text-sm font-bold font-outfit text-white truncate">
              AI Virtual Film Studio
            </span>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="relative flex h-2 w-2">
                {isActive ? (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </>
                ) : (
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                )}
              </span>
              <span className="text-[10px] text-amber-300 font-medium tracking-wide">
                24/7 Autonomous Engine
              </span>
            </div>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2 py-3 space-y-4">
        {/* Navigation Group: Operations */}
        <SidebarGroup>
          <SidebarGroupLabel className="text-[10px] uppercase font-bold text-slate-400 tracking-wider px-2">
            Studio Operations
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {/* Movies & Series Catalog */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  id="nav-sidebar-catalog"
                  isActive={activeTab === "catalog"}
                  onClick={() => setActiveTab("catalog")}
                  tooltip="Film & Series Catalog"
                  className={activeTab === "catalog" ? "bg-amber-500/15 text-amber-300 font-semibold" : "text-slate-300 hover:text-white"}
                >
                  <Film className="h-4 w-4 text-amber-400" />
                  <span>Film Catalog</span>
                  <Badge variant="outline" className="ml-auto text-[10px] px-1.5 py-0 border-white/10 text-slate-400">
                    {catalogCount}
                  </Badge>
                </SidebarMenuButton>
              </SidebarMenuItem>

              {/* Workflows & DAG */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  id="nav-sidebar-workflows"
                  isActive={activeTab === "workflows"}
                  onClick={() => setActiveTab("workflows")}
                  tooltip="Workflows & State Machine DAG"
                  className={activeTab === "workflows" ? "bg-amber-500/15 text-amber-300 font-semibold" : "text-slate-300 hover:text-white"}
                >
                  <Workflow className="h-4 w-4 text-cyan-400" />
                  <span>Workflows &amp; DAG</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              {/* 24 Agents Directory */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  id="nav-sidebar-departments"
                  isActive={activeTab === "departments"}
                  onClick={() => setActiveTab("departments")}
                  tooltip="24 Agents Directory"
                  className={activeTab === "departments" ? "bg-amber-500/15 text-amber-300 font-semibold" : "text-slate-300 hover:text-white"}
                >
                  <Bot className="h-4 w-4 text-pink-400" />
                  <span>24 Agents Directory</span>
                  <Badge variant="outline" className="ml-auto text-[10px] px-1.5 py-0 border-white/10 text-pink-300/80">
                    24
                  </Badge>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Navigation Group: Engine Live Controls */}
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
          <SidebarGroupLabel className="text-[10px] uppercase font-bold text-slate-400 tracking-wider px-2">
            24/7 Loop Controls
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <div className="bg-white/[0.02] border border-white/5 rounded-xl p-3 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Loop Status:</span>
                <span className="font-semibold text-white">
                  {isActive ? "Running 24/7" : isPaused ? "Paused" : "Idle"}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-white/5 pt-2">
                <span>Cycle:</span>
                <strong className="text-amber-400 font-mono">#{status?.cycle_count ?? 0}</strong>
              </div>

              {/* Control Buttons Grid */}
              <div className="grid grid-cols-2 gap-1.5 pt-1">
                {!status?.studio_active_24_7 ? (
                  <Button
                    id="btn-sidebar-start"
                    size="sm"
                    className="h-7 text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-semibold col-span-2"
                    onClick={() => handleAction("start", studioStart)}
                    disabled={actionLoading !== null}
                  >
                    <Play className="h-3 w-3 mr-1 fill-white" /> Start Loop
                  </Button>
                ) : status?.paused ? (
                  <Button
                    id="btn-sidebar-resume"
                    size="sm"
                    className="h-7 text-xs bg-cyan-600 hover:bg-cyan-500 text-white font-semibold col-span-2"
                    onClick={() => handleAction("resume", studioResume)}
                    disabled={actionLoading !== null}
                  >
                    <Play className="h-3 w-3 mr-1 fill-white" /> Resume Loop
                  </Button>
                ) : (
                  <Button
                    id="btn-sidebar-pause"
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs bg-amber-500/10 border-amber-500/30 text-amber-300 hover:bg-amber-500/20 col-span-2"
                    onClick={() => handleAction("pause", studioPause)}
                    disabled={actionLoading !== null}
                  >
                    <Pause className="h-3 w-3 mr-1" /> Pause Loop
                  </Button>
                )}

                <Button
                  id="btn-sidebar-restart"
                  size="sm"
                  variant="ghost"
                  className="h-7 text-xs text-purple-300 hover:text-white hover:bg-purple-500/10 border border-white/5"
                  onClick={() => handleAction("restart", studioRestart)}
                  disabled={actionLoading !== null}
                  title="Restart Engine"
                >
                  <RotateCw className="h-3 w-3 mr-1" /> Restart
                </Button>

                {status?.studio_active_24_7 && (
                  <Button
                    id="btn-sidebar-stop"
                    size="sm"
                    variant="ghost"
                    className="h-7 text-xs text-red-400 hover:text-white hover:bg-red-500/10 border border-white/5"
                    onClick={() => handleAction("stop", studioStop)}
                    disabled={actionLoading !== null}
                    title="Stop Engine"
                  >
                    <Square className="h-3 w-3 mr-1" /> Stop
                  </Button>
                )}
              </div>
            </div>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Navigation Group: Production Launchers */}
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
          <SidebarGroupLabel className="text-[10px] uppercase font-bold text-slate-400 tracking-wider px-2">
            Launch On-Demand
          </SidebarGroupLabel>
          <SidebarGroupContent className="space-y-2">
            <Button
              id="btn-sidebar-produce"
              size="sm"
              className="w-full h-8 text-xs bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-semibold shadow-md shadow-amber-500/20"
              onClick={onOpenNewProduction}
            >
              <Clapperboard className="h-3.5 w-3.5 mr-1.5" />
              Produce Movie / Series
            </Button>

            <Button
              id="btn-sidebar-concept"
              size="sm"
              variant="outline"
              className="w-full h-8 text-xs bg-purple-500/10 border-purple-500/30 text-purple-300 hover:bg-purple-500/20"
              onClick={onOpenNewCreative}
            >
              <Sparkles className="h-3.5 w-3.5 mr-1.5 text-purple-400" />
              Develop Concept
            </Button>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* Footer System Specs */}
      <SidebarFooter className="border-t border-white/10 p-3 group-data-[collapsible=icon]:hidden text-[11px] text-slate-400 space-y-1">
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Server className="h-3 w-3 text-emerald-400" /> API Server
          </span>
          <span className="font-mono text-emerald-300">Port 8000</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Film className="h-3 w-3 text-amber-400" /> Web Client
          </span>
          <span className="font-mono text-amber-300">Port 3000</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <Database className="h-3 w-3 text-cyan-400" /> Vector Memory
          </span>
          <span className="text-slate-300">pgvector</span>
        </div>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}

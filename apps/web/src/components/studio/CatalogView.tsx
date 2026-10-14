"use client";

import React, { useState } from "react";
import {
  Film,
  Sparkles,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldCheck,
  Video,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CatalogItem, CreativeConceptItem } from "@/lib/api";

interface CatalogViewProps {
  productions: CatalogItem[];
  concepts: CreativeConceptItem[];
  onSelectProject: (item: CatalogItem | CreativeConceptItem) => void;
}

export function CatalogView({
  productions,
  concepts,
  onSelectProject,
}: CatalogViewProps) {
  const [filterType, setFilterType] = useState<"all" | "movie" | "series" | "concepts">("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredProductions = productions.filter((p) => {
    const matchesFilter =
      filterType === "all" ||
      (filterType === "movie" && p.format === "movie") ||
      (filterType === "series" && p.format === "series");

    const matchesSearch =
      searchQuery.trim() === "" ||
      p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.project_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.logline && p.logline.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesFilter && matchesSearch;
  });

  const filteredConcepts = concepts.filter((c) => {
    return (
      searchQuery.trim() === "" ||
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.logline.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.series_premise && c.series_premise.toLowerCase().includes(searchQuery.toLowerCase()))
    );
  });

  return (
    <div className="space-y-6">
      {/* Top Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 glass-panel p-4 rounded-xl border border-white/5">
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto">
          <Button
            id="filter-all"
            size="sm"
            variant={filterType === "all" ? "default" : "ghost"}
            className={`text-xs h-8 ${filterType === "all" ? "bg-amber-500 text-black font-semibold hover:bg-amber-400" : "text-slate-400 hover:text-white"}`}
            onClick={() => setFilterType("all")}
          >
            All Productions ({productions.length})
          </Button>
          <Button
            id="filter-movies"
            size="sm"
            variant={filterType === "movie" ? "default" : "ghost"}
            className={`text-xs h-8 ${filterType === "movie" ? "bg-amber-500 text-black font-semibold hover:bg-amber-400" : "text-slate-400 hover:text-white"}`}
            onClick={() => setFilterType("movie")}
          >
            <Film className="h-3.5 w-3.5 mr-1" />
            Movies
          </Button>
          <Button
            id="filter-series"
            size="sm"
            variant={filterType === "series" ? "default" : "ghost"}
            className={`text-xs h-8 ${filterType === "series" ? "bg-amber-500 text-black font-semibold hover:bg-amber-400" : "text-slate-400 hover:text-white"}`}
            onClick={() => setFilterType("series")}
          >
            <Video className="h-3.5 w-3.5 mr-1" />
            Series
          </Button>
          <Button
            id="filter-concepts"
            size="sm"
            variant={filterType === "concepts" ? "default" : "ghost"}
            className={`text-xs h-8 ${filterType === "concepts" ? "bg-purple-500 text-white font-semibold hover:bg-purple-400" : "text-slate-400 hover:text-white"}`}
            onClick={() => setFilterType("concepts")}
          >
            <Sparkles className="h-3.5 w-3.5 mr-1" />
            Creative Concepts ({concepts.length})
          </Button>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <Input
            id="input-search-catalog"
            placeholder="Search titles, loglines, genres..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-8 text-xs bg-black/40 border-white/10 text-slate-100 placeholder:text-slate-500 focus-visible:ring-amber-500/50"
          />
        </div>
      </div>

      {/* Productions Grid */}
      {filterType !== "concepts" && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 px-1 font-semibold uppercase tracking-wider">
            <span>Studio Master Releases ({filteredProductions.length})</span>
            <span>Autonomously Written &amp; Directed</span>
          </div>

          {filteredProductions.length === 0 ? (
            <div className="glass-panel p-12 text-center rounded-xl border border-white/5 space-y-2">
              <Film className="h-10 w-10 text-slate-600 mx-auto" />
              <p className="text-sm font-semibold text-slate-300">No movies found matching criteria</p>
              <p className="text-xs text-slate-500">
                Trigger a new production or let the 24/7 autonomous loop generate the next feature!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredProductions.map((prod) => (
                <div
                  key={prod.project_id}
                  id={`card-project-${prod.project_id}`}
                  className="glass-card rounded-xl p-5 flex flex-col justify-between border border-white/10 group cursor-pointer"
                  onClick={() => onSelectProject(prod)}
                >
                  <div className="space-y-3">
                    {/* Header Badges */}
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-1.5">
                        <Badge
                          variant="outline"
                          className="bg-amber-500/10 text-amber-300 border-amber-500/30 uppercase text-[10px] font-semibold tracking-wider"
                        >
                          {prod.format}
                        </Badge>
                        {prod.cycle_number && (
                          <Badge variant="outline" className="text-[10px] text-slate-400 border-white/10">
                            Cycle #{prod.cycle_number}
                          </Badge>
                        )}
                      </div>

                      <Badge
                        variant="outline"
                        className="bg-emerald-500/10 text-emerald-300 border-emerald-500/30 text-[10px] flex items-center gap-1"
                      >
                        <ShieldCheck className="h-3 w-3" />
                        Cleared
                      </Badge>
                    </div>

                    {/* Movie Title */}
                    <h3 className="text-lg font-bold font-outfit text-white group-hover:text-amber-300 transition-colors leading-tight">
                      {prod.title}
                    </h3>

                    {/* Logline Preview */}
                    <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                      {prod.logline || "Autonomously generated cinematic narrative developed by the 24 AI studio agents."}
                    </p>

                    {/* Runtime decided dynamically by AI */}
                    {prod.runtime_decided_by_ai && (
                      <div className="text-[11px] text-cyan-300/90 flex items-center gap-1.5 bg-cyan-950/30 border border-cyan-800/30 rounded-md p-2">
                        <Clock className="h-3.5 w-3.5 shrink-0 text-cyan-400" />
                        <span className="truncate">
                          <strong>AI Runtime:</strong> {String(prod.runtime_decided_by_ai)}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Card Footer */}
                  <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="truncate">{new Date(prod.produced_at).toLocaleDateString()}</span>
                    <span className="flex items-center gap-1 text-amber-400 font-semibold group-hover:translate-x-0.5 transition-transform">
                      Inspect 24 Agents <ArrowRight className="h-3 w-3" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Creative Concepts Section */}
      {(filterType === "all" || filterType === "concepts") && (
        <div className="space-y-3 pt-4">
          <div className="flex items-center justify-between text-xs text-purple-300/80 px-1 font-semibold uppercase tracking-wider">
            <span>Creative Development Blueprints ({filteredConcepts.length})</span>
            <span>Idea Generator &bull; Critic &bull; Concept &bull; Research</span>
          </div>

          {filteredConcepts.length === 0 ? (
            <div className="glass-panel p-8 text-center rounded-xl border border-white/5">
              <p className="text-xs text-slate-400">No standalone creative concepts found yet.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredConcepts.map((concept) => (
                <div
                  key={concept.project_id}
                  id={`card-concept-${concept.project_id}`}
                  className="glass-card rounded-xl p-5 flex flex-col justify-between border border-purple-500/20 group cursor-pointer hover:border-purple-500/50"
                  onClick={() => onSelectProject(concept)}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge
                        variant="outline"
                        className="bg-purple-500/10 text-purple-300 border-purple-500/30 text-[10px] font-semibold"
                      >
                        {concept.format} Blueprint
                      </Badge>
                      <Badge
                        variant="outline"
                        className="bg-amber-500/10 text-amber-300 border-amber-500/30 text-[10px]"
                      >
                        Critic: {concept.critic_verdict}
                      </Badge>
                    </div>

                    <h3 className="text-base font-bold font-outfit text-white group-hover:text-purple-300 transition-colors">
                      {concept.title}
                    </h3>

                    <p className="text-xs text-slate-300 line-clamp-3">
                      {concept.logline || concept.series_premise}
                    </p>

                    <div className="flex items-center gap-3 text-[11px] text-slate-400 pt-1">
                      <span>{concept.characters_count} Characters</span>
                      <span>&bull;</span>
                      <span>Research: {concept.research_completed ? "Completed" : "Bypassed"}</span>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-white/5 flex items-center justify-between text-[11px] text-purple-300 font-semibold">
                    <span>{new Date(concept.created_at).toLocaleDateString()}</span>
                    <span className="flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                      View Blueprint <ArrowRight className="h-3 w-3" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

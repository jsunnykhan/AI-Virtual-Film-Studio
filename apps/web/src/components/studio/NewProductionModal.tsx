"use client";

import React, { useState } from "react";
import { Clapperboard, Sparkles, Check, AlertCircle, Loader2 } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { triggerMovieWorkflow } from "@/lib/api";

interface NewProductionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function NewProductionModal({
  isOpen,
  onClose,
  onSuccess,
}: NewProductionModalProps) {
  const [prompt, setPrompt] = useState("");
  const [format, setFormat] = useState("movie");
  const [durationMode, setDurationMode] = useState<"ai" | "custom">("ai");
  const [customMinutes, setCustomMinutes] = useState("10");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        user_request:
          prompt.trim() ||
          "Generate an original cinematic movie or series concept without human boundaries.",
        format,
        target_duration_minutes:
          durationMode === "custom" ? parseFloat(customMinutes) || null : null,
        max_iterations: 3,
      };

      await triggerMovieWorkflow(payload);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to trigger movie production");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && !loading && onClose()}>
      <DialogContent className="max-w-lg bg-[#0a0d18] border-white/10 text-slate-100 shadow-2xl p-6">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-1">
            <div className="h-8 w-8 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Clapperboard className="h-4 w-4" />
            </div>
            <DialogTitle className="text-xl font-bold font-outfit text-white">
              Launch Production
            </DialogTitle>
          </div>
          <p className="text-xs text-slate-400">
            Triggers the full multi-department pipeline through all 24 AI studio agents.
          </p>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          {/* Prompt */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span>Production Prompt / Concept Spark</span>
              <span className="text-[10px] text-slate-500 font-normal">Optional</span>
            </label>
            <textarea
              id="input-production-prompt"
              rows={3}
              placeholder="e.g. A dystopian neo-noir mystery where human memories can be traded as black market currency... (leave blank for autonomous conception)"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-amber-500/50"
            />
          </div>

          {/* Format Selection */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Format</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                id="btn-format-movie"
                onClick={() => setFormat("movie")}
                className={`py-2 px-3 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  format === "movie"
                    ? "bg-amber-500/20 border-amber-500/40 text-amber-300 shadow-sm shadow-amber-500/10"
                    : "bg-white/[0.02] border-white/5 text-slate-400 hover:text-white"
                }`}
              >
                Feature Film / Movie
              </button>
              <button
                type="button"
                id="btn-format-series"
                onClick={() => setFormat("series")}
                className={`py-2 px-3 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  format === "series"
                    ? "bg-amber-500/20 border-amber-500/40 text-amber-300 shadow-sm shadow-amber-500/10"
                    : "bg-white/[0.02] border-white/5 text-slate-400 hover:text-white"
                }`}
              >
                Episodic Series
              </button>
            </div>
          </div>

          {/* Duration Mode */}
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Runtime Decision</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                id="btn-duration-ai"
                onClick={() => setDurationMode("ai")}
                className={`py-2 px-3 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  durationMode === "ai"
                    ? "bg-cyan-500/20 border-cyan-500/40 text-cyan-300"
                    : "bg-white/[0.02] border-white/5 text-slate-400 hover:text-white"
                }`}
              >
                <Sparkles className="h-3 w-3" />
                Decided by AI Agents
              </button>
              <button
                type="button"
                id="btn-duration-custom"
                onClick={() => setDurationMode("custom")}
                className={`py-2 px-3 rounded-lg border text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  durationMode === "custom"
                    ? "bg-cyan-500/20 border-cyan-500/40 text-cyan-300"
                    : "bg-white/[0.02] border-white/5 text-slate-400 hover:text-white"
                }`}
              >
                Custom Minutes
              </button>
            </div>
            {durationMode === "custom" && (
              <Input
                id="input-custom-minutes"
                type="number"
                min="1"
                max="300"
                value={customMinutes}
                onChange={(e) => setCustomMinutes(e.target.value)}
                placeholder="Target runtime in minutes (e.g. 15)"
                className="mt-2 h-8 text-xs bg-black/40 border-white/10"
              />
            )}
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-xs text-red-300 flex items-center gap-2">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onClose}
              disabled={loading}
              className="text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              id="btn-submit-production"
              size="sm"
              disabled={loading}
              className="text-xs bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-black font-semibold"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Agents Orchestrating...
                </>
              ) : (
                <>
                  <Clapperboard className="h-3.5 w-3.5 mr-1.5" />
                  Start Production
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

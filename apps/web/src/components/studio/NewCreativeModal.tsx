"use client";

import React, { useState } from "react";
import { Sparkles, Loader2, AlertCircle } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { triggerCreativeWorkflow } from "@/lib/api";

interface NewCreativeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function NewCreativeModal({
  isOpen,
  onClose,
  onSuccess,
}: NewCreativeModalProps) {
  const [prompt, setPrompt] = useState("");
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
          "Autonomously conceive an original animated sci-fi or fantasy series blueprint.",
        max_iterations: 3,
      };

      await triggerCreativeWorkflow(payload);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to trigger creative workflow");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && !loading && onClose()}>
      <DialogContent className="max-w-lg bg-[#0a0d18] border-white/10 text-slate-100 shadow-2xl p-6">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-1">
            <div className="h-8 w-8 rounded-lg bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Sparkles className="h-4 w-4" />
            </div>
            <DialogTitle className="text-xl font-bold font-outfit text-white">
              Creative Concept Development
            </DialogTitle>
          </div>
          <p className="text-xs text-slate-400">
            Orchestrates Idea Generator &rarr; Executive Producer &rarr; Idea Critic &rarr; Concept Developer &rarr; Research Agent.
          </p>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300 flex items-center justify-between">
              <span>Concept Prompt / Genre Inspiration</span>
              <span className="text-[10px] text-slate-500 font-normal">Optional</span>
            </label>
            <textarea
              id="input-creative-prompt"
              rows={3}
              placeholder="e.g. An underwater steampunk society where deep-sea divers discover forgotten ancient artificial intelligence..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-purple-500/50"
            />
          </div>

          <div className="p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg text-[11px] text-purple-200/90">
            Deliverables include: Complete series premise, main characters dossier with motivations &amp; relationship dynamics, episode engines, season one arc, and research grounding.
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
              id="btn-submit-creative"
              size="sm"
              disabled={loading}
              className="text-xs bg-purple-600 hover:bg-purple-500 text-white font-semibold"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 mr-1.5 animate-spin" />
                  Generating Concept...
                </>
              ) : (
                <>
                  <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                  Develop Blueprint
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

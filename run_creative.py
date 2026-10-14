#!/usr/bin/env python3
"""
CLI script to immediately trigger the Creative Workflow:
Runs: Idea Generator -> Executive Producer -> Idea Critic -> Concept Developer -> Research Agent.
Saves deliverables to output/creative_concepts.json.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
import json
import sys
from uuid import uuid4

from workflows.creative_workflow import build_creative_workflow, save_creative_concept


async def main() -> None:
    prompt = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "Autonomously develop an original cinematic animated movie or series concept."
    )
    project_id = f"creative_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:4]}"

    print("\n" + "=" * 65)
    print("🎬 AI MOVIE STUDIO — CREATIVE WORKFLOW TRIGGER")
    print(f"Project ID: {project_id}")
    print(f"Prompt: {prompt}")
    print("Departments: Idea Generator -> Executive Producer -> Critic -> Concept Developer -> Research")
    print("=" * 65 + "\n")

    workflow = build_creative_workflow()
    initial_state = {
        "project_id": project_id,
        "user_request": prompt,
        "iteration": 0,
        "max_iterations": 3,
        "status": "creative_workflow_started",
    }

    result = await workflow.ainvoke(
        initial_state,
        config={"recursion_limit": 25},
    )

    saved = save_creative_concept(result)

    print("\n" + "=" * 65)
    print("✅ CREATIVE WORKFLOW COMPLETED SUCCESSFULLY!")
    print(f"Title:           {saved.get('title')}")
    print(f"Format:          {saved.get('format')}")
    print(f"Genre:           {', '.join(saved.get('genre', [])) if isinstance(saved.get('genre'), list) else saved.get('genre')}")
    print(f"Logline:         {saved.get('logline')}")
    print(f"Critic Verdict:  {saved.get('critic_verdict')}")
    print(f"Characters:      {saved.get('characters_count')} main characters defined")
    print(f"Research Done:   {saved.get('research_completed')}")
    print(f"Catalog File:    output/creative_concepts.json")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

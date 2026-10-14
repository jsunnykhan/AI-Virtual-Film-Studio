import unittest
from unittest.mock import AsyncMock, patch

from agents.core.states import CreativeWorkflowState
from workflows.creative_workflow import (
    build_creative_workflow,
    route_after_critic,
    route_after_executive_producer,
    route_after_idea_generator,
    save_creative_concept,
)


class TestCreativeWorkflowRouting(unittest.TestCase):

    def test_route_after_idea_generator(self):
        state: CreativeWorkflowState = {"idea": {"success": True}}
        self.assertEqual(route_after_idea_generator(state), "executive_producer")

        state = {"idea": {"success": False}}
        self.assertEqual(route_after_idea_generator(state), "stop")

    def test_route_after_executive_producer_approved(self):
        state: CreativeWorkflowState = {
            "final_decision": {"success": True, "output": {"approved": True}},
            "iteration": 0,
            "max_iterations": 3,
        }
        self.assertEqual(route_after_executive_producer(state), "critic")

    def test_route_after_executive_producer_rejected_retry(self):
        state: CreativeWorkflowState = {
            "final_decision": {"success": True, "output": {"approved": False}},
            "iteration": 0,
            "max_iterations": 3,
        }
        self.assertEqual(route_after_executive_producer(state), "regenerate")

    def test_route_after_executive_producer_max_iterations_proceeds_to_critic(self):
        state: CreativeWorkflowState = {
            "final_decision": {"success": True, "output": {"approved": False}},
            "iteration": 3,
            "max_iterations": 3,
        }
        # Does not halt, proceeds to critic to refine
        self.assertEqual(route_after_executive_producer(state), "critic")

    def test_route_after_critic_verdicts(self):
        # strong_candidate proceeds
        state: CreativeWorkflowState = {
            "critique": {"success": True, "output": {"verdict": "strong_candidate"}},
            "iteration": 0,
            "max_iterations": 3,
        }
        self.assertEqual(route_after_critic(state), "develop")

        # needs_revision proceeds so concept developer can address notes
        state = {
            "critique": {"success": True, "output": {"verdict": "needs_revision"}},
            "iteration": 0,
            "max_iterations": 3,
        }
        self.assertEqual(route_after_critic(state), "develop")

        # weak_candidate retries if iteration < max
        state = {
            "critique": {"success": True, "output": {"verdict": "weak_candidate"}},
            "iteration": 0,
            "max_iterations": 3,
        }
        self.assertEqual(route_after_critic(state), "regenerate")

        # weak_candidate at max iterations develops best draft
        state = {
            "critique": {"success": True, "output": {"verdict": "weak_candidate"}},
            "iteration": 3,
            "max_iterations": 3,
        }
        self.assertEqual(route_after_critic(state), "develop")

    def test_workflow_compilation(self):
        wf = build_creative_workflow()
        self.assertIsNotNone(wf)


if __name__ == "__main__":
    unittest.main()

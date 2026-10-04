import asyncio
import unittest

from agents.core.memory import StudioStore
from agents.creative.concept_developer import concept_developer
from agents.creative.idea_critic import idea_critic
from agents.creative.idea_generator import idea_generator
from db.connection import close_pool
from db.init_db import init_db
from memory.postgres_vector import PostgresVectorStore
from memory.vector_store import get_vector_store
from tools.character import CharacterGetInput, character_get
from tools.movie_bible import MovieBibleSearchInput, movie_bible_search
from tools.registry import build_registry
from tools.shot import ShotCreateInput, shot_create
from workflows.creative_workflow import build_creative_workflow


class TestPostgresVectorStore(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_db()
        self.store = get_vector_store()
        self.project_id = "test_studio_project"
        await self.store.clear(self.project_id)

    async def asyncTearDown(self):
        await self.store.clear(self.project_id)
        await close_pool()

    async def test_implements_studio_store(self):
        self.assertIsInstance(self.store, StudioStore)
        self.assertIsInstance(self.store, PostgresVectorStore)

    async def test_project_summary(self):
        summary_text = "A thrilling cyberpunk animated series about rogue robots."
        await self.store.upsert_project(
            project_id=self.project_id,
            name="Cyberpunk Robots",
            summary=summary_text,
        )

        retrieved = await self.store.get_project_summary(self.project_id)
        self.assertEqual(retrieved, summary_text)

    async def test_canon_upsert_and_retrieval(self):
        char_data = {
            "name": "Kaelen",
            "role": "Rebel Pilot",
            "personality": "Fearless, impulsive, fiercely loyal",
            "goal": "Liberate the neon skyways",
        }

        inserted = await self.store.upsert_canon(
            project_id=self.project_id,
            entity_id="char_kaelen",
            entity_type="character",
            data=char_data,
        )
        self.assertEqual(inserted["id"], "char_kaelen")
        self.assertEqual(inserted["type"], "character")
        self.assertEqual(inserted["data"]["name"], "Kaelen")

        # Single entity lookup
        entity = await self.store.get_canon_entity(
            project_id=self.project_id,
            entity_id="char_kaelen",
            entity_type="character",
        )
        self.assertIsNotNone(entity)
        self.assertEqual(entity["data"]["role"], "Rebel Pilot")

        # Wrong type returns None
        wrong_type = await self.store.get_canon_entity(
            project_id=self.project_id,
            entity_id="char_kaelen",
            entity_type="location",
        )
        self.assertIsNone(wrong_type)

        # Multi-entity lookup
        multi = await self.store.get_canon(
            project_id=self.project_id,
            entity_ids=["char_kaelen", "non_existent"],
        )
        self.assertEqual(len(multi), 1)
        self.assertEqual(multi[0]["id"], "char_kaelen")

    async def test_semantic_vector_search(self):
        # Insert 3 diverse entities
        await self.store.upsert_canon(
            project_id=self.project_id,
            entity_id="robot_orion",
            entity_type="character",
            data={
                "name": "Orion",
                "role": "Autonomous Starship Navigator Robot",
                "personality": "Curious, philosophical AI searching deep space",
                "goal": "Chart uncharted star systems and find ancient relics",
            },
        )

        await self.store.upsert_canon(
            project_id=self.project_id,
            entity_id="bakery_baker",
            entity_type="character",
            data={
                "name": "Pierre",
                "role": "Master Pastry Chef in Paris",
                "personality": "Passionate, jovial baker of baguettes and croissants",
                "goal": "Win the golden rolling pin in the countryside festival",
            },
        )

        await self.store.upsert_canon(
            project_id=self.project_id,
            entity_id="shot_space_flight",
            entity_type="shot",
            data={
                "shot_id": "shot_space_flight",
                "action": "A lone mechanical drone glides past purple nebula clouds and asteroidal rings",
                "camera": "Wide cinematic tracking shot",
                "lighting": "Deep space starlight with neon nebular reflections",
            },
        )

        # Query 1: Vector search for space exploration / robots
        space_results = await self.store.search_canon(
            project_id=self.project_id,
            query="deep space interstellar robot navigation",
            limit=2,
        )
        self.assertGreaterEqual(len(space_results), 1)
        top_id = space_results[0]["id"]
        # Top match must be robot or space flight, NOT the Parisian baker
        self.assertIn(top_id, ["robot_orion", "shot_space_flight"])
        self.assertNotEqual(top_id, "bakery_baker")

        # Query 2: Vector search for bakery / food cooking
        food_results = await self.store.search_canon(
            project_id=self.project_id,
            query="french pastry baking flour croissants kitchen",
            limit=1,
        )
        self.assertEqual(len(food_results), 1)
        self.assertEqual(food_results[0]["id"], "bakery_baker")

        # Query 3: Entity type filtered search
        shot_only = await self.store.search_canon(
            project_id=self.project_id,
            query="drone flight",
            limit=5,
            entity_type="shot",
        )
        for item in shot_only:
            self.assertEqual(item["type"], "shot")

    async def test_agent_runs_history(self):
        # Save results for an agent
        await self.store.save_result(
            project_id=self.project_id,
            agent_id="idea_generator",
            task_id="task_1",
            result={"title": "First Draft", "rating": 5},
        )
        await self.store.save_result(
            project_id=self.project_id,
            agent_id="idea_generator",
            task_id="task_2",
            result={"title": "Second Draft", "rating": 8},
        )

        history = await self.store.get_recent_history(
            project_id=self.project_id,
            agent_id="idea_generator",
            limit=5,
        )
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["task_id"], "task_1")
        self.assertEqual(history[1]["task_id"], "task_2")
        self.assertEqual(history[1]["result"]["title"], "Second Draft")

    async def test_tasks_crud(self):
        task_data = {
            "task_id": "test_task_99",
            "project_id": self.project_id,
            "agent_id": "director",
            "objective": "Plan camera angles for scene 1",
            "status": "in_progress",
        }
        created = await self.store.create_task(task_data)
        self.assertEqual(created["task_id"], "test_task_99")

        retrieved = await self.store.get_task("test_task_99")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["objective"], "Plan camera angles for scene 1")

    async def test_tools_integration(self):
        # Test character tool
        await self.store.upsert_canon(
            project_id=self.project_id,
            entity_id="char_eva",
            entity_type="character",
            data={"name": "Eva", "role": "Commander"},
        )
        char = await character_get(
            self.store,
            CharacterGetInput(project_id=self.project_id, character_id="char_eva"),
        )
        self.assertIsNotNone(char)
        self.assertEqual(char["data"]["name"], "Eva")

        # Test shot create tool
        shot_input = ShotCreateInput(
            project_id=self.project_id,
            shot_id="shot_001",
            scene_id="scene_001",
            duration_sec=3.5,
            characters=["char_eva"],
            action="Eva commands the fleet to engage hyperspace",
            camera={"angle": "extreme_close_up", "lens": "85mm"},
            lighting="Dramatic red cockpit emergency lighting",
        )
        created_shot = await shot_create(self.store, shot_input)
        self.assertEqual(created_shot["id"], "shot_001")

        # Test movie bible search tool via vector search
        search_res = await movie_bible_search(
            self.store,
            MovieBibleSearchInput(
                project_id=self.project_id,
                query="cockpit emergency hyperspace fleet",
                limit=3,
            ),
        )
        self.assertGreaterEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["id"], "shot_001")

    def test_agents_use_vector_store(self):
        self.assertIsInstance(idea_generator.memory, PostgresVectorStore)
        self.assertIsInstance(idea_critic.memory, PostgresVectorStore)
        self.assertIsInstance(concept_developer.memory, PostgresVectorStore)

    def test_creative_workflow_compilation(self):
        workflow = build_creative_workflow()
        self.assertIsNotNone(workflow)


if __name__ == "__main__":
    unittest.main()

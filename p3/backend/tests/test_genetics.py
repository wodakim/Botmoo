import unittest
from simulation import Agent, WorldEngine, ACTION_REPRODUCE, ACTION_EAT, JOB_TRADER
from systems.inventory import Item

class TestGenetics(unittest.TestCase):
    def test_agent_init_genetics(self):
        agent = Agent(0, 0)
        self.assertIn(agent.gender, ["M", "F"])
        self.assertGreater(agent.age, 0)
        self.assertEqual(agent.generation, 1)

    def test_inheritance(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        world.agents = [] # Clear default trader

        father = Agent(0, 0, "Dad")
        father.gender = "M"
        father.clan = "Stark"
        father.generation = 1

        mother = Agent(0, 0, "Mom")
        mother.gender = "F"
        mother.clan = "Lannister"
        mother.generation = 1

        # Manually reproduce
        father.reproduce(mother, world)

        self.assertEqual(len(world.agents), 1)
        child = world.agents[0]

        self.assertEqual(child.age, 0)
        self.assertEqual(child.generation, 2)
        # Patrilineal logic in reproduce()
        self.assertEqual(child.clan, "Stark")

    def test_aging_death(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        elder = Agent(0, 0, "Elder")
        elder.hunger = -5000 # Prevent starvation
        world.agents = [elder]

        elder.age = 50000 # Very old

        # Probabilistic death, try loop
        died = False
        for _ in range(3000): # Should die within ticks if 0.1% chance
            elder.perform_action("idle", world)
            if elder.is_dead:
                died = True
                break

        self.assertTrue(died, "Elder should have died of old age")
        # Check logs for death message
        self.assertTrue(any("old age" in log for log in elder.memory["logs"]))

    def test_reproduction_action(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        m = Agent(5, 5)
        m.gender = "M"
        m.age = 20 * 720
        m.energy = 100
        m.hunger = 0

        f = Agent(5, 6)
        f.gender = "F"
        f.age = 20 * 720
        f.energy = 100
        f.hunger = 0

        world.agents = [m, f]

        # Decide action -> Should want to reproduce
        action = m.decide_action(world)
        self.assertEqual(action, ACTION_REPRODUCE)
        self.assertEqual(m._repro_partner, f)

        # Perform action
        initial_pop = len(world.agents)
        m.perform_action(ACTION_REPRODUCE, world)

        self.assertEqual(len(world.agents), initial_pop + 1)

if __name__ == "__main__":
    unittest.main()

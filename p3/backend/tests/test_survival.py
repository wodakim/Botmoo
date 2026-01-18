import unittest
from simulation import Agent, WorldEngine, ACTION_EAT, ACTION_GATHER, Item

class TestSurvivalFeatures(unittest.TestCase):
    def test_starvation_damage(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        victim = Agent(5, 5, "Starving Victim")
        world.agents = [victim]

        # Set hunger to max
        victim.hunger = victim.max_hunger
        initial_energy = victim.energy

        # Trigger an update (perform action IDLE usually)
        victim.perform_action("idle", world)

        # Should have taken damage
        self.assertLess(victim.energy, initial_energy)
        # Check if "Starving!" message exists in any log entry
        self.assertTrue(any("Starving!" in log for log in victim.memory["logs"]))

    def test_eating_berries(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        eater = Agent(5, 5, "Eater")
        world.agents = [eater]

        eater.hunger = 50
        eater.inventory.add(Item("Berries", "food"))

        self.assertEqual(eater.inventory.count("Berries"), 1)

        eater.perform_action(ACTION_EAT, world)

        self.assertEqual(eater.inventory.count("Berries"), 0)
        self.assertLess(eater.hunger, 50)
        self.assertIn("Ate berries.", eater.memory["logs"][-1])

    def test_foraging_berries(self):
        # This test relies on RNG, so we might need to loop or force seed if possible.
        # Instead, we can mock random or just run enough times?
        # Let's just check if logic exists by forcing success via logic knowledge?
        # No, can't easily force random.random() without mocking.
        # We'll just run loop until success or limit.

        world = WorldEngine(width=10, height=10, num_agents=0)
        gatherer = Agent(5, 5, "Gatherer")
        # Ensure grass
        world.grid[5][5] = "grass"

        found = False
        for _ in range(50):
            gatherer.perform_action(ACTION_GATHER, world)
            if gatherer.inventory.count("Berries") > 0:
                found = True
                break

        self.assertTrue(found, "Should eventually find berries on grass")

if __name__ == "__main__":
    unittest.main()

import unittest
from simulation import Agent, WorldEngine, ACTION_EAT, ACTION_SLEEP, ACTION_ATTACK, TERRAIN_WATER, TERRAIN_FOREST, TERRAIN_GRASS, JOB_GUARD
from systems.inventory import Item

class TestAgentAI(unittest.TestCase):
    def test_initial_state(self):
        agent = Agent(0, 0)
        self.assertEqual(agent.hunger, 0)
        self.assertEqual(agent.energy, 100)
        self.assertEqual(len(agent.memory["hostile_agents"]), 0)

    def test_hunger_logic(self):
        agent = Agent(0, 0)
        agent.hunger = 90
        agent.energy = 50
        agent.inventory.add(Item("Berries", "food")) # Give food
        world = WorldEngine()
        
        # Should prioritize eating
        action = agent.decide_action(world)
        self.assertEqual(action, ACTION_EAT)

    def test_sleep_logic(self):
        agent = Agent(0, 0)
        agent.hunger = 0
        agent.energy = 10
        world = WorldEngine()
        
        # Should prioritize sleeping
        action = agent.decide_action(world)
        self.assertEqual(action, ACTION_SLEEP)
        
    def test_aggression_memory_logic(self):
        # Setup: Agent A is near Agent B
        world = WorldEngine(width=10, height=10, num_agents=0)
        agent_a = Agent(5, 5, "A")
        agent_a.job = JOB_GUARD # Guards are more aggressive
        agent_a.psyche.neuroticism = 0.1 # Low fear, won't flee
        agent_a.psyche.agreeableness = 0.0 # Mean
        agent_a.inventory.equipped["hand"] = Item("Sword", "weapon", 20) # Real Item object
        
        agent_b = Agent(5, 6, "B")
        world.agents = [agent_a, agent_b]
        
        # Force hostility
        agent_a.memory["hostile_agents"].add(agent_b.id)
        
        # Agent A should decide to attack B (Aggression 90 + 20 - 0)
        action = agent_a.decide_action(world)
        self.assertEqual(action, ACTION_ATTACK)
        
        # Perform attack
        initial_energy_b = agent_b.energy
        agent_a.perform_action(ACTION_ATTACK, world)
        
        # Agent B should have taken damage
        self.assertLess(agent_b.energy, initial_energy_b)
        
        # Agent B should now remember A as hostile
        self.assertIn(agent_a.id, agent_b.memory["hostile_agents"])

class TestWorld(unittest.TestCase):
    def test_grid_biomes(self):
        world = WorldEngine(width=20, height=20, num_agents=0)
        terrains = set()
        for row in world.grid:
            for cell in row:
                terrains.add(cell)
        self.assertIn(TERRAIN_GRASS, terrains)

    def test_get_map(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        data = world.get_map()
        self.assertEqual(data["width"], 10)
        self.assertEqual(data["height"], 10)
        self.assertEqual(len(data["grid"]), 10)

if __name__ == '__main__':
    unittest.main()

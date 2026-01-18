import unittest
from simulation import Agent, WorldEngine, ACTION_CRAFT, ACTION_GATHER, TERRAIN_FOREST
from systems.inventory import Item, CraftingSystem

class TestInventory(unittest.TestCase):
    def test_add_remove(self):
        agent = Agent(0, 0)
        item = Item("Wood", "resource")
        self.assertTrue(agent.inventory.add(item))
        self.assertEqual(len(agent.inventory.items), 1)
        self.assertTrue(agent.inventory.remove("Wood"))
        self.assertEqual(len(agent.inventory.items), 0)

    def test_crafting_logic(self):
        agent = Agent(0, 0)
        # Add 3 Wood
        for _ in range(3):
            agent.inventory.add(Item("Wood", "resource"))
        
        self.assertTrue(CraftingSystem.can_craft(agent.inventory, "Spear"))
        self.assertTrue(CraftingSystem.craft(agent.inventory, "Spear"))
        
        # Should have consumed wood and gained spear
        self.assertEqual(agent.inventory.count("Wood"), 0)
        self.assertEqual(agent.inventory.count("Spear"), 1)

    def test_equip(self):
        agent = Agent(0, 0)
        spear = Item("Spear", "weapon", 15)
        agent.inventory.add(spear)
        agent.inventory.equip(spear, "hand")
        
        self.assertEqual(agent.inventory.equipped["hand"], spear)
        self.assertNotIn(spear, agent.inventory.items)

class TestPsychology(unittest.TestCase):
    def test_sanity_loss(self):
        agent = Agent(0, 0)
        initial_sanity = agent.psyche.sanity
        agent.log_event("Test Trauma", -10)
        self.assertLess(agent.psyche.sanity, initial_sanity)

if __name__ == '__main__':
    unittest.main()

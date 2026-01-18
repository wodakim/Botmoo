import unittest
from simulation import Agent, WorldEngine, ACTION_ATTACK, ACTION_TRADE, JOB_TRADER, JOB_THIEF, Corpse
from systems.inventory import Item

class TestDeltaFeatures(unittest.TestCase):
    def test_combat_damage(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        attacker = Agent(5, 5, "Attacker")
        victim = Agent(5, 5, "Victim")
        world.agents = [attacker, victim]
        
        initial_hp = victim.energy
        attacker.inventory.equipped["hand"] = Item("Sword", "weapon", 20)
        
        # Force hit (bypass random)
        # We test take_damage directly to avoid random RNG in perform_action
        victim.take_damage(20, attacker, world)
        
        self.assertLess(victim.energy, initial_hp)
        self.assertIn(attacker.id, victim.memory["hostile_agents"])

    def test_death_and_corpse(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        victim = Agent(5, 5, "Victim")
        victim.inventory.add(Item("Gold", "resource", 0, 100))
        world.agents = [victim]
        
        killer = Agent(5, 6, "Killer")
        victim.die(world, killer)
        
        self.assertTrue(victim.is_dead)
        self.assertEqual(len(world.corpses), 1)
        self.assertEqual(world.corpses[0].inventory.items[0].name, "Gold")

    def test_trade_logic(self):
        world = WorldEngine(width=10, height=10, num_agents=0)
        trader = Agent(5, 5, "Trader", JOB_TRADER)
        seller = Agent(5, 6, "Seller")
        seller.inventory.add(Item("Sword", "weapon", 30, 50))
        
        world.agents = [trader, seller]
        
        # Setup Seller to trade
        seller._trade_target = trader
        seller.perform_action("trade", world)
        
        # Seller should have Gold, Trader should have Sword
        self.assertEqual(seller.inventory.gold, 50)
        self.assertEqual(trader.inventory.items[0].name, "Sword")

if __name__ == "__main__":
    unittest.main()

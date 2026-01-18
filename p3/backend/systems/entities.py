from typing import List, Dict

class Clan:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.members = []
        self.enemies = []

    def add_member(self, agent_id):
        self.members.append(agent_id)

    def is_enemy(self, other_clan_name):
        return other_clan_name in self.enemies

    def declare_war(self, other_clan_name):
        if other_clan_name not in self.enemies:
            self.enemies.append(other_clan_name)

class Corpse:
    def __init__(self, x, y, name, inventory, killer_id=None):
        self.x = x
        self.y = y
        self.name = f"Corpse of {name}"
        self.inventory = inventory
        self.killer_id = killer_id
        self.decay = 100 # ticks before disappearing

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "name": self.name,
            "inventory": self.inventory.to_dict(),
            "decay": self.decay
        }

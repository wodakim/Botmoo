from typing import List, Dict, Optional

class Item:
    def __init__(self, name: str, item_type: str, power: float = 0, value: int = 0):
        self.name = name
        self.type = item_type # "resource", "weapon", "armor"
        self.power = power
        self.value = value

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "power": self.power,
            "value": self.value
        }

class Inventory:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.items: List[Item] = []
        self.gold = 0
        self.equipped: Dict[str, Optional[Item]] = {
            "hand": None,
            "body": None
        }

    def add(self, item: Item):
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False
        
    def remove(self, item_name: str, count=1):
        removed = 0
        to_remove = []
        for i in self.items:
            if i.name == item_name and removed < count:
                to_remove.append(i)
                removed += 1
        
        if removed == count:
            for i in to_remove:
                self.items.remove(i)
            return True
        return False

    def count(self, item_name: str):
        return sum(1 for i in self.items if i.name == item_name)

    def equip(self, item: Item, slot: str):
        if slot in self.equipped:
            if self.equipped[slot]:
                self.add(self.equipped[slot]) # Unequip old
            self.equipped[slot] = item
            if item in self.items:
                self.items.remove(item)

    def to_dict(self):
        return {
            "items": [i.to_dict() for i in self.items],
            "gold": self.gold,
            "equipped": {k: (v.to_dict() if v else None) for k, v in self.equipped.items()}
        }

class CraftingSystem:
    RECIPES = {
        "Spear": {"cost": {"Wood": 3}, "result": Item("Spear", "weapon", 15, 10)},
        "Tunic": {"cost": {"Fiber": 3}, "result": Item("Tunic", "armor", 10, 15)},
        "Club": {"cost": {"Wood": 2}, "result": Item("Club", "weapon", 10, 5)},
        "Sword": {"cost": {"Ore": 2}, "result": Item("Sword", "weapon", 30, 50)},
    }

    @staticmethod
    def can_craft(inventory: Inventory, item_name: str):
        if item_name not in CraftingSystem.RECIPES: return False
        recipe = CraftingSystem.RECIPES[item_name]
        for mat, count in recipe["cost"].items():
            if inventory.count(mat) < count:
                return False
        return True

    @staticmethod
    def craft(inventory: Inventory, item_name: str):
        if not CraftingSystem.can_craft(inventory, item_name): return False
        
        recipe = CraftingSystem.RECIPES[item_name]
        # Consume materials
        for mat, count in recipe["cost"].items():
            inventory.remove(mat, count)
        
        # Add result
        # We need to create a new Item instance, otherwise we might share references if we just used the recipe result directly
        result_proto = recipe["result"]
        new_item = Item(result_proto.name, result_proto.type, result_proto.power, result_proto.value)
        inventory.add(new_item)
        return True

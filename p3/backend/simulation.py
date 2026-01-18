import random
import uuid
import math
import logging
from systems.psychology import Psychology, EpisodicMemory
from systems.inventory import Inventory, Item, CraftingSystem
from systems.memetics import MemeticHost, LanguageEngine
from systems.entities import Corpse, Clan

logger = logging.getLogger(__name__)

# --- Enums / Constants ---
GRID_SIZE = 64
TERRAIN_GRASS = "grass"
TERRAIN_WALL = "wall"
TERRAIN_WATER = "water"
TERRAIN_FOREST = "forest"

ACTION_MOVE = "move"
ACTION_EAT = "eat"
ACTION_SLEEP = "sleep"
ACTION_IDLE = "idle"
ACTION_ATTACK = "attack"
ACTION_GATHER = "gather"
ACTION_CRAFT = "craft"
ACTION_TRADE = "trade"
ACTION_STEAL = "steal"
ACTION_BUILD = "build"
ACTION_REPRODUCE = "reproduce"

JOB_LUMBERJACK = "lumberjack"
JOB_GUARD = "guard"
JOB_GATHERER = "gatherer"
JOB_BLACKSMITH = "blacksmith"
JOB_THIEF = "thief"
JOB_TRADER = "trader"
JOB_MONSTER = "monster"

# Configuration for Time
TICKS_PER_HOUR = 30 # 0.5s * 30 = 15s per hour. Day = 15s * 24 = 6 minutes.

# --- Models ---

class Agent:
    def __init__(self, x, y, name="Bot", job=None):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.x = x
        self.y = y
        self.job = job if job else random.choice([JOB_LUMBERJACK, JOB_GUARD, JOB_GATHERER, JOB_BLACKSMITH, JOB_THIEF])
        self.color = self._get_job_color()
        self.clan = None
        self.gender = random.choice(["M", "F"])
        self.age = 20 * 720 # Start at 20 years old (approx)
        self.generation = 1
        self.is_dead = False
        
        # Core Systems
        self.psyche = Psychology()
        self.inventory = Inventory()
        self.memetics = MemeticHost(self.psyche.openness)
        
        # Stats
        self.hunger = 0
        self.energy = 100
        self.max_hunger = 100
        self.max_energy = 100
        
        self.speech_cooldown = 0
        
        self.memory = {
            "hostile_agents": set(),
            "last_action": None,
            "logs": [], 
            "episodes": []
        }
        self.current_speech = None
        self.speech_tick = 0
        self._current_target = None
        self._craft_target = None
        self._trade_target = None
        self._repro_partner = None

    def reproduce(self, partner, world):
        if not partner: return

        child_name = f"Child-{world.tick_count}"
        child = Agent(self.x, self.y, child_name)
        child.age = 0
        child.generation = max(self.generation, partner.generation) + 1
        child.clan = self.clan if self.gender == "M" else partner.clan
        child.color = self.color # Simplified inheritance

        # Mix traits
        for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
            val1 = getattr(self.psyche, trait)
            val2 = getattr(partner.psyche, trait)
            new_val = (val1 + val2) / 2.0 + random.uniform(-0.1, 0.1)
            setattr(child.psyche, trait, max(0.0, min(1.0, new_val)))

        world._place_agent(child)
        world.agents.append(child)
        world.broadcast_event(f"A baby was born: {child.clan} clan!")

    def _get_job_color(self):
        if self.job == JOB_LUMBERJACK: return "#8D6E63" 
        if self.job == JOB_GUARD: return "#5C6BC0"      
        if self.job == JOB_GATHERER: return "#66BB6A"
        if self.job == JOB_BLACKSMITH: return "#424242"
        if self.job == JOB_THIEF: return "#212121"
        if self.job == JOB_TRADER: return "#FFD700"
        if self.job == JOB_MONSTER: return "#FF0000"
        return "#BDBDBD"

    def calculate_prestige(self):
        score = len(self.inventory.items)
        if self.inventory.equipped["hand"]: score += 5
        if self.inventory.equipped["body"]: score += 3
        score += (self.energy / 20)
        return score / 100.0 

    def log_event(self, message, emotional_weight=0, event_type="neutral", tick=0):
        self.memory["logs"].append(message)
        if len(self.memory["logs"]) > 10:
            self.memory["logs"].pop(0)
            
        episode = EpisodicMemory(tick, event_type, message, emotional_weight)
        self.memory["episodes"].append(episode)
        
        if emotional_weight < -2:
            self.psyche.update_sanity(emotional_weight)
        elif emotional_weight > 2:
            self.psyche.update_sanity(emotional_weight * 0.5)

    def say(self, sentiment, tick_now, world, context_action=None, context_target=None):
        if self.speech_cooldown > 0 and sentiment != "pain": return # Pain overrides cooldown
        if self.job == JOB_MONSTER: return

        text = ""
        meme = None

        # Procedural Generation (Priority)
        if context_action:
             target_name = context_target.name if context_target else None
             if sentiment == "neutral" and random.random() < 0.5:
                 text = LanguageEngine.generate_sentence("self", context_action, target_name, sentiment)
             elif sentiment == "hostile":
                 text = LanguageEngine.generate_sentence("self", "attack", target_name, "hostile")

        # Fallback to Memetics
        if not text:
            if self.psyche.sanity < 30 and random.random() < 0.4:
                text = "..."
            else:
                meme = self.memetics.express(sentiment)
                if not meme: return
                text = meme.text

        self.current_speech = text
        self.speech_tick = tick_now
        self.speech_cooldown = 20 # 10s silence
        
        if meme:
            self._broadcast_meme(meme, world)

    def _broadcast_meme(self, meme, world):
        if not meme: return
        prestige = len(self.inventory.items) / 10.0
        nearby = self._get_nearby_agents(world, radius=5)
        for other in nearby:
            if other.job == JOB_MONSTER: continue
            infected = other.memetics.expose(meme, prestige)
            if infected:
                other.log_event(f"Learned '{meme.text}' from {self.name}", 0.5, "learning", world.tick_count)

    def decide_action(self, world):
        if self.is_dead: return ACTION_IDLE
        if self.speech_cooldown > 0: self.speech_cooldown -= 1

        scores = {
            ACTION_MOVE: 0, ACTION_EAT: 0, ACTION_SLEEP: 0, ACTION_IDLE: 0,
            ACTION_ATTACK: 0, ACTION_GATHER: 0, ACTION_CRAFT: 0,
            ACTION_TRADE: 0, ACTION_STEAL: 0, ACTION_BUILD: 0,
            ACTION_REPRODUCE: 0
        }
        
        nearby_agents = self._get_nearby_agents(world)
        nearby_hostiles = [a for a in nearby_agents if a.id in self.memory["hostile_agents"] or a.job == JOB_MONSTER]
        
        # ADHD: Chance to be distracted and pick random action or just move
        if "adhd" in self.psyche.disorders and random.random() < 0.2:
             return random.choice([ACTION_MOVE, ACTION_IDLE, ACTION_GATHER])

        # Chat (Increased probability slightly, controlled by cooldown)
        if "schizophrenia" in self.psyche.disorders and random.random() < 0.1:
             self.say(random.choice(["fearful", "hostile", "neutral"]), world.tick_count, world)
        elif nearby_hostiles and random.random() < 0.3:
             self.say("hostile", world.tick_count, world, context_action="attack", context_target=nearby_hostiles[0])
        elif nearby_agents and random.random() < 0.2:
             self.say("friendly", world.tick_count, world)

        # 1. Survival
        scores[ACTION_EAT] = (self.hunger / self.max_hunger) * 100
        scores[ACTION_SLEEP] = ((self.max_energy - self.energy) / self.max_energy) * 100
        
        # Hunger override: if no food, prioritize gathering/work (desperation)
        has_food = self.inventory.count("Berries") > 0
        if self.hunger > 50 and not has_food:
             scores[ACTION_EAT] = 0 # Can't eat air
             scores[ACTION_GATHER] = 50 + (self.hunger / 2) # Desperate for food

        # Day/Night Cycle Logic
        is_night = world.is_night()
        if is_night:
            scores[ACTION_SLEEP] += 20 
            scores[ACTION_MOVE] -= 10  
            if self.psyche.neuroticism > 0.5:
                scores[ACTION_SLEEP] += 20 
        
        # Monster Logic
        if self.job == JOB_MONSTER:
            scores[ACTION_EAT] = 0
            scores[ACTION_SLEEP] = 0
            if is_night:
                scores[ACTION_MOVE] = 50
                scores[ACTION_ATTACK] = 100 if nearby_agents else 0
            else:
                scores[ACTION_IDLE] = 100 
            
            living_targets = [a for a in nearby_agents if not a.is_dead and a.job != JOB_MONSTER]
            self._current_target = living_targets[0] if living_targets else None
            return max(scores, key=scores.get)

        # 2. Combat / Danger
        combat_power = self.inventory.equipped["hand"].power if self.inventory.equipped["hand"] else 0
        confidence = 1.0 if (combat_power > 10 or self.job == JOB_GUARD) else 0.2
        if self.psyche.neuroticism > 0.7: confidence *= 0.5

        if "sociopathy" in self.psyche.disorders:
            confidence = 1.5 # Overconfident/Callous

        if nearby_hostiles:
            if "fear" in self.psyche.disorders:
                scores[ACTION_MOVE] += 100 # Flee!
            else:
                scores[ACTION_ATTACK] = 90 * confidence
        elif nearby_agents:
            if self.job == JOB_GUARD:
                for n in nearby_agents:
                    if n.job == JOB_THIEF or n.job == JOB_MONSTER: scores[ACTION_ATTACK] = 80
            elif self.job == JOB_THIEF:
                scores[ACTION_STEAL] = 60
            elif "paranoia" in self.psyche.disorders:
                scores[ACTION_ATTACK] = 50 * confidence
            elif "sociopathy" in self.psyche.disorders:
                 # Sociopaths might attack for gain or no reason
                 if random.random() < 0.1: scores[ACTION_ATTACK] = 60

        # 3. Economy (Trade)
        self._trade_target = None
        traders = [a for a in nearby_agents if a.job == JOB_TRADER]
        if traders and len(self.inventory.items) > 5 and not is_night:
            scores[ACTION_TRADE] = 70
            self._trade_target = traders[0]

        # Reproduction
        self._repro_partner = None
        if self.age > 18 * 720 and self.energy > 80 and self.hunger < 20:
             potential_partners = [a for a in nearby_agents if a.gender != self.gender and a.age > 18 * 720]
             if potential_partners:
                 scores[ACTION_REPRODUCE] = 80
                 self._repro_partner = potential_partners[0]
        
        # 4. Work
        scores[ACTION_MOVE] = 20
        scores[ACTION_IDLE] = 5
        
        terrain = world.get_terrain(self.x, self.y)
        self._craft_target = None

        # Construction Logic
        if self.inventory.count("Wood") >= 5 and terrain == TERRAIN_GRASS:
             # Builders want to build walls
             if self.job == JOB_LUMBERJACK or self.job == JOB_BLACKSMITH:
                 scores[ACTION_BUILD] = 65

        if not is_night: 
            if self.job == JOB_LUMBERJACK:
                if terrain == TERRAIN_FOREST: scores[ACTION_GATHER] = 40
                else: scores[ACTION_MOVE] += 10
            elif self.job == JOB_BLACKSMITH:
                if self.inventory.count("Ore") >= 2:
                    if CraftingSystem.can_craft(self.inventory, "Sword"):
                        self._craft_target = "Sword"
                        scores[ACTION_CRAFT] = 80
                elif terrain == TERRAIN_WALL: 
                    scores[ACTION_GATHER] = 40
                else:
                    scores[ACTION_MOVE] += 10 
            elif self.job == JOB_GATHERER:
                scores[ACTION_GATHER] = 30
        
        # Gatherer override: If hungry, gather!
        if self.hunger > 50 and not has_food:
             scores[ACTION_GATHER] = max(scores[ACTION_GATHER], 60)

        if self.inventory.equipped["hand"] is None:
             if CraftingSystem.can_craft(self.inventory, "Spear"):
                 self._craft_target = "Spear"
                 scores[ACTION_CRAFT] = 75

        best_action = max(scores, key=scores.get)
        
        if best_action == ACTION_ATTACK and self.job != JOB_MONSTER:
            self._current_target = nearby_hostiles[0] if nearby_hostiles else (nearby_agents[0] if nearby_agents else None)
        elif best_action == ACTION_STEAL:
            self._current_target = nearby_agents[0] if nearby_agents else None

        return best_action

    def perform_action(self, action, world):
        self.memory["last_action"] = action
        tick = world.tick_count
        self.age += 1 # Age naturally
        
        # Natural Death (Approx 60 "days")
        if self.age > 60 * 720 and random.random() < 0.001:
            self.log_event("Died of old age.", -10, "death", tick)
            self.die(world, None)
            return

        if action == ACTION_MOVE:
            self._move_randomly(world)
            self.energy = max(0, self.energy - 1)
            # Hunger grows slower now (1.5s per tick is gone, but we want 6m cycle)
            if tick % 5 == 0: self.hunger = min(self.max_hunger, self.hunger + 1)
            
        elif action == ACTION_EAT:
            if self.inventory.count("Berries") > 0:
                self.inventory.remove("Berries", 1)
                self.hunger = max(0, self.hunger - 30)
                self.energy = max(0, self.energy - 1)
                self.log_event("Ate berries.", 2, "survival", tick)
            else:
                 self.log_event("No food to eat!", -1, "fail", tick)

        elif action == ACTION_GATHER:
            self.energy = max(0, self.energy - 2)
            if tick % 5 == 0: self.hunger = min(self.max_hunger, self.hunger + 2)
            terrain = world.get_terrain(self.x, self.y)
            
            loot = None
            if self.job == JOB_BLACKSMITH and terrain == TERRAIN_WALL:
                loot = "Ore"
            elif terrain == TERRAIN_FOREST:
                loot = "Wood"
            
            # Forage for berries (Everyone can do it on Grass/Forest)
            found_food = False
            if terrain == TERRAIN_FOREST or terrain == TERRAIN_GRASS:
                 if random.random() < 0.3: # 30% chance for food
                     self.inventory.add(Item("Berries", "food", 0, 2))
                     self.log_event("Found Berries!", 2, "survival", tick)
                     found_food = True

            if loot and random.random() < 0.6:
                val = 3 if loot == "Wood" else 8
                self.inventory.add(Item(loot, "resource", 0, val))
                self.log_event(f"Gathered {loot}.", 1, "work", tick)
            elif not found_food:
                self.log_event("Failed gather.", 0, "work", tick)

        elif action == ACTION_CRAFT:
            target = self._craft_target
            if target and CraftingSystem.craft(self.inventory, target):
                self.log_event(f"Crafted {target}!", 5, "achievement", tick)
            else:
                self.log_event("Failed craft.", -1, "fail", tick)

        elif action == ACTION_BUILD:
             if self.inventory.count("Wood") >= 5:
                 self.inventory.remove("Wood", 5)
                 world.set_terrain(self.x, self.y, TERRAIN_WALL)
                 self.log_event("Built a wall.", 5, "achievement", tick)
                 self.say("neutral", tick, world, "craft", Item("Wall", "build"))
             else:
                 self.log_event("Not enough wood to build.", 0, "fail", tick)

        elif action == ACTION_REPRODUCE:
             if self._repro_partner:
                 self.reproduce(self._repro_partner, world)
                 self.energy -= 30
                 self.log_event("Started a family.", 10, "joy", tick)
                 self.say("friendly", tick, world)

        elif action == ACTION_SLEEP:
            self.energy = min(self.max_energy, self.energy + 5) # Slower regen
            if tick % 10 == 0: self.hunger = min(self.max_hunger, self.hunger + 1)
            
        elif action == ACTION_ATTACK:
            target = self._current_target
            if target:
                # Combat Logic
                base_dmg = 10
                weapon = self.inventory.equipped["hand"]
                if weapon: base_dmg += weapon.power
                if self.job == JOB_GUARD or self.job == JOB_MONSTER: base_dmg += 5
                if self.job == JOB_MONSTER: base_dmg = 20

                # Hit Chance (Agility vs Agility approximation)
                hit_chance = 0.7 + ((self.energy - target.energy) / 200.0)

                outcome = "hit"
                if random.random() > hit_chance:
                    outcome = "miss"
                elif random.random() < 0.1: # 10% Dodge chance
                    outcome = "dodge"
                elif target.inventory.equipped["hand"] and random.random() < 0.15: # Parry chance if armed
                    outcome = "parry"

                if outcome == "hit":
                    # Critical?
                    is_crit = random.random() < 0.1
                    final_dmg = base_dmg * 1.5 if is_crit else base_dmg

                    target.take_damage(final_dmg, self, world)

                    # Visual & Log
                    crit_str = " CRITICAL!" if is_crit else ""
                    self.log_event(f"Hit {target.name}{crit_str}", 2, "combat", tick)
                    self.current_speech = f"Take that! ({int(final_dmg)} dmg)" if self.job != JOB_MONSTER else "ROAR!"
                    self.speech_tick = tick

                elif outcome == "miss":
                    self.log_event(f"Missed {target.name}!", -1, "combat", tick)
                    self.current_speech = "Damn, missed!"
                    self.speech_tick = tick

                elif outcome == "dodge":
                    self.log_event(f"{target.name} dodged!", -1, "combat", tick)
                    target.current_speech = "Too slow!"
                    target.speech_tick = tick

                elif outcome == "parry":
                    self.log_event(f"{target.name} parried!", -1, "combat", tick)
                    target.current_speech = "Blocked!"
                    target.speech_tick = tick

                self.energy = max(0, self.energy - 5)

        elif action == ACTION_TRADE:
            target = self._trade_target
            if target:
                if self.inventory.items:
                    item = self.inventory.items.pop()
                    self.inventory.gold += item.value
                    target.inventory.add(item) 
                    target.inventory.gold -= item.value
                    self.log_event(f"Sold {item.name}", 2, "trade", tick)

        elif action == ACTION_IDLE:
             self.energy = max(0, self.energy - 0.5)
             if tick % 10 == 0: self.hunger = min(self.max_hunger, self.hunger + 0.5)
             
             # Flavor logs for liveliness
             if random.random() < 0.05:
                 flavors = ["Whistling a tune.", "Watching the sky.", "Thinking about life.", "Kicking a stone.", "Adjusting gear."]
                 self.log_event(random.choice(flavors), 0, "idle", tick)

             if self.job == JOB_MONSTER and not world.is_night():
                 self.take_damage(20, self, world)

        # Starvation Check
        if self.hunger >= self.max_hunger and self.job != JOB_MONSTER:
             self.take_damage(1, self, world) # Starve slowly
             if tick % 5 == 0: self.log_event("Starving!", -5, "pain", tick)

    def take_damage(self, amount, attacker, world):
        self.energy = max(0, self.energy - amount)
        if attacker != self:
            self.memory["hostile_agents"].add(attacker.id)
        
        self.log_event(f"Hurt by {attacker.name}!", -5, "pain", world.tick_count)
        
        if self.energy <= 0:
            self.die(world, attacker)

    def die(self, world, killer):
        self.is_dead = True
        corpse = Corpse(self.x, self.y, self.name, self.inventory, killer.id if killer else None)
        world.add_corpse(corpse)
        msg = f"{self.name} died."
        if killer and killer != self: msg = f"{self.name} killed by {killer.name}!"
        world.broadcast_event(msg)

    def _move_randomly(self, world):
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < world.width and 0 <= new_y < world.height:
            if not world.is_blocked(new_x, new_y):
                self.x = new_x
                self.y = new_y

    def _get_nearby_agents(self, world, radius=4):
        nearby = []
        for other in world.agents:
            if other.id == self.id or other.is_dead: continue
            dist = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
            if dist <= radius:
                nearby.append(other)
        return nearby

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "job": self.job,
            "is_dead": self.is_dead,
            "stats": {"hunger": self.hunger, "energy": self.energy},
            "inventory": self.inventory.to_dict(),
            "speech": {"text": self.current_speech, "tick": self.speech_tick},
            "genetics": {"gender": self.gender, "clan": self.clan, "age": self.age}
        }


class WorldEngine:
    def __init__(self, width=GRID_SIZE, height=GRID_SIZE, num_agents=10):
        self.width = width
        self.height = height
        self.tick_count = 0
        self.time_of_day = 8 # Start at 8:00
        self.grid = self._generate_biomes()
        self.agents = []
        self.corpses = []
        self.events = []
        self.clan_names = ["Stark", "Lannister", "Wayne", "Doe", "Smith"]
        self._spawn_agents(num_agents)

    def is_night(self):
        return self.time_of_day >= 22 or self.time_of_day < 6

    def _generate_biomes(self):
        grid = [[TERRAIN_GRASS for _ in range(self.width)] for _ in range(self.height)]
        def grow_region(terrain_type, count, min_size, max_size):
            for _ in range(count):
                cx = random.randint(0, self.width - 1)
                cy = random.randint(0, self.height - 1)
                size = random.randint(min_size, max_size)
                for _ in range(size * 4): 
                    ox = random.randint(-int(math.sqrt(size)), int(math.sqrt(size)))
                    oy = random.randint(-int(math.sqrt(size)), int(math.sqrt(size)))
                    nx, ny = cx + ox, cy + oy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        grid[ny][nx] = terrain_type
        grow_region(TERRAIN_WATER, 3, 20, 50)
        grow_region(TERRAIN_FOREST, 6, 10, 30)
        for _ in range(5):
            cx = random.randint(0, self.width - 1)
            cy = random.randint(0, self.height - 1)
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            length = random.randint(5, 15)
            for i in range(length):
                nx, ny = cx + dx*i, cy + dy*i
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    grid[ny][nx] = TERRAIN_WALL
        return grid

    def _spawn_agents(self, count):
        for i in range(1):
            agent = Agent(0, 0, f"Trader-{i}", JOB_TRADER)
            agent.inventory.gold = 500
            self._place_agent(agent)
            self.agents.append(agent)
            
        for i in range(count):
            name = f"Citoyen-{i}"
            agent = Agent(0, 0, name)
            agent.clan = random.choice(self.clan_names)
            agent.name = f"{name} {agent.clan}"
            self._place_agent(agent)
            self.agents.append(agent)

    def _spawn_monster(self):
        monsters = len([a for a in self.agents if a.job == JOB_MONSTER and not a.is_dead])
        if monsters < 3:
            monster = Agent(0, 0, "Nightmare", JOB_MONSTER)
            monster.energy = 200 
            self._place_agent(monster)
            self.agents.append(monster)
            self.broadcast_event("A shadow rises...")

    def _place_agent(self, agent):
        attempts = 0
        while attempts < 100:
            rx = random.randint(0, self.width - 1)
            ry = random.randint(0, self.height - 1)
            if not self.is_blocked(rx, ry):
                agent.x = rx
                agent.y = ry
                break
            attempts += 1

    def is_blocked(self, x, y):
        terrain = self.grid[y][x]
        if terrain == TERRAIN_WALL or terrain == TERRAIN_WATER:
            return True
        for a in self.agents:
            if not a.is_dead and a.x == x and a.y == y:
                return True
        return False

    def get_terrain(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return TERRAIN_WALL

    def set_terrain(self, x, y, type):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = type

    def add_corpse(self, corpse):
        self.corpses.append(corpse)

    def broadcast_event(self, text):
        self.events.append({"tick": self.tick_count, "text": text})
        if len(self.events) > 5: self.events.pop(0)

    def update(self):
        self.tick_count += 1
        
        # New Time Logic: 30 ticks = 1 hour
        if self.tick_count % TICKS_PER_HOUR == 0:
            self.time_of_day = (self.time_of_day + 1) % 24
        
        if self.is_night() and random.random() < 0.05: # Lower spawn chance due to longer night
            self._spawn_monster()

        active_agents = [a for a in self.agents if not a.is_dead]
        for agent in active_agents:
            action = agent.decide_action(self)
            agent.perform_action(action, self)
            
        self.agents = [a for a in self.agents if not (a.job == JOB_MONSTER and a.is_dead)]

    def get_state(self):
        return {
            "tick": self.tick_count,
            "time": self.time_of_day,
            "width": self.width,
            "height": self.height,
            "agents": [a.to_dict() for a in self.agents if not a.is_dead],
            "corpses": [c.to_dict() for c in self.corpses],
            "events": self.events
        }

    def get_map(self):
        return {
            "width": self.width,
            "height": self.height,
            "grid": self.grid
        }

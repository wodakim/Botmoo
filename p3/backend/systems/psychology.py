import random
import uuid

class Psychology:
    def __init__(self):
        # Big Five Personality Traits (0.0 to 1.0)
        self.openness = random.random()        # Creativity, curiosity -> Affects Crafting / Exploration
        self.conscientiousness = random.random() # Discipline, organization -> Affects Work / Hoarding
        self.extraversion = random.random()    # Social energy -> Affects Chat / Grouping
        self.agreeableness = random.random()   # Kindness, cooperation -> Affects Sharing / Aggression
        self.neuroticism = random.random()     # Anxiety, instability -> Affects Sanity loss / Flight response

        # Mental State
        self.sanity = 100.0
        self.max_sanity = 100.0
        
        # Disorders (Acquired via trauma)
        self.disorders = [] # List of strings: "paranoia", "hoarding_ocd", "schizophrenia"

    def update_sanity(self, amount):
        self.sanity = max(0, min(self.max_sanity, self.sanity + amount))
        self._check_disorders()

    def _check_disorders(self):
        # Thresholds for developing disorders
        if self.sanity < 30 and self.neuroticism > 0.6 and "paranoia" not in self.disorders:
            self.disorders.append("paranoia")
        
        if self.sanity < 20 and self.openness > 0.7 and "schizophrenia" not in self.disorders:
            self.disorders.append("schizophrenia")
            
        if self.sanity < 40 and self.conscientiousness > 0.8 and "hoarding_ocd" not in self.disorders:
            self.disorders.append("hoarding_ocd")

    def to_dict(self):
        return {
            "traits": {
                "O": round(self.openness, 2),
                "C": round(self.conscientiousness, 2),
                "E": round(self.extraversion, 2),
                "A": round(self.agreeableness, 2),
                "N": round(self.neuroticism, 2),
            },
            "sanity": round(self.sanity, 1),
            "disorders": self.disorders
        }

class EpisodicMemory:
    def __init__(self, tick, event_type, description, emotional_weight, related_agent_id=None):
        self.tick = tick
        self.type = event_type # "trauma", "joy", "neutral"
        self.description = description
        self.emotional_weight = emotional_weight # -10.0 (Trauma) to +10.0 (Ecstasy)
        self.related_agent_id = related_agent_id

    def to_dict(self):
        return {
            "tick": self.tick,
            "desc": self.description,
            "weight": self.emotional_weight
        }

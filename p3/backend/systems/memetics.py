import random
import uuid

class LanguageEngine:
    def __init__(self):
        pass

    @staticmethod
    def generate_sentence(subject, action, object_name=None, mood="neutral"):
        """Generates a procedural sentence based on context."""

        # Simple Grammar: Subject + Verb + Object + Adjective/End

        verbs = {
            "attack": ["hits", "strikes", "bashes", "cuts"],
            "eat": ["eats", "devours", "munches", "consumes"],
            "gather": ["finds", "picks", "grabs", "harvests"],
            "craft": ["makes", "builds", "forges", "crafts"],
            "trade": ["sells", "buys", "swaps", "barters"],
            "idle": ["waits", "rests", "stands", "looks around"],
            "flee": ["runs from", "escapes", "evades"],
            "steal": ["steals from", "robs", "picks pocket of"]
        }

        adjectives = {
            "neutral": [".", " calmly.", "."],
            "hostile": [" aggressively!", " with rage!", "!"],
            "fearful": [" quickly!", " in panic!", "..."],
            "friendly": [" happily.", " with a smile.", "."],
            "pain": [" painfully.", " while bleeding.", "!"]
        }

        # Self-reference logic
        subj_str = "I" if subject == "self" else subject

        verb_list = verbs.get(action, ["does"])
        verb = random.choice(verb_list)

        # Adjust verb conjugation for "I"
        if subject == "self":
            # Very simple de-conjugation (strikes -> strike) - English is hard, keeping it primitive/caveman style might be better?
            # Let's go with "Me eat berry" style for "Artificial Life" feel, or normal english?
            # "I eat" vs "He eats".
            if verb.endswith("s"): verb = verb[:-1]

        obj_str = ""
        if object_name:
            obj_str = f" {object_name}"

        adj_str = random.choice(adjectives.get(mood, adjectives["neutral"]))

        return f"{subj_str} {verb}{obj_str}{adj_str}"

class Meme:
    def __init__(self, text, sentiment, parent_id=None):
        self.id = str(uuid.uuid4())[:8]
        self.text = text
        self.sentiment = sentiment # "hostile", "friendly", "fearful", "neutral"
        self.parent_id = parent_id # Lineage
        self.generation = 0
        self.virality = 1.0 # Base infection rate

    def mutate(self):
        """Returns a mutated version of this meme."""
        # Mutation Logic: Phonetic drift or Synonym swap
        new_text = self._apply_drift(self.text)
        child = Meme(new_text, self.sentiment, self.id)
        child.generation = self.generation + 1
        return child

    def _apply_drift(self, text):
        # Simple procedural corruption
        vowels = "aeiou"
        if random.random() < 0.3:
            # Vowel shift
            char_list = list(text)
            idx = random.randint(0, len(char_list)-1)
            if char_list[idx] in vowels:
                char_list[idx] = random.choice(vowels)
            return "".join(char_list)
        elif random.random() < 0.2:
            # Truncation
            if len(text) > 3:
                return text[:-1]
        elif random.random() < 0.2:
            # Emphasize
            return text + "!"
        return text

class MemeticHost:
    def __init__(self, openness_trait):
        self.openness = openness_trait # Susceptibility
        self.vocabulary = {} # {sentiment: [Meme]}
        self.infection_history = set() # Meme IDs already caught

        # Seed basic vocab
        self._seed_vocab()

    def _seed_vocab(self):
        seeds = {
            "hostile": ["Back off.", "Fight me?", "Go away!"],
            "friendly": ["Hello.", "Peace.", "Good trade."],
            "fearful": ["Run!", "Help!", "Monster!"],
            "neutral": ["Hmm.", "Nice day.", "Busy."]
        }
        for cat, texts in seeds.items():
            self.vocabulary[cat] = [Meme(t, cat) for t in texts]

    def expose(self, meme: Meme, source_prestige: float):
        """Try to learn a new meme from a source."""
        if meme.id in self.infection_history:
            return False # Already immune/knows it
        
        # Infection Chance = Openness * Virality * Source Prestige
        chance = self.openness * meme.virality * (1.0 + source_prestige)
        
        if random.random() < chance:
            self.learn(meme)
            return True
        return False

    def learn(self, meme: Meme):
        if meme.sentiment not in self.vocabulary:
            self.vocabulary[meme.sentiment] = []
        
        # Limit vocab size (Memory constraint)
        if len(self.vocabulary[meme.sentiment]) > 5:
            self.vocabulary[meme.sentiment].pop(0) # Forget oldest
            
        self.vocabulary[meme.sentiment].append(meme)
        self.infection_history.add(meme.id)

    def express(self, sentiment):
        """Returns a meme to speak, potentially mutating it."""
        if sentiment not in self.vocabulary or not self.vocabulary[sentiment]:
            return None
        
        meme = random.choice(self.vocabulary[sentiment])
        
        # Mutation on expression (Evolution)
        if random.random() < 0.1: # 10% mutation rate
            mutant = meme.mutate()
            self.learn(mutant) # Self-infection with new idea
            return mutant
        
        return meme

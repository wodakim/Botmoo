import random
import uuid

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
            "hostile": ["Grr.", "Back off.", "Fight?"],
            "friendly": ["Hi.", "Peace.", "Good day."],
            "fearful": ["No!", "Run!", "Scary."],
            "neutral": ["Hmm.", "Okay.", "Work."]
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

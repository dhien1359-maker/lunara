import random

MOODS = [
    ("●'◡'●", "#FF9EC4", "#e0608a"),
    ("●'▽'●", "#A8D8EA", "#4a9abf"),
    ("●'ᴗ'●", "#B5EAD7", "#3aaa80"),
    ("●'_'●", "#FFD9A0", "#e09030"),
    ("●'◕'●", "#D4A8FF", "#8844cc"),
]
SAYS = ["Wheee~!", "Boing!", "Yay!", "Hehe~", "✨", "♪", "Hiiii!", "Weee~"]

class MoodFeature:
    def __init__(self):
        self._idx = 0
        self._apply()

    def _apply(self):
        self.face, self.color, self.dark = MOODS[self._idx]

    def next(self):
        self._idx = (self._idx + 1) % len(MOODS)
        self._apply()

    def random_say(self):
        return random.choice(SAYS)

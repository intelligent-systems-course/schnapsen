from unittest import TestCase
from schnapsen.bots import RdeepBot
from schnapsen.game import SchnapsenGamePlayEngine
import random


class RdeepBotTest(TestCase):
    def setUp(self) -> None:
        self.engine = SchnapsenGamePlayEngine()
        self.bot1 = RdeepBot(16, 4, random.Random(42), "bot1")
        self.bot2 = RdeepBot(16, 4, random.Random(43), "bot2")

    def test_run(self) -> None:
        for i in range(10):
            self.engine.play_game(self.bot1, self.bot2, random.Random(i))

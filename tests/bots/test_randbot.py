from unittest import TestCase
from schnapsen.bots import RandBot
from schnapsen.game import SchnapsenGamePlayEngine
import random


class RandBotTest(TestCase):
    def setUp(self) -> None:
        self.engine = SchnapsenGamePlayEngine()
        self.bot1 = RandBot(random.Random(42), "bot1")
        self.bot2 = RandBot(random.Random(43), "bot2")

    def test_run(self) -> None:
        for i in range(1000):
            self.engine.play_game(self.bot1, self.bot2, random.Random(i))

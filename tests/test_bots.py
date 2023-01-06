from unittest import TestCase
from schnapsen.bots import RandBot, AlphaBetaBot
from schnapsen.game import SchnapsenGamePlayEngine
import random


class RandBotTest(TestCase):
    def setUp(self) -> None:
        self.engine = SchnapsenGamePlayEngine()
        self.bot1 = RandBot(42)
        self.bot2 = RandBot(43)

    def test_run(self) -> None:
        for i in range(1000):
            self.engine.play_game(self.bot1, self.bot2, random.Random(i))


class AlphaBetaBotTest(TestCase):
    def setUp(self) -> None:
        self.engine = SchnapsenGamePlayEngine()
        self.bot1 = AlphaBetaBot()
        self.bot2 = AlphaBetaBot()

    def test_run(self) -> None:
        # TODO
        pass

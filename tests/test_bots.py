from unittest import TestCase
import random
from typing import Optional
from schnapsen.bots import RandBot, AlphaBetaBot, MiniMaxBot, RdeepBot
from schnapsen.game import (
    SchnapsenGamePlayEngine,
    Bot,
    PlayerPerspective,
    Move,
    GamePhase,
)


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


class RandMiniMaxBot(Bot):
    """In the phase1, this bot plays random, and in the phase2, it plays minimax.
    The opponent is random."""

    def __init__(self) -> None:
        self.bot_phase1 = RandBot(42)
        self.bot_phase2 = MiniMaxBot()

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if state.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(state, leader_move)
        elif state.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(state, leader_move)
        else:
            raise ValueError("Phase ain't right.")


class RdeepMiniMaxBot(Bot):
    """In the phase1, this bot plays random, and in the phase2, it plays minimax.
    The opponent is random."""

    def __init__(self) -> None:
        self.bot_phase1 = RdeepBot(num_samples=16, depth=4, rand=random.Random(42))
        self.bot_phase2 = MiniMaxBot()

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if state.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(state, leader_move)
        elif state.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(state, leader_move)
        else:
            raise ValueError("Phase ain't right.")


class MiniMaxBotTest(TestCase):
    def setUp(self) -> None:
        self.engine = SchnapsenGamePlayEngine()
        self.bot1 = RandMiniMaxBot()
        self.bot2 = RandBot(43)

    def test_run(self) -> None:

        winners = {"RandMiniMaxBot": 0, "RandBot": 0}
        for i in range(2):
            winner, _, _ = self.engine.play_game(self.bot1, self.bot2, random.Random(i))

            if winner == self.bot1:
                winners["RandMiniMaxBot"] += 1
            elif winner == self.bot2:
                winners["RandBot"] += 1
            else:
                raise ValueError


class RdeepMiniMaxBotTest(TestCase):
    def setUp(self) -> None:
        self.engine = SchnapsenGamePlayEngine()
        self.bot1 = RandMiniMaxBot()
        self.bot2 = RdeepBot(num_samples=16, depth=4, rand=random.Random(43))

    def test_run(self) -> None:

        winners = {"RdeepMiniMaxBot": 0, "RdeepBot": 0}
        for i in range(2):
            winner, _, _ = self.engine.play_game(self.bot1, self.bot2, random.Random(i))

            if winner == self.bot1:
                winners["RdeepMiniMaxBot"] += 1
            elif winner == self.bot2:
                winners["RdeepBot"] += 1
            else:
                raise ValueError

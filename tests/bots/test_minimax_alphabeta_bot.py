from unittest import TestCase
import random
from typing import Optional
import time
from schnapsen.bots import RandBot, MiniMaxBot, AlphaBetaBot, RdeepBot
from schnapsen.game import (
    Bot,
    Move,
    PlayerPerspective,
    GamePhase,
    GameState,
    SchnapsenGamePlayEngine,
    BotState,
    RegularMove,
    Hand,
    Talon,
    _DummyBot,
    Score,
)
from schnapsen.deck import Card, Suit


class TwoStageBot(Bot):
    """Bot which plays first the one, than the other startegy"""

    def __init__(self, name: str, bot1: Bot, bot2: Bot) -> None:
        super().__init__(name)
        self.bot_phase1: Bot = bot1
        self.bot_phase2: Bot = bot2

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if perspective.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(perspective, leader_move)
        else:
            raise AssertionError("Phase ain't right.")


class RandMiniMaxBot(TwoStageBot):
    """In the phase1, this bot plays random, and in the phase2, it plays minimax.
    The opponent is random."""

    def __init__(self, rand: random.Random, name: str = "rand_minimax_bot") -> None:
        super().__init__(name, RandBot(rand=rand), MiniMaxBot())


class RdeepMiniMaxBot(TwoStageBot):
    """In the phase1, this bot plays rdeep, and in the phase2, it plays minimax.
    The opponent is random."""

    def __init__(self, rand: random.Random, name: str = "rdeep_minimax_bot") -> None:
        super().__init__(name, RdeepBot(num_samples=16, depth=4, rand=rand), MiniMaxBot())


class RandAlphaBetaBot(TwoStageBot):
    """In the phase1, this bot plays random, and in the phase2, it plays AlphaBeta.
    The opponent is random."""

    def __init__(self, rand: random.Random, name: str = "rand_alphabeta_bot") -> None:
        super().__init__(name, RandBot(rand=rand), AlphaBetaBot())


class RdeepAlphaBetaBot(TwoStageBot):
    """In the phase1, this bot plays rdeep, and in the phase2, it plays alphabeta.
    The opponent is random."""

    def __init__(self, rand: random.Random, name: str = "rdeep_alphabeta_bot") -> None:
        super().__init__(name, RdeepBot(num_samples=16, depth=4, rand=rand), AlphaBetaBot())


class MiniMaxBotTest(TestCase):
    def setUp(self) -> None:
        self.engine = SchnapsenGamePlayEngine()
        self.bot1 = RandMiniMaxBot(random.Random(42), "rand_minimax_bot")
        self.bot2 = RdeepMiniMaxBot(random.Random(43), "rdeep_minimax_bot")
        self.bot3 = RandBot(random.Random(44), "randbot")

        self.bot4 = RandAlphaBetaBot(random.Random(42), "rand_alphabeta_bot")
        self.bot5 = RdeepAlphaBetaBot(random.Random(43), "rdeep_alphabeta_bot")

    def test_run_1(self) -> None:
        winners = {str(self.bot1): 0, str(self.bot3): 0}
        num_games = 50
        for i in range(num_games):
            winner, _, _ = self.engine.play_game(
                self.bot1, self.bot3, random.Random(i)
            )

            winners[str(winner)] += 1

        self.assertTrue(winners[str(self.bot1)] > num_games // 2)

    def test_run_2(self) -> None:
        winners = {str(self.bot1): 0, str(self.bot2): 0}
        num_games = 50
        for i in range(num_games):
            winner, _, _ = self.engine.play_game(
                self.bot1, self.bot2, random.Random(i)
            )

            winners[str(winner)] += 1

        self.assertTrue(winners[str(self.bot2)] > num_games // 2)

    def test_second_phase(self) -> None:
        num_games = 10
        engine = SchnapsenGamePlayEngine()

        for i in range(num_games):
            state = engine.get_random_phase_two_state(random.Random(i))
            # We play two games from this state, one minimaxA  vs minimaxB.
            # We let the winning side play against many games against rand. This winning side must never lose

            minimaxA = MiniMaxBot()
            minimaxB = MiniMaxBot()
            outcome = engine.play_game_from_state_with_new_bots(state, new_leader=minimaxA, new_follower=minimaxB, leader_move=None)

            for j in range(10):
                randbot = RandBot(random.Random(j))
                if outcome[0] == minimaxA:
                    outcome2 = engine.play_game_from_state_with_new_bots(state, new_leader=minimaxA, new_follower=randbot, leader_move=None)
                    assert outcome2[0] == minimaxA
                else:
                    # minimaxB won
                    outcome2 = engine.play_game_from_state_with_new_bots(state, new_leader=randbot, new_follower=minimaxB, leader_move=None)
                    assert outcome2[0] == minimaxB


class MiniMaxBotAlphaBetaPhaseTwoEasy(TestCase):
    def setUp(self) -> None:
        self.num_runs = 100
        self.minimax_time = 0.0
        self.alphabeta_time = 0.0

        self.engine = SchnapsenGamePlayEngine()
        self.leader_move = None
        self.maximizing = True
        leader = BotState(
            implementation=_DummyBot(),
            hand=Hand(
                cards=[
                    Card.ACE_CLUBS,
                    Card.JACK_DIAMONDS,
                    Card.TEN_CLUBS,
                    Card.JACK_SPADES,
                ]
            ),
            score=Score(direct_points=54, pending_points=0),
            won_cards=[
                Card.QUEEN_DIAMONDS,
                Card.TEN_DIAMONDS,
                Card.KING_HEARTS,
                Card.JACK_HEARTS,
                Card.TEN_HEARTS,
                Card.ACE_HEARTS,
                Card.QUEEN_SPADES,
                Card.ACE_SPADES,
            ],
        )
        follower = BotState(
            implementation=_DummyBot(),
            hand=Hand(
                cards=[
                    Card.ACE_DIAMONDS,
                    Card.QUEEN_CLUBS,
                    Card.QUEEN_HEARTS,
                    Card.TEN_SPADES,
                ]
            ),
            score=Score(direct_points=14, pending_points=0),
            won_cards=[
                Card.KING_DIAMONDS,
                Card.KING_SPADES,
                Card.JACK_CLUBS,
                Card.KING_CLUBS,
            ],
        )
        talon = Talon(cards=[], trump_suit=Suit.SPADES)
        self.state = GameState(
            leader=leader, follower=follower, talon=talon, previous=None
        )

        self.minimaxbot = MiniMaxBot()
        self.alphabetabot = AlphaBetaBot()

    def test_value_move(self) -> None:
        for _ in range(self.num_runs):
            start = time.time()

            best_value, best_move = self.minimaxbot.value(
                self.state, self.engine, self.leader_move, self.maximizing
            )

            self.assertEqual(best_value, 2)
            self.assertEqual(best_move, RegularMove(Card.ACE_CLUBS))
            end = time.time()
            self.minimax_time += end - start

        for _ in range(self.num_runs):
            start = time.time()

            best_value, best_move = self.alphabetabot.value(
                self.state, self.engine, self.leader_move, self.maximizing
            )

            self.assertEqual(best_value, 2)
            self.assertEqual(best_move, RegularMove(Card.ACE_CLUBS))
            end = time.time()
            self.alphabeta_time += end - start

        # alphabeta should be faster, because it prunes more. Besides that, the result
        # should be the same
        self.assertTrue(self.alphabeta_time < self.minimax_time)


class MiniMaxBotAlphaBetaPhaseTwoHard(TestCase):
    def setUp(self) -> None:
        self.num_runs = 100
        self.minimax_time = 0.0
        self.alphabeta_time = 0.0

        self.engine = SchnapsenGamePlayEngine()
        self.leader_move = None
        self.maximizing = True
        leader = BotState(
            implementation=_DummyBot(),
            hand=Hand(
                cards=[
                    Card.QUEEN_SPADES,
                    Card.ACE_DIAMONDS,
                    Card.QUEEN_CLUBS,
                    Card.QUEEN_HEARTS,
                    Card.TEN_SPADES,
                ]
            ),
            score=Score(direct_points=14, pending_points=0),
            won_cards=[
                Card.KING_DIAMONDS,
                Card.KING_SPADES,
                Card.JACK_CLUBS,
                Card.KING_CLUBS,
            ],
        )
        follower = BotState(
            implementation=_DummyBot(),
            hand=Hand(
                cards=[
                    Card.ACE_SPADES,
                    Card.ACE_CLUBS,
                    Card.JACK_DIAMONDS,
                    Card.TEN_CLUBS,
                    Card.JACK_SPADES,
                ]
            ),
            score=Score(direct_points=40, pending_points=0),
            won_cards=[
                Card.QUEEN_DIAMONDS,
                Card.TEN_DIAMONDS,
                Card.KING_HEARTS,
                Card.JACK_HEARTS,
                Card.TEN_HEARTS,
                Card.ACE_HEARTS,
            ],
        )
        talon = Talon(cards=[], trump_suit=Suit.SPADES)
        self.state = GameState(
            leader=leader, follower=follower, talon=talon, previous=None
        )

        self.minimaxbot = MiniMaxBot()
        self.alphabetabot = AlphaBetaBot()

    def test_value_move(self) -> None:
        for _ in range(self.num_runs):
            start = time.time()

            best_value, best_move = self.minimaxbot.value(
                self.state, self.engine, self.leader_move, self.maximizing
            )

            self.assertEqual(best_value, -2)
            self.assertEqual(best_move, RegularMove(Card.QUEEN_SPADES))
            end = time.time()
            self.minimax_time += end - start

        for _ in range(self.num_runs):
            start = time.time()

            best_value, best_move = self.alphabetabot.value(
                self.state, self.engine, self.leader_move, self.maximizing
            )

            self.assertEqual(best_value, -2)
            self.assertEqual(best_move, RegularMove(Card.QUEEN_SPADES))
            end = time.time()
            self.alphabeta_time += end - start

        # alphabeta should be faster, because it prunes more. Besides that, the result
        # should be the same
        self.assertTrue(self.alphabeta_time < self.minimax_time)

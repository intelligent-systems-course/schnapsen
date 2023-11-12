from unittest import TestCase
import random
from typing import Optional
from schnapsen.bots import RandBot, MiniMaxBot, RdeepBot
from schnapsen.game import (
    Bot,
    Move,
    PlayerPerspective,
    GamePhase,
    GameState,
    FollowerPerspective,
    LeaderPerspective,
    GamePlayEngine,
    SchnapsenTrickScorer,
    SchnapsenGamePlayEngine,
    BotState,
    RegularMove,
    Hand,
    Talon,
    _DummyBot,
    Score,
)
from schnapsen.deck import Card, Suit, Rank


class RandMiniMaxBot(Bot):
    """In the phase1, this bot plays random, and in the phase2, it plays minimax.
    The opponent is random."""

    def __init__(self, rand=random.Random, name="rand_minimax_bot") -> None:
        super().__init__(name)
        self.bot_phase1 = RandBot(rand=rand)
        self.bot_phase2 = MiniMaxBot()

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if state.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(state, leader_move)
        elif state.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(state, leader_move)
        else:
            raise ValueError("Phase ain't right.")


class RdeepMiniMaxBot(Bot):
    """In the phase1, this bot plays rdeep, and in the phase2, it plays minimax.
    The opponent is random."""

    def __init__(self, rand=random.Random, name: str = "rdeep_minimax_bot") -> None:
        super().__init__(name)
        self.bot_phase1 = RdeepBot(num_samples=16, depth=4, rand=rand)
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
        self.bot1 = RandMiniMaxBot(random.Random(42), "rand_minimax_bot")
        self.bot2 = RdeepMiniMaxBot(random.Random(43), "rdeep_minimax_bot")
        self.bot3 = RandBot(random.Random(44), "randbot")

    def test_run_1(self) -> None:
        winners = {str(self.bot1): 0, str(self.bot3): 0}
        num_games = 50
        for i in range(num_games):
            winner, points, score = self.engine.play_game(
                self.bot1, self.bot3, random.Random(i)
            )

            winners[str(winner)] += 1

        self.assertTrue(winners[str(self.bot1)] > num_games // 2)

    def test_run_2(self) -> None:
        winners = {str(self.bot2): 0, str(self.bot3): 0}
        num_games = 50
        for i in range(num_games):
            winner, points, score = self.engine.play_game(
                self.bot2, self.bot3, random.Random(i)
            )

            winners[str(winner)] += 1

        self.assertTrue(winners[str(self.bot2)] > num_games // 2)

    def test_run_3(self) -> None:
        winners = {str(self.bot1): 0, str(self.bot2): 0}
        num_games = 50
        for i in range(num_games):
            winner, points, score = self.engine.play_game(
                self.bot1, self.bot2, random.Random(i)
            )

            winners[str(winner)] += 1

        self.assertTrue(winners[str(self.bot2)] > num_games // 2)


class MiniMaxBotPhaseTwo(TestCase):
    def test_value_move_easy(self) -> None:
        engine = SchnapsenGamePlayEngine()
        leader_move = None
        maximizing = True

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
        state = GameState(leader=leader, follower=follower, talon=talon, previous=None)

        bot = MiniMaxBot()

        best_value, best_move = bot.value(state, engine, leader_move, maximizing)

        self.assertEqual(best_value, 2)
        self.assertEqual(best_move, RegularMove(Card.ACE_CLUBS))

    def test_value_move_hard(self) -> None:
        engine = SchnapsenGamePlayEngine()
        leader_move = None
        maximizing = True

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
        state = GameState(leader=leader, follower=follower, talon=talon, previous=None)

        bot = MiniMaxBot()

        best_value, best_move = bot.value(state, engine, leader_move, maximizing)

        self.assertEqual(best_value, -2)
        self.assertEqual(best_move, RegularMove(Card.QUEEN_SPADES))

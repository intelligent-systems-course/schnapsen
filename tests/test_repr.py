import random
from unittest import TestCase
from schnapsen.deck import Card, Suit, OrderedCardCollection
from schnapsen.game import (
    TrumpExchange,
    RegularMove,
    RegularTrick,
    Marriage,
    Hand,
    Talon,
    PartialTrick,
    Score,
    BotState,
    GameState,
)
from schnapsen.bots.rand import RandBot


class ReprTest(TestCase):
    def test_OrderedCardCollection(self) -> None:
        output = str(OrderedCardCollection([Card.ACE_CLUBS, Card.ACE_SPADES]))
        self.assertEqual(
            output, "OrderedCardCollection(cards=[Card.ACE_CLUBS, Card.ACE_SPADES])"
        )

    def test_Marriage(self) -> None:
        output = str(Marriage(Card.QUEEN_CLUBS, Card.KING_CLUBS))
        self.assertEqual(
            output, "Marriage(queen_card=Card.QUEEN_CLUBS, king_card=Card.KING_CLUBS)"
        )

    def test_Trick(self) -> None:
        mv = RegularMove(Card.ACE_CLUBS)
        mv_ = RegularMove(Card.ACE_HEARTS)
        output = str(RegularTrick(leader_move=mv, follower_move=mv_))
        self.assertEqual(
            output,
            "RegularTrick(leader_move=RegularMove(card=Card.ACE_CLUBS), follower_move=RegularMove(card=Card.ACE_HEARTS))",
        )

    def test_GameState(self) -> None:
        bot0 = RandBot(random.Random(42), "RandBot(seed=42)")
        output_bot0 = str(bot0)
        self.assertEqual("RandBot(seed=42)", output_bot0)

        hand0 = Hand(
            cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS]
        )
        output_hand0 = str(hand0)
        self.assertEqual(
            output_hand0,
            "Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5)",
        )
        score0 = Score(direct_points=4, pending_points=2)
        output_score0 = str(score0)
        self.assertEqual(output_score0, "Score(direct_points=4, pending_points=2)")

        won_cards0 = [Card.ACE_DIAMONDS]
        leader = BotState(
            implementation=bot0,
            hand=hand0,
            score=score0,
            won_cards=won_cards0,
        )
        output_leader = str(leader)
        self.assertEqual(
            output_leader,
            "BotState(implementation=RandBot(seed=42), hand=Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5), score=Score(direct_points=4, pending_points=2), won_cards=[Card.ACE_DIAMONDS])",
        )

        bot1 = RandBot(random.Random(43), "RandBot(seed=43)")
        hand1 = Hand(
            cards=[
                Card.ACE_SPADES,
                Card.FIVE_HEARTS,
                Card.NINE_CLUBS,
                Card.SEVEN_SPADES,
            ]
        )
        output_bot1 = str(bot1)
        self.assertEqual("RandBot(seed=43)", output_bot1)
        output_hand1 = str(hand1)
        self.assertEqual(
            output_hand1,
            "Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5)",
        )

        score1 = Score(direct_points=2, pending_points=4)
        won_cards1 = [Card.NINE_DIAMONDS]
        follower = BotState(
            implementation=bot1,
            hand=hand1,
            score=score1,
            won_cards=won_cards1,
        )
        talon = Talon(cards=[Card.ACE_HEARTS], trump_suit=Suit.HEARTS)
        output_talon = str(talon)
        self.assertEqual(
            output_talon, "Talon(cards=[Card.ACE_HEARTS], trump_suit=HEARTS)"
        )

        output_follower = str(follower)
        self.assertEqual(
            output_follower,
            "BotState(implementation=RandBot(seed=43), hand=Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5), score=Score(direct_points=2, pending_points=4), won_cards=[Card.NINE_DIAMONDS])",
        )

        gs = GameState(
            leader=leader, follower=follower, talon=talon, previous=None
        )
        output_gs = str(gs)
        self.assertEqual(
            output_gs,
            "GameState(leader=BotState(implementation=RandBot(seed=42), hand=Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5), score=Score(direct_points=4, pending_points=2), won_cards=[Card.ACE_DIAMONDS]), follower=BotState(implementation=RandBot(seed=43), hand=Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5), score=Score(direct_points=2, pending_points=4), won_cards=[Card.NINE_DIAMONDS]), talon=Talon(cards=[Card.ACE_HEARTS], trump_suit=HEARTS), previous=None)",
        )

        te = TrumpExchange(jack=Card.JACK_SPADES)
        output_te = str(te)
        self.assertEqual(output_te, "TrumpExchange(jack=Card.JACK_SPADES)")

        mv = RegularMove(Card.ACE_CLUBS)
        output_mv = str(mv)
        self.assertEqual(output_mv, "RegularMove(card=Card.ACE_CLUBS)")

        pt = PartialTrick(leader_move=mv)
        output_pt = str(pt)
        self.assertEqual(
            output_pt,
            "PartialTrick(leader_move=RegularMove(card=Card.ACE_CLUBS))",
        )

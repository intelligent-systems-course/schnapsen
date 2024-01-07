import random
from unittest import TestCase
from schnapsen.deck import Card, Rank, Suit
from schnapsen.game import (
    TrumpExchange,
    Marriage,
    Hand,
    Talon,
    Score,
    BotState,
    GameState,
    SchnapsenGamePlayEngine,
    LeaderPerspective,
    RegularMove,
    FollowerPerspective,
)
from schnapsen.bots.rand import RandBot


class MoveTest(TestCase):
    """Tests the different move types"""

    def setUp(self) -> None:
        self.jacks: list[Card] = []
        for suit in Suit:
            jack = Card.get_card(Rank.JACK, suit)
            self.jacks.append(jack)

    def test_trump_exchange_creation(self) -> None:
        for jack in self.jacks:
            exchange = TrumpExchange(jack=jack)
            self.assertTrue(exchange.is_trump_exchange())
            self.assertFalse(exchange.is_marriage())
            self.assertEqual(len(exchange.cards), 1)
            self.assertEqual(exchange.cards[0], jack)

    def test_trump_creation_fails(self) -> None:
        for card in Card:
            if card not in self.jacks:
                with self.assertRaises(AssertionError):
                    TrumpExchange(jack=card)

    def test_marriage_creation_fails(self) -> None:
        for card1 in Card:
            for card2 in Card:
                if not (card1.suit == card2.suit and card1.rank == Rank.QUEEN, card2.rank == Rank.KING):
                    with self.assertRaises(AssertionError):
                        Marriage(queen_card=card1, king_card=card2)

    def test_marriage_creation(self) -> None:
        for suit in Suit:
            queen = Card.get_card(Rank.QUEEN, suit)
            king = Card.get_card(Rank.KING, suit)
            marriage = Marriage(queen_card=queen, king_card=king)
            self.assertTrue(marriage.is_marriage())
            self.assertFalse(marriage.is_trump_exchange())
            self.assertEqual(marriage.underlying_regular_move().cards[0], king)
            self.assertEqual(marriage.cards, [queen, king])


class HandTest(TestCase):

    def setUp(self) -> None:
        self.ten_cards = [
            Card.FIVE_CLUBS,
            Card.JACK_HEARTS,
            Card.ACE_SPADES,
            Card.TWO_HEARTS,
            Card.QUEEN_HEARTS,
            # intentional repetition. Hand should not assume uniqueness
            Card.QUEEN_HEARTS,
            Card.JACK_SPADES,
            Card.ACE_HEARTS,
            Card.TWO_CLUBS,
            Card.QUEEN_DIAMONDS,
        ]

    def test_too_large_creation_fail(self) -> None:
        for max_size in range(len(self.ten_cards)):
            for too_large in range(max_size + 1, len(self.ten_cards)):
                too_many_cards = self.ten_cards[:too_large]
                with self.assertRaises(AssertionError):
                    Hand(cards=too_many_cards, max_size=max_size)

    def test_creation(self) -> None:
        for max_size in range(len(self.ten_cards)):
            for created_size in range(max_size):
                start_cards = self.ten_cards[:created_size]
                hand = Hand(start_cards, max_size=max_size)
                if created_size == 0:
                    self.assertTrue(hand.is_empty())
                else:
                    self.assertFalse(hand.is_empty())

    def test_removal_unique(self) -> None:
        hand = Hand(self.ten_cards[:5])
        self.assertIn(Card.FIVE_CLUBS, hand)
        hand.remove(Card.FIVE_CLUBS)
        self.assertNotIn(Card.FIVE_CLUBS, hand)

    def test_removal_duplicate(self) -> None:
        hand = Hand(self.ten_cards, max_size=10)
        self.assertIn(Card.QUEEN_HEARTS, hand)
        hand.remove(Card.QUEEN_HEARTS)
        self.assertIn(Card.QUEEN_HEARTS, hand)
        # remove the second one
        hand.remove(Card.QUEEN_HEARTS)
        self.assertNotIn(Card.QUEEN_HEARTS, hand)

    def test_remove_non_existing(self) -> None:
        hand = Hand(self.ten_cards, max_size=10)
        for card in Card:
            if card not in self.ten_cards:
                with self.assertRaises(Exception):
                    hand.remove(card)

    def test_add(self) -> None:
        hand = Hand(self.ten_cards[:4], max_size=5)
        hand.add(Card.KING_SPADES)
        self.assertEqual(
            hand.cards,
            [
                Card.FIVE_CLUBS,
                Card.JACK_HEARTS,
                Card.ACE_SPADES,
                Card.TWO_HEARTS,
                Card.KING_SPADES,
            ],
        )

    def test_add_too_much(self) -> None:
        hand = Hand(self.ten_cards[:4], max_size=5)
        hand.add(Card.EIGHT_CLUBS)
        with self.assertRaises(AssertionError):
            hand.add(Card.FIVE_HEARTS)

    def test_has_cards(self) -> None:
        hand = Hand(self.ten_cards, max_size=10)
        self.assertTrue(hand.has_cards([Card.JACK_HEARTS, Card.TWO_HEARTS]))

    def test_copy(self) -> None:
        hand = Hand(self.ten_cards, max_size=10)
        copy = hand.copy()
        self.assertEqual(copy.get_cards(), hand.get_cards())
        # modifying the copy must not modify the original
        copy.remove(Card.FIVE_CLUBS)
        self.assertEqual(hand.get_cards(), self.ten_cards)

    def test_filter_suit(self) -> None:
        hand = Hand(self.ten_cards, max_size=10)
        self.assertEqual(
            hand.filter_suit(Suit.HEARTS),
            [Card.JACK_HEARTS, Card.TWO_HEARTS, Card.QUEEN_HEARTS, Card.QUEEN_HEARTS, Card.ACE_HEARTS],
        )
        self.assertEqual(hand.filter_suit(Suit.SPADES), [Card.ACE_SPADES, Card.JACK_SPADES])
        self.assertEqual(hand.filter_suit(Suit.CLUBS), [Card.FIVE_CLUBS, Card.TWO_CLUBS])
        self.assertEqual(hand.filter_suit(Suit.DIAMONDS), [Card.QUEEN_DIAMONDS])

    def test_filter_rank(self) -> None:
        hand = Hand(self.ten_cards, max_size=10)
        self.assertEqual(hand.filter_rank(Rank.ACE), [Card.ACE_SPADES, Card.ACE_HEARTS])
        self.assertEqual(hand.filter_rank(Rank.TWO), [Card.TWO_HEARTS, Card.TWO_CLUBS])
        self.assertEqual(hand.filter_rank(Rank.JACK), [Card.JACK_HEARTS, Card.JACK_SPADES])
        self.assertEqual(hand.filter_rank(Rank.QUEEN), [Card.QUEEN_HEARTS, Card.QUEEN_HEARTS, Card.QUEEN_DIAMONDS])
        self.assertEqual(hand.filter_rank(Rank.KING), [])
        self.assertEqual(hand.filter_rank(Rank.THREE), [])


class TalonTest(TestCase):

    def setUp(self) -> None:
        self.ten_cards = [
            Card.FIVE_CLUBS,
            Card.JACK_HEARTS,
            Card.ACE_SPADES,
            Card.TWO_HEARTS,
            Card.QUEEN_HEARTS,
            # intentional repetition. Talon should not assume uniqueness
            Card.QUEEN_HEARTS,
            Card.JACK_SPADES,
            Card.ACE_HEARTS,
            Card.TWO_CLUBS,
            Card.QUEEN_DIAMONDS,
        ]

    def test_creation_and_trump_suit(self) -> None:
        t = Talon([], Suit.HEARTS)
        self.assertEqual(t.trump_suit(), Suit.HEARTS)
        t = Talon(self.ten_cards)
        self.assertEqual(t.trump_suit(), Suit.DIAMONDS)
        t = Talon(self.ten_cards, Suit.DIAMONDS)
        self.assertEqual(t.trump_suit(), Suit.DIAMONDS)

    def test_wrong_suit_creation(self) -> None:
        with self.assertRaises(AssertionError):
            Talon(self.ten_cards, Suit.CLUBS)
        with self.assertRaises(AssertionError):
            Talon([], None)

    def test_correct_trump_exchange(self) -> None:
        t = Talon(self.ten_cards)
        old_trump = t.trump_exchange(Card.JACK_DIAMONDS)
        self.assertEqual(old_trump, Card.QUEEN_DIAMONDS)
        self.assertEqual(len(list(t.get_cards())), 10)
        copy = list(self.ten_cards)
        copy[9] = Card.JACK_DIAMONDS
        self.assertEqual(t.get_cards(), copy)
        self.assertEqual(t.trump_suit(), Suit.DIAMONDS)

    def test_draw_cards(self) -> None:
        t = Talon(self.ten_cards)
        drawn = list(t.draw_cards(4))
        self.assertEqual(drawn, self.ten_cards[0:4])
        rest = list(t.get_cards())
        self.assertEqual(rest, self.ten_cards[4:10])

    def test_overdraw_cards(self) -> None:
        t = Talon(self.ten_cards)
        with self.assertRaises(AssertionError):
            t.draw_cards(11)


class ScoreTest(TestCase):

    def test_add(self) -> None:
        for direct1 in range(-10, 10):
            for pending1 in range(-10, 10):
                score1 = Score(direct_points=direct1, pending_points=pending1)
                for direct2 in range(-1, 10):
                    for pending2 in range(-1, 10):
                        score2 = Score(direct_points=direct2, pending_points=pending2)
                        for together in [score1 + score2, score2 + score1]:  # the sum must be invariant to order
                            self.assertEqual(together.direct_points, direct1 + direct2)
                            self.assertEqual(together.pending_points, pending1 + pending2)

    def test_redeem_pending_points(self) -> None:
        for direct1 in range(-10, 10):
            for pending1 in range(-10, 10):
                score = Score(direct_points=direct1, pending_points=pending1)
                redeemed = score.redeem_pending_points()
                self.assertEqual(redeemed.pending_points, 0)
                self.assertEqual(redeemed.direct_points, direct1 + pending1)


class GameTest(TestCase):

    def test_BotState(self) -> None:
        bot = RandBot(random.Random(42))
        hand = Hand(
            cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS]
        )
        score = Score(direct_points=4, pending_points=2)
        won_cards = [Card.ACE_DIAMONDS]
        foo = BotState(
            implementation=bot,
            hand=hand,
            score=score,
            won_cards=won_cards,
        )
        bar = foo.copy()
        self.assertEqual(bar.implementation, bot)
        self.assertEqual(bar.hand.cards, hand.cards)
        self.assertEqual(bar.score, score)
        self.assertEqual(bar.won_cards, won_cards)

    def test_GameState(self) -> None:
        bot0 = RandBot(random.Random(42))
        hand0 = Hand(
            cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS]
        )
        score0 = Score(direct_points=4, pending_points=2)
        won_cards0 = [Card.ACE_DIAMONDS]
        leader = BotState(
            implementation=bot0,
            hand=hand0,
            score=score0,
            won_cards=won_cards0,
        )

        bot1 = RandBot(random.Random(43))
        hand1 = Hand(
            cards=[
                Card.ACE_SPADES,
                Card.FIVE_HEARTS,
                Card.NINE_CLUBS,
                Card.SEVEN_SPADES,
            ]
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

        gs = GameState(
            leader=leader, follower=follower, talon=talon, previous=None
        )
        self.assertFalse(gs.are_all_cards_played())

    def test_LeaderGameState(self) -> None:
        bot0 = RandBot(random.Random(42))
        hand0 = Hand(
            cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS]
        )
        score0 = Score(direct_points=4, pending_points=2)
        won_cards0 = [Card.ACE_DIAMONDS]
        leader = BotState(
            implementation=bot0,
            hand=hand0,
            score=score0,
            won_cards=won_cards0,
        )

        bot1 = RandBot(random.Random(43))
        hand1 = Hand(
            cards=[
                Card.ACE_SPADES,
                Card.FIVE_HEARTS,
                Card.NINE_CLUBS,
                Card.SEVEN_SPADES,
            ]
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

        gs = GameState(
            leader=leader, follower=follower, talon=talon, previous=None
        )
        sgpe = SchnapsenGamePlayEngine()
        lgs = LeaderPerspective(state=gs, engine=sgpe)
        self.assertEqual(
            lgs.valid_moves(),
            [
                RegularMove(Card.ACE_CLUBS),
                RegularMove(Card.FIVE_CLUBS),
                RegularMove(Card.NINE_HEARTS),
                RegularMove(Card.SEVEN_CLUBS),
            ],
        )
        self.assertEqual(
            lgs.get_hand().cards,
            [
                Card.ACE_CLUBS,
                Card.FIVE_CLUBS,
                Card.NINE_HEARTS,
                Card.SEVEN_CLUBS,
            ],
        )

    def test_FollowerGameState(self) -> None:
        bot0 = RandBot(random.Random(42))
        hand0 = Hand(
            cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS]
        )
        score0 = Score(direct_points=4, pending_points=2)
        won_cards0 = [Card.ACE_DIAMONDS]
        leader = BotState(
            implementation=bot0,
            hand=hand0,
            score=score0,
            won_cards=won_cards0,
        )

        bot1 = RandBot(random.Random(43))
        hand1 = Hand(
            cards=[
                Card.ACE_SPADES,
                Card.FIVE_HEARTS,
                Card.NINE_CLUBS,
                Card.SEVEN_SPADES,
            ]
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

        gs = GameState(
            leader=leader, follower=follower, talon=talon, previous=None
        )
        sgpe = SchnapsenGamePlayEngine()

        mv = RegularMove(Card.ACE_CLUBS)

        # TODO lgs should be tested as well
        # lgs = LeaderGameState(state=gs, engine=sgpe)
        fgs = FollowerPerspective(state=gs, engine=sgpe, leader_move=mv)
        self.assertEqual(
            fgs.valid_moves(),
            [
                RegularMove(Card.ACE_SPADES),
                RegularMove(Card.FIVE_HEARTS),
                RegularMove(Card.NINE_CLUBS),
                RegularMove(Card.SEVEN_SPADES),
            ],
        )
        self.assertEqual(
            fgs.get_hand().cards,
            [
                Card.ACE_SPADES,
                Card.FIVE_HEARTS,
                Card.NINE_CLUBS,
                Card.SEVEN_SPADES,
            ],
        )

    def test_marriage_point(self) -> None:
        # make game
        # play marriage
        # loose trick
        # make sure marriage points are not applied
        #        assert
        # win trick

        # make sure marriage poits are applied
        #        assert
        pass

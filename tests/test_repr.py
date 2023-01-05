from unittest import TestCase
from schnapsen.cli import RandBot
from schnapsen.deck import Card, Suit, OrderedCardCollection
from schnapsen.game import (
    Trump_Exchange,
    RegularMove,
    Marriage,
    Hand,
    Talon,
    PartialTrick,
    Trick,
    Score,
    BotState,
    GameState,
    SchnapsenGamePlayEngine,
    LeaderGameState,
    FollowerGameState,
)


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
        te = Trump_Exchange(jack=Suit.SPADES)
        mv = RegularMove(Card.ACE_CLUBS)
        mv_ = RegularMove(Card.ACE_HEARTS)
        output = str(Trick(trump_exchange=te, leader_move=mv, follower_move=mv_))
        self.assertEqual(
            output,
            "Trick(trump_exchange=Trump_Exchange(jack=SPADES), leader_move=RegularMove(card=Card.ACE_CLUBS), follower_move=RegularMove(card=Card.ACE_HEARTS))",
        )

    def test_GameState(self) -> None:
        bot0 = RandBot(seed=42)
        output_bot0 = str(bot0)
        self.assertEqual(output_bot0, "RandBot(seed=42)")

        hand0 = Hand(
            cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS]
        )
        output_hand0 = str(hand0)
        self.assertEqual(
            output_hand0,
            "Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5)",
        )
        bot_id0 = "0"
        score0 = Score(direct_points=4, pending_points=2)
        output_score0 = str(score0)
        self.assertEqual(output_score0, "Score(direct_points=4, pending_points=2)")

        won_cards0 = [Card.ACE_DIAMONDS]
        leader = BotState(
            implementation=bot0,
            hand=hand0,
            bot_id=bot_id0,
            score=score0,
            won_cards=won_cards0,
        )
        output_leader = str(leader)
        self.assertEqual(
            output_leader,
            "BotState(implementation=RandBot(seed=42), hand=Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5), bot_id=0, score=Score(direct_points=4, pending_points=2), won_cards=[Card.ACE_DIAMONDS])",
        )

        bot1 = RandBot(seed=43)
        hand1 = Hand(
            cards=[
                Card.ACE_SPADES,
                Card.FIVE_HEARTS,
                Card.NINE_CLUBS,
                Card.SEVEN_SPADES,
            ]
        )
        output_bot1 = str(bot1)
        self.assertEqual(output_bot1, "RandBot(seed=43)")
        output_hand1 = str(hand1)
        self.assertEqual(
            output_hand1,
            "Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5)",
        )

        bot_id1 = "1"
        score1 = Score(direct_points=2, pending_points=4)
        won_cards1 = [Card.NINE_DIAMONDS]
        follower = BotState(
            implementation=bot1,
            hand=hand1,
            bot_id=bot_id1,
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
            "BotState(implementation=RandBot(seed=43), hand=Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5), bot_id=1, score=Score(direct_points=2, pending_points=4), won_cards=[Card.NINE_DIAMONDS])",
        )

        gs = GameState(
            leader=leader, follower=follower, talon=talon, previous="previous"
        )
        output_gs = str(gs)
        self.assertEqual(
            output_gs,
            "GameState(leader=BotState(implementation=RandBot(seed=42), hand=Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5), bot_id=0, score=Score(direct_points=4, pending_points=2), won_cards=[Card.ACE_DIAMONDS]), follower=BotState(implementation=RandBot(seed=43), hand=Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5), bot_id=1, score=Score(direct_points=2, pending_points=4), won_cards=[Card.NINE_DIAMONDS]), talon=Talon(cards=[Card.ACE_HEARTS], trump_suit=HEARTS), previous=previous, played_trick=None)",
        )

        sgpe = SchnapsenGamePlayEngine()
        output_sgpe = str(sgpe)
        # below can't be tested since the memory locations are different.
        # self.assertEqual(
        #     output_sgpe,
        #     "GamePlayEngine(deck_generator=<schnapsen.game.SchnapsenDeckGenerator object at 0x7fb20754f940>, hand_generator=<schnapsen.game.SchnapsenHandGenerator object at 0x7fb20754f700>, trick_implementer=<schnapsen.game.SchnapsenTrickImplementer object at 0x7fb20754f8e0>, move_requester=<schnapsen.game.SimpleMoveRequester object at 0x7fb20754f5b0>, move_validator=<schnapsen.game.SchnapsenMoveValidator object at 0x7fb20754fe20>, trick_scorer=<schnapsen.game.SchnapsenTrickScorer object at 0x7fb20754faf0>)",
        # )

        te = Trump_Exchange(jack=Suit.SPADES)
        output_te = str(te)
        self.assertEqual(output_te, "Trump_Exchange(jack=SPADES)")

        mv = RegularMove(Card.ACE_CLUBS)
        output_mv = str(mv)
        self.assertEqual(output_mv, "RegularMove(card=Card.ACE_CLUBS)")

        pt = PartialTrick(trump_exchange=te, leader_move=mv)
        output_pt = str(pt)
        self.assertEqual(
            output_pt,
            "PartialTrick(trump_exchange=Trump_Exchange(jack=SPADES), leader_move=RegularMove(card=Card.ACE_CLUBS))",
        )

        lgs = LeaderGameState(state=gs, engine=sgpe)
        output_lgs = str(lgs)
        # below can't be tested since the memory locations are different.
        # self.assertEqual(
        #     output_lgs,
        #     "LeaderGameState(state=GameState(leader=BotState(implementation=RandBot(seed=42), hand=Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5), bot_id=0, score=Score(direct_points=4, pending_points=2), won_cards=[Card.ACE_DIAMONDS]), follower=BotState(implementation=RandBot(seed=43), hand=Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5), bot_id=1, score=Score(direct_points=2, pending_points=4), won_cards=[Card.NINE_DIAMONDS]), talon=Talon(cards=[Card.ACE_HEARTS], trump_suit=HEARTS), previous=previous, played_trick=None), engine=GamePlayEngine(deck_generator=<schnapsen.game.SchnapsenDeckGenerator object at 0x7fa68cffca00>, hand_generator=<schnapsen.game.SchnapsenHandGenerator object at 0x7fa68cffc730>, trick_implementer=<schnapsen.game.SchnapsenTrickImplementer object at 0x7fa68cffc9d0>, move_requester=<schnapsen.game.SimpleMoveRequester object at 0x7fa68cffc580>, move_validator=<schnapsen.game.SchnapsenMoveValidator object at 0x7fa68cffcf40>, trick_scorer=<schnapsen.game.SchnapsenTrickScorer object at 0x7fa68cffc550>)",
        # )
        fgs = FollowerGameState(state=gs, engine=sgpe, partial_trick=pt)
        output_fgs = str(fgs)
        # below can't be tested since the memory locations are different.
        # self.assertEqual(
        #     output_fgs,
        #     "FollowerGameState(state=GameState(leader=BotState(implementation=RandBot(seed=42), hand=Hand(cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS], max_size=5), bot_id=0, score=Score(direct_points=4, pending_points=2), won_cards=[Card.ACE_DIAMONDS]), follower=BotState(implementation=RandBot(seed=43), hand=Hand(cards=[Card.ACE_SPADES, Card.FIVE_HEARTS, Card.NINE_CLUBS, Card.SEVEN_SPADES], max_size=5), bot_id=1, score=Score(direct_points=2, pending_points=4), won_cards=[Card.NINE_DIAMONDS]), talon=Talon(cards=[Card.ACE_HEARTS], trump_suit=HEARTS), previous=previous, played_trick=None), engine=GamePlayEngine(deck_generator=<schnapsen.game.SchnapsenDeckGenerator object at 0x7f4342d92a00>, hand_generator=<schnapsen.game.SchnapsenHandGenerator object at 0x7f4342d92730>, trick_implementer=<schnapsen.game.SchnapsenTrickImplementer object at 0x7f4342d929d0>, move_requester=<schnapsen.game.SimpleMoveRequester object at 0x7f4342d92580>, move_validator=<schnapsen.game.SchnapsenMoveValidator object at 0x7f4342d92f40>, trick_scorer=<schnapsen.game.SchnapsenTrickScorer object at 0x7f4342d92550>), partial_trick=PartialTrick(trump_exchange=Trump_Exchange(jack=SPADES), leader_move=RegularMove(card=Card.ACE_CLUBS)))",
        # )

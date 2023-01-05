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
        assert output == "OrderedCardCollection(cards=[Card.ACE_CLUBS, Card.ACE_SPADES])"


    def test_Marriage(self) -> None:
        output = str(Marriage(Card.QUEEN_CLUBS, Card.KING_CLUBS))
        assert output == "Marriage(queen_card=Card.QUEEN_CLUBS, king_card=Card.KING_CLUBS)"

    def test_Trick(self) -> None:
        te = Trump_Exchange(jack=Suit.SPADES)
        mv = RegularMove(Card.ACE_CLUBS)
        mv_ = RegularMove(Card.ACE_HEARTS)
        print(Trick(trump_exchange=te, leader_move=mv, follower_move=mv_))

    def test_GameState(self) -> None:
        bot0 = RandBot(seed=42)
        print(bot0)
        hand0 = Hand(
            cards=[Card.ACE_CLUBS, Card.FIVE_CLUBS, Card.NINE_HEARTS, Card.SEVEN_CLUBS]
        )
        bot_id0 = "0"
        score0 = Score(direct_points=4, pending_points=2)
        print(score0)
        won_cards0 = [Card.ACE_DIAMONDS]
        leader = BotState(
            implementation=bot0,
            hand=hand0,
            bot_id=bot_id0,
            score=score0,
            won_cards=won_cards0,
        )
        print(leader)

        bot1 = RandBot(seed=43)
        hand1 = Hand(
            cards=[
                Card.ACE_SPADES,
                Card.FIVE_HEARTS,
                Card.NINE_CLUBS,
                Card.SEVEN_SPADES,
            ]
        )
        print(hand1)
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
        print(talon)

        gs = GameState(
            leader=leader, follower=follower, talon=talon, previous="previous"
        )
        print(gs)
        sgpe = SchnapsenGamePlayEngine()
        print(sgpe)

        te = Trump_Exchange(jack=Suit.SPADES)
        print(te)
        mv = RegularMove(Card.ACE_CLUBS)
        print(mv)
        pt = PartialTrick(trump_exchange=te, leader_move=mv)
        print(pt)
        lgs = LeaderGameState(state=gs, engine=sgpe)
        print(lgs)
        fgs = FollowerGameState(state=gs, engine=sgpe, partial_trick=pt)
        print(fgs)

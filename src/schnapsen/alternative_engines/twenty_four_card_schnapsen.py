from schnapsen.game import DeckGenerator, SchnapsenDeckGenerator, GamePlayEngine, SchnapsenHandGenerator, SchnapsenMoveValidator, SchnapsenTrickImplementer, SchnapsenTrickScorer, SimpleMoveRequester
from schnapsen.deck import Card, OrderedCardCollection, Rank, Suit


class MyDeckGenerator(DeckGenerator):
    def get_initial_deck(self) -> OrderedCardCollection:
        normal = SchnapsenDeckGenerator().get_initial_deck()
        cards = list(normal.get_cards())
        for suit in Suit:
            cards.append(Card.get_card(Rank.NINE, suit))
        return OrderedCardCollection(cards)


class MyTrickScorer(SchnapsenTrickScorer):

    scores = {
        Rank.ACE: 11,
        Rank.TEN: 10,
        Rank.KING: 4,
        Rank.QUEEN: 3,
        Rank.JACK: 2,
        Rank.NINE: 1,
    }

    # We override how points are given, because we need a score for the extra card
    def rank_to_points(self, rank: Rank) -> int:
        return MyTrickScorer.scores[rank]


class TwentyFourSchnapsenGamePlayEngine(GamePlayEngine):
    def __init__(self) -> None:
        super().__init__(
            deck_generator=MyDeckGenerator(),
            hand_generator=SchnapsenHandGenerator(),
            trick_implementer=SchnapsenTrickImplementer(),
            move_requester=SimpleMoveRequester(),
            move_validator=SchnapsenMoveValidator(),
            trick_scorer=MyTrickScorer()
        )

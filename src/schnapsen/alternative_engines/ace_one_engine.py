from schnapsen.game import GamePlayEngine, SchnapsenDeckGenerator, SchnapsenHandGenerator, SchnapsenMoveValidator, SchnapsenTrickImplementer, SchnapsenTrickScorer, SimpleMoveRequester
from schnapsen.deck import Rank


class MyTrickScorer(SchnapsenTrickScorer):

    SCORES = {
        Rank.ACE: 1,
        Rank.TEN: 10,
        Rank.KING: 4,
        Rank.QUEEN: 3,
        Rank.JACK: 2,
        Rank.NINE: 1,
    }

    # We override how points are given, because we score the ACE differently
    def rank_to_points(self, rank: Rank) -> int:
        return MyTrickScorer.SCORES[rank]


class AceOneGamePlayEngine(GamePlayEngine):
    def __init__(self) -> None:
        super().__init__(
            deck_generator=SchnapsenDeckGenerator(),
            hand_generator=SchnapsenHandGenerator(),
            trick_implementer=SchnapsenTrickImplementer(),
            move_requester=SimpleMoveRequester(),
            move_validator=SchnapsenMoveValidator(),
            trick_scorer=MyTrickScorer()
        )

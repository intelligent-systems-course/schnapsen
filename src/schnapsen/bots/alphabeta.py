from typing import Optional

from ..game import Bot, Move, PartialTrick, PlayerGameState


class AlphaBetaBot(Bot):
    def __init__(self) -> None:
        super().__init__()

    def get_move(self, state: PlayerGameState, leader_move: Optional[PartialTrick]) -> Move:
        raise NotImplementedError()

from typing import Optional

from schnapsen.game import Bot, Move, PlayerGameState


class AlphaBetaBot(Bot):
    def __init__(self) -> None:
        super().__init__()

    def get_move(self, state: PlayerGameState, leader_move: Optional[Move]) -> Move:
        raise NotImplementedError()

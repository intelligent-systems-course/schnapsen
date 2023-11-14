from typing import Optional

from schnapsen.game import Bot, Move, PlayerPerspective


class AlphaBetaBot(Bot):
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        raise NotImplementedError()

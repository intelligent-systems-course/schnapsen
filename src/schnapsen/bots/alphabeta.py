from typing import Optional

from schnapsen.game import Bot, Move, PlayerPerspective


class AlphaBetaBot(Bot):
    def __init__(self) -> None:
        super().__init__()

    def get_move(self, player_perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        raise NotImplementedError()

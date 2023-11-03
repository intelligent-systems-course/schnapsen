from typing import Optional

from schnapsen.game import Bot, Move, PlayerPerspective


class AlphaBetaBot(Bot):
    def __init__(self, name: str = "alphabetabot") -> None:
        super().__init__(name)

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        raise NotImplementedError()

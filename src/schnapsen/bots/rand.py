import random
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move


class RandBot(Bot):
    def __init__(self, rand: random.Random, name: Optional[str] = None) -> None:
        super().__init__(name)
        self.rng = rand

    def get_move(
        self,
        perspective: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:
        moves: list[Move] = perspective.valid_moves()
        move = self.rng.choice(moves)
        return move

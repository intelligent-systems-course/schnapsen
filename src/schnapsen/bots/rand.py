import random
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move


class RandBot(Bot):
    def __init__(self, rand: random.Random, name: Optional[str] = None) -> None:
        super().__init__(name)
        self.rng = rand

    def get_move(
        self,
        state: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:
        moves: list[Move] = state.valid_moves()
        move = self.rng.choice(list(moves))
        return move

    def __repr__(self) -> str:
        return f"RandBot(rng={self.rng})"

import random
from typing import Optional
from schnapsen.game import Bot, PlayerGameState, Move


class RandBot(Bot):
    # TODO: This class should replace the RandBot class defined in src/schnapsen/cli.py
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.rng = random.Random(self.seed)

    def get_move(
        self,
        state: PlayerGameState,
        leader_move: Optional[Move],
    ) -> Move:
        moves = state.valid_moves()
        move = self.rng.choice(list(moves))
        return move

    def __repr__(self) -> str:
        return f"RandBot(seed={self.seed})"

import random
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move


class RandBot(Bot):
    """This bot plays random moves, deterministically using the random number generator provided.

    Args:
        rand (random.Random): The random number generator used to make the random choice of cards
        name (Optional[str]): The optional name of this bot
    """
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

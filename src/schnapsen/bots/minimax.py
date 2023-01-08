"""The minimax algorithm only works when you know the global state. That is, you have
to know the cards of both yours and your opponents. Otherwise, you can't make a search 
tree."""
import random
from typing import Optional

from ..game import Bot, Move, PartialTrick, PlayerGameState


class MiniMaxBot(Bot):
    def __init__(self, randomize: bool = True, depth: int = 8, seed: int = 42) -> None:
        self.randomize = randomize
        self.max_depth = depth
        self.seed = seed
        self.rng = random.Random(self.seed)

    def get_move(
        self, state: PlayerGameState, leader_move: Optional[PartialTrick]
    ) -> Move:
        try:
            state.get_opponent_hand_in_phase_two()
        except AssertionError:
            # We can't do MiniMax in phase 1. We'll resort to random.
            moves = state.valid_moves()
            move = self.rng.choice(list(moves))

            return move

        print(f"am_i_leader: {state.am_i_leader()}")
        print(f"leader_move: {leader_move}")
        print(f"valid moves: {state.valid_moves()}")
        print(f"get_hand: {state.get_hand()}")
        print(f"get_my_score: {state.get_my_score()}")
        print(f"get_opponent_score: {state.get_opponent_score()}")
        print(f"get_opponent_hand_in_phase_two: {state.get_opponent_hand_in_phase_two()}")
        print(f"get_won_cards: {state.get_won_cards()}")
        print(f"get_opponent_won_cards: {state.get_opponent_won_cards()}")

        moves = state.valid_moves()
        import pdb; pdb.set_trace()

        move = self.rng.choice(list(moves))

        print(f"valid moves: {moves}")
        print(f"move: {move}")
        print()

        return move

    def __repr__(self) -> str:
        return (
            f"MiniMaxBot(randomize={self.randomize}, depth={self.max_depth}, "
            f"seed={self.seed})"
        )

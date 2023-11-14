from typing import Optional

from schnapsen.game import (
    Bot,
    Move,
    PlayerPerspective,
    GamePhase,
    GameState,
    FollowerPerspective,
    LeaderPerspective,
    GamePlayEngine,
    SchnapsenTrickScorer,
)
from .minimax import OneFixedMoveBot

import random


class AlphaBetaBot(Bot):
    """
    A bot playing the alphabetga strategy in the second phase of the game.
    It cannot be used for the first phase. What you can do is delegate from your own bot
    to this one in the second phase.

    This would look something like:

    class YourBot(Bot):
        def __init__(self):
            self.delegate_phase2 = MiniMaxBot()
        def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
            if state.get_phase() == GamePhase.TWO:
                return self.delegate_phase2.get_move(state, leader_move)
            else:
                # The logic of your bot
    """

    def __init__(self) -> None:
        super().__init__()
        self.fake_rand = random.Random(0)

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        assert (
            state.get_phase() == GamePhase.TWO
        ), "AlphaBetaBot can only work in the second phase of the game."
        _, move = self.value(
            state.make_assumption(leader_move=leader_move, rand=self.fake_rand),
            state.get_engine(),
            leader_move=leader_move,
            maximizing=True,
        )
        assert move
        return move

    def value(
        self,
        state: GameState,
        engine: GamePlayEngine,
        leader_move: Optional[Move],
        maximizing: bool,
        alpha: float = float("-inf"),
        beta: float = float("inf"),
    ) -> tuple[float, Optional[Move]]:
        my_perspective: PlayerPerspective
        if leader_move is None:
            # we are the leader
            my_perspective = LeaderPerspective(state, engine)
        else:
            my_perspective = FollowerPerspective(state, engine, leader_move)
        valid_moves = my_perspective.valid_moves()

        best_value = float("-inf") if maximizing else float("inf")
        best_move: Optional[Move] = None
        for move in valid_moves:
            leader: Bot
            follower: Bot
            if leader_move is None:
                # we are leader,
                value, _ = self.value(
                    state=state,
                    engine=engine,
                    leader_move=move,
                    maximizing=not maximizing,
                    alpha=alpha,
                    beta=beta,
                )
            else:
                # We are the follower.
                leader = OneFixedMoveBot(leader_move)
                follower = OneFixedMoveBot(move)
                new_game_state, rounds = engine.play_at_most_n_tricks(
                    game_state=state, new_leader=leader, new_follower=follower, n=1
                )
                assert rounds == 1
                winning_info = SchnapsenTrickScorer().declare_winner(new_game_state)
                if winning_info:
                    winner = winning_info[0].implementation
                    points = winning_info[1]
                    follower_wins = winner == follower
                    if not follower_wins:
                        assert winner == leader
                    if not follower_wins:
                        points = -points
                    if not maximizing:
                        points = -points
                    value = points
                else:
                    # play the next round by doing a recursive call
                    leader_stayed = leader == new_game_state.leader.implementation

                    if leader_stayed:
                        next_maximizing = not maximizing
                    else:  # if not leader_stayed
                        next_maximizing = maximizing
                    value, _ = self.value(
                        new_game_state, engine, None, next_maximizing, alpha, beta
                    )
            if maximizing:
                if value > best_value:
                    best_move = move
                    best_value = value
                alpha = max(alpha, best_value)  # alphabeta pruning
                if beta <= alpha:
                    break
            else:
                if value < best_value:
                    best_move = move
                    best_value = value
                beta = min(beta, best_value)  # alphabeta pruning
                if beta <= alpha:
                    break
        return best_value, best_move

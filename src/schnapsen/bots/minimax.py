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


class MiniMaxBot(Bot):
    """
    A bot playing the minimax strategy in the second phase of the game.
    It cannot be used for the first phase. What you can do is delegate from your own bot to this one in the second phase.
    This would look something like:
    <pre>
    class YourBot(Bot):
        def __init__(self):
            self.delegate_phase2 = MiniMaxBot()
        def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
            if state.get_phase() == GamePhase.TWO:
                return self.delegate_phase2.get_move(state, leader_move)
            else:
                # The logic of your bot
    </pre>
    """

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        assert (perspective.get_phase() == GamePhase.TWO), "MiniMaxBot can only work in the second phase of the game."
        _, move = self.value(
            perspective.get_state_in_phase_two(),
            perspective.get_engine(),
            leader_move=leader_move,
            maximizing=True,
        )
        return move

    def value(
        self,
        state: GameState,
        engine: GamePlayEngine,
        leader_move: Optional[Move],
        maximizing: bool,
    ) -> tuple[float, Move]:
        """Get the score and the corresponding move which eithers maxmizes or minimizes the objective.

        Args:
            state (GameState): The current state of the game
            engine (GamePlayEngine): _description_
            leader_move (Optional[Move]): _description_
            maximizing (bool): _description_

        Returns:
            tuple[float, Optional[Move]]: _description_
        """
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
                # we are leader, call self to get the follower to play
                value, _ = self.value(
                    state=state,
                    engine=engine,
                    leader_move=move,
                    maximizing=not maximizing,
                )
            else:
                # We are the follower. We need to complete the trick and then call self to play the next trick, with the correct maximizing, depending on who is the new leader
                leader = OneFixedMoveBot(leader_move)
                follower = OneFixedMoveBot(move)
                new_game_state = engine.play_one_trick(game_state=state, new_leader=leader, new_follower=follower)
                winning_info = SchnapsenTrickScorer().declare_winner(new_game_state)
                if winning_info:
                    winner = winning_info[0].implementation
                    points = winning_info[1]
                    follower_wins = winner == follower

                    if not follower_wins:
                        points = -points
                    if not maximizing:
                        points = -points
                    value = points
                else:
                    # play the next round by doing a recursive call
                    leader_stayed = leader == new_game_state.leader.implementation

                    if leader_stayed:
                        # At the next step, the leader is our opponent, and it will be doing the opposite of what we do.
                        next_maximizing = not maximizing
                    else:  # if not leader_stayed
                        # At the next step we will have become the leader, so we will keep doing what we did
                        next_maximizing = maximizing
                    # implementation note: the previous two case could be written with a xor, but this seemed more readable
                    value, _ = self.value(new_game_state, engine, None, next_maximizing)
            if maximizing and value > best_value:
                best_move = move
                best_value = value
            elif not maximizing and value < best_value:
                best_move = move
                best_value = value
        assert best_move  # We are sure the best_move can no longer be None. We assert to make sure we did not make a logical mistake
        return best_value, best_move


class OneFixedMoveBot(Bot):
    def __init__(self, move: Move) -> None:
        self.first_move: Optional[Move] = move

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        assert self.first_move, "This bot can only play one move, after that it ends"
        move = self.first_move
        self.first_move = None
        return move

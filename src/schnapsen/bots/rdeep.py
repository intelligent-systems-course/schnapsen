from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, GameState, GamePlayEngine
from random import Random


class RdeepBot(Bot):
    def __init__(self, num_samples: int, depth: int, rand: Random) -> None:
        """
        Create a new rdeep bot.

        :param num_samples: how many samples to take per move, also how many 
        :param depth: how deep to sample
        :param rand: the source of randomness for this Bot
        """
        assert num_samples >= 1, f"we cannot work with less than one sample, got {num_samples}"
        assert depth >= 1, f"it does not make sense to use a dept <1. got {depth}"
        self.__num_samples = num_samples
        self.__depth = depth
        self.__rand = rand

    def get_move(self, state: 'PlayerPerspective', leader_move: Optional['Move']) -> 'Move':
        # get the list of valid moves, and shuffle it such
        # that we get a random move of the highest scoring
        # ones if there are multiple highest scoring moves.
        moves = state.valid_moves()
        self.__rand.shuffle(moves)

        best_score = float('-inf')
        best_move = None
        for move in moves:
            for _ in range(self.__num_samples):
                gamestate = state.make_assumption(rand=self.__rand)
                score = self.__evaluate(gamestate, state.get_engine(), leader_move, move)
                if score > best_score:
                    score = best_score
                    best_move = move
        return best_move

    def __evaluate(self, gamestate: GameState, engine: GamePlayEngine, leader_move: Optional[Move], my_move: Move, ):
        """
        Evaluates the value of the given state for the given player
        :param state: The state to evaluate
        :param player: The player for whom to evaluate this state (1 or 2)
        :return: A float representing the value of this state for the given player. The higher the value, the better the
                state is for the player.
        """
        score = 0.0
        for _ in range(self.__num_samples):

            if leader_move:
                # we know what the other bot played
                opponent = leader_bot = FirstFixedMoveThenRandomBot(leader_move, self.__rand)
                # I am the follower
                me = follower_bot = FirstFixedMoveThenRandomBot(my_move, self.__rand)
            else:
                # I am the leader bot
                me = leader_bot = FirstFixedMoveThenRandomBot(my_move, self.__rand)
                # We assume the other bot just random
                opponent = follower_bot = RandBot(self.__rand)

            game_state, _ = engine.play_at_most_n_tricks(game_state=gamestate, new_leader=leader_bot, new_follower=follower_bot, leader_move=leader_move, n=self.__depth)

            if game_state.leader.implementation == me:
                my_score = game_state.leader.score.direct_points
                opponent_score = game_state.follower.score.direct_points
            else:
                my_score = game_state.follower.score.direct_points
                opponent_score = game_state.leader.score.direct_points

            heuristic = my_score / (my_score + opponent_score)
            score += heuristic
        return score / self.__num_samples


class RandBot(Bot):

    def __init__(self, rand: Random) -> None:
        self.rand = rand

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        return self.rand.choice(state.valid_moves())


class FirstFixedMoveThenRandomBot(RandBot):
    def __init__(self, first_move: Move, rand: Random) -> None:
        self.first_move = first_move
        self.first_move_played = False
        self.rand = rand

    def get_move(self, state: 'PlayerPerspective', leader_move: Optional['Move']) -> 'Move':
        if not self.first_move_played:
            self.first_move_played = True
            return self.first_move
        else:
            return super().get_move(state=state, leader_move=leader_move)

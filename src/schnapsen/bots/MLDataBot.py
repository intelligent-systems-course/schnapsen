from src.schnapsen.game import Bot, PlayerGameState, PartialTrick, Move, Trick
from src.schnapsen.bots.MLBaseBot import MLBaseBot
from typing import Optional, Tuple, List

class MLDataBot(MLBaseBot):
    '''
    This class is defined to allow the creation of a training schnapsen bot dataset, that allows us to train a Machine Learning (ML) Bot
    Practically, it helps us record how the game plays out according to a provided Bot behaviour; build what is called a "replay memory"
    In more detail, we create one training sample for each decision the bot makes within a game, where a decision is an action selection for a specific game state.
    Then we relate each decision with the outcome of the game, i.e. whether this bot won or not.
    This way we can then train a bot according to the assumption that:
        "decisions in earlier games that ended up in victories should be preferred over decisions that lead to lost games"
    This class only records the decisions and game outcomes of the provided bot, according to its own perspective - incomplete game state knowledge.
    '''
    def __init__(self, bot: Bot) -> None:
        '''
        bot: the provided bot that will actually play the game and make decisions
        '''
        get also a filename, and append the recored replay memories on this file,
        super().__init__()
        self.bot = bot
        self.my_history: Optional[list[tuple[PlayerGameState, Optional[Trick]]]] = None

        self.last_leader_trick: Optional[PartialTrick] = None
        self.my_last_move: Optional[Move] = None

    def get_move(self, state: PlayerGameState, leader_move: Optional[PartialTrick]) -> Move:
        '''
            This function simply calls the get_move of the provided bot, while also allows us to additionally record the game replay
        '''
        selected_move = self.bot.get_move(state=state, leader_move=leader_move)
        if state.am_i_leader() and leader_move is not None:
            raise ValueError("This bot cannot be the leader and at the same time being provided a leader move to respond to as follower!")
        #  to same computational effort, we only need to call the get_game_history() towards the end of the game, so we check the amount of player's cards
        if len(state. get_hand().get_cards()) <= 2:
            self.my_history = state.get_game_history()
            # self.last_leader_trick = leader_move
            # self.my_last_move = selected_move
        return selected_move


    def get_game_replay_training_samples(self, is_winner) -> List[Tuple[np.ndarray, bool]]:
        # game_history: List[Tuple[PlayerGameState, Optional[Trick]]], last_move: Move, was_winner: bool)
        #
        # # last round is treated differently, since the move of the agents is not stored there.
        # last_round_history = self.my_history[0]
        # last_player_game_state: PlayerGameState =

        for player_game_state, leader_trick in self.my_history:

            i_was_leader = player_game_state.am_i_leader()

            if i_was_leader and leader_trick is not None:
                raise ValueError("The history of this agent is not correct, as it was the leader but the leader move in its history has a value!")
            elif i_was_leader == False and leader_trick is None:
                raise ValueError("The history of this agent is not correct, as it was not the leader but the leader move in its history has no value!")


            if i_was_leader:
                leader_move = self.
            # state_feature_representation = MLBaseBot.get_state_feature_vector(player_game_state, trick)




            was_leader = player_game_state.am_i_leader()
            # if this was the leader of that round, then we encode the game state, and this agent's action
            if was_leader:
                state_feature_representation = MLBaseBot.get_state_feature_vector(player_game_state, leader_trick)

                leader_trick_feature_representation: np.ndarray = MLBaseBot.get_move_feature_vector(leader_move)

            # # add this features to the feature set
            # state_feature_list.append(leader_trick_feature_representation)

            leader_move = trick.l


            leader_move =


        # for

        # return []
        pass

    # def __repr__(self) -> str:
    #     return f"HistoryBot(seed={self.seed})"

from src.schnapsen.game import Bot, PlayerGameState, PartialTrick, SchnapsenDeckGenerator, Move, Trick, GamePhase, ExchangeTrick
from typing import Optional
import numpy as np
from typing import Iterable, List, Optional, Tuple, Union, cast, Any
from src.schnapsen.deck import Suit, Rank
import numpy.typing as npt


class MLPlayingBot(Bot):
    '''
    This class loads a trained ML model and uses it to play
    '''
    def __init__(self) -> None:
        super().__init__()
        # load model

    def get_move(self, state: 'PlayerGameState', leader_move: Optional[PartialTrick]) -> 'Move':
        # get valid actions
        # get state representation
        # for each action:
            # get action representation and total representation
            # pass it through the model and get estimated probability of winning per action
        # select action with the highest probability of winning
        # return this move
        pass

class MLDataBot(Bot):
    '''
    This class is defined to allow the creation of a training schnapsen bot dataset, that allows us to train a Machine Learning (ML) Bot
    Practically, it helps us record how the game plays out according to a provided Bot behaviour; build what is called a "replay memory"
    In more detail, we create one training sample for each decision the bot makes within a game, where a decision is an action selection for a specific game state.
    Then we relate each decision with the outcome of the game, i.e. whether this bot won or not.
    This way we can then train a bot according to the assumption that:
        "decisions in earlier games that ended up in victories should be preferred over decisions that lead to lost games"
    This class only records the decisions and game outcomes of the provided bot, according to its own perspective - incomplete game state knowledge.
    The replay memories are stored under the directory "ML_replay_memories" in a file whose filename
    is passed through the parameter "replay_memory_filename" when creating a MLDataBot object.
    '''
    def __init__(self, bot: Bot, replay_memory_filename: str) -> None:
        '''
        bot: the provided bot that will actually play the game and make decisions
        replay_memory_filename: the filename under which the replay memory records will be stored, under the directory "ML_replay_memories"
        '''
        self.bot = bot
        self.my_history: Optional[list[tuple[PlayerGameState, Optional[Trick]]]] = None
        self.replay_memory_filename = replay_memory_filename

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

        # we iterate over all the rounds of the game, and ignore teh
        for player_game_state, round_trick in self.my_history[1:]:

            #  in case
            if round_trick is None:


            i_was_leader = player_game_state.am_i_leader()

            if i_was_leader and leader_trick is not None:
                raise ValueError("The history of this agent is not correct, as it was the leader but the leader move in its history has a value!")
            elif i_was_leader == False and leader_trick is None:
                raise ValueError("The history of this agent is not correct, as it was not the leader but the leader move in its history has no value!")


            if i_was_leader:
                leader_move = self.
            # state_feature_representation = get_state_feature_vector(player_game_state, trick)




            was_leader = player_game_state.am_i_leader()
            # if this was the leader of that round, then we encode the game state, and this agent's action
            if was_leader:
                state_feature_representation = get_state_feature_vector(player_game_state, leader_trick)

                leader_trick_feature_representation: np.ndarray = get_move_feature_vector(leader_move)

            # # add this features to the feature set
            # state_feature_list.append(leader_trick_feature_representation)

            leader_move = trick.l


            leader_move =


        # for

        # return [

    # def __repr__(self) -> str:
    #     return f"HistoryBot(seed={self.seed})"

def train_ML_model():
    pass

def create_state_and_actions_vector_representation(player_game_state: PlayerGameState, leader_move: Optional[Move], follower_move: Optional[Move]) -> np.ndarray:
    '''
    This function takes as input a PlayerGameState variable, and the two moves of leader and follower, and returns one complete feature representation that contains all information
    '''
    player_game_state_representation = get_state_feature_vector(player_game_state)
    leader_move_representation = get_move_feature_vector(leader_move)
    follower_move_representation = get_move_feature_vector(follower_move)

    complete_feature_representation = np.concatenate \
        ((player_game_state_representation, leader_move_representation, follower_move_representation), axis=0)
    return complete_feature_representation


def get_one_hot_encoding_of_card_suit(card_suit: Suit) -> np.ndarray:
    '''
    Translating the suit of a card into one hot vector encoding of size 4 and type of numpy ndarray.
    '''
    card_suit_one_hot: list[int]
    if card_suit == Suit.HEARTS:
        card_suit_one_hot = [0, 0, 0, 1]
    elif card_suit == Suit.CLUBS:
        card_suit_one_hot = [0, 0, 1, 0]
    elif card_suit == Suit.SPADES:
        card_suit_one_hot = [0, 1, 0, 0]
    else:
        card_suit_one_hot = [1, 0, 0, 0]
    return np.array(card_suit_one_hot, dtype=np.int_)

def get_one_hot_encoding_of_card_rank(card_rank: Rank) -> np.ndarray:
    '''
    Translating the rank of a card into one hot vector encoding of size 13 and type of numpy ndarray.
    '''
    card_rank_one_hot: list[int]
    if card_rank == Rank.ACE:
        card_rank_one_hot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    elif card_rank == Rank.TWO:
        card_rank_one_hot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
    elif card_rank == Rank.THREE:
        card_rank_one_hot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
    elif card_rank == Rank.FOUR:
        card_rank_one_hot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    elif card_rank == Rank.FIVE:
        card_rank_one_hot = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
    elif card_rank == Rank.SIX:
        card_rank_one_hot = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    elif card_rank == Rank.SEVEN:
        card_rank_one_hot = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    elif card_rank == Rank.EIGHT:
        card_rank_one_hot = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    elif card_rank == Rank.NINE:
        card_rank_one_hot = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    elif card_rank == Rank.TEN:
        card_rank_one_hot = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    elif card_rank == Rank.JACK:
        card_rank_one_hot = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    elif card_rank == Rank.QUEEN:
        card_rank_one_hot = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        card_rank_one_hot = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    return np.array(card_rank_one_hot, dtype=np.int_)

def get_move_feature_vector(move: Optional[Move]) -> np.ndarray:
    '''
        in case there isn't any move provided move to encode, we still need to create a "padding"-"meaningless" vector of the same size,
        filled with 0s, since the ML models need to receive input of the same dimensionality always.
        Otherwise, we create all the ifnormation of the move i) move type, ii) played card rank and iii) played card suit
        translate this information into one-hot vectors respectively, and concatenate these vectors into one move feature representation vector
    '''

    if move is None:
        move_type_one_hot_encoding_numpy_array = np.array([0, 0, 0], dtype=np.int_)
        card_rank_one_hot_encoding_numpy_array = np.array([0, 0, 0, 0], dtype=np.int_)
        card_suit_one_hot_encoding_numpy_array = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.int_)

    else:
        move_type_one_hot_encoding: list[int]
        # in case the move is a marriage move
        if move.is_marriage():
            move_type_one_hot_encoding = [0, 0, 1]
            card = move.queen_card
        #  in case the move is a trump exchange move
        elif move.is_trump_exchange():
            move_type_one_hot_encoding = [0, 1, 0]
            card = move.jack
        #  in case it is a regular move
        else:
            move_type_one_hot_encoding = [1, 0, 0]
            card = move.card
        move_type_one_hot_encoding_numpy_array: np.ndarray = np.array(move_type_one_hot_encoding, dtype=np.int_)
        card_rank_one_hot_encoding_numpy_array: np.ndarray = get_one_hot_encoding_of_card_rank(card.rank)
        card_suit_one_hot_encoding_numpy_array: np.ndarray = get_one_hot_encoding_of_card_suit(card.suit)

    move_feature_vector_numpy = np.concatenate((move_type_one_hot_encoding_numpy_array,
                                                card_rank_one_hot_encoding_numpy_array, card_suit_one_hot_encoding_numpy_array), axis=0)

    return move_feature_vector_numpy

def get_state_feature_vector(player_game_state: PlayerGameState) -> np.ndarray:
    '''
        This function gathers all subjective information that this bot has access to, that can be used to decide its next move, including:
        - points of this player (int)
        - points of the opponent (int)
        - pending points of this player (int)
        - pending points of opponent (int)
        - the trump suit (1-hot encoding)
        - phase of game (1-hoy encoding)
        - talon size (int)
        - if this player is leader (1-hot encoding)
        - What is the status of each card of the deck (where it is, or if its location is unknown)

        Important: This function should not include the move of this agent.
        It should only include any earlier actions of other agents (so the action of the other agent in case that is the leader)
    '''
    # a list of all the features that consist the state feature set, of type np.ndarray
    state_feature_list: List[np.ndarray] = []

    player_score = player_game_state.get_my_score()
    # - points of this player (int)
    player_points = player_score.direct_points
    # - pending points of this player (int)
    player_pending_points = player_score.pending_points

    # add the features to the feature set
    state_feature_list.append(np.array([player_points], np.int_))
    state_feature_list.append(np.array([player_pending_points], np.int_))

    opponents_score = player_game_state.get_opponent_score()
    # - points of the opponent (int)
    opponents_points = opponents_score.direct_points
    # - pending points of opponent (int)
    opponents_pending_points = opponents_score.pending_points

    # add the features to the feature set
    state_feature_list.append(np.array([opponents_points], np.int_))
    state_feature_list.append(np.array([opponents_pending_points], np.int_))

    # - the trump suit (1-hot encoding)
    trump_suit = player_game_state.get_trump_suit()
    trump_suit_one_hot_numpy_array = get_one_hot_encoding_of_card_suit(trump_suit)
    # add this features to the feature set
    state_feature_list.append(trump_suit_one_hot_numpy_array)

    # - phase of game (1-hot encoding)
    game_phase_encoded = [1, 0] if player_game_state.get_phase() == GamePhase.TWO else [0, 1]
    # add this features to the feature set
    state_feature_list.append(np.array(game_phase_encoded, dtype=np.int_))

    # - talon size (int)
    talon_size = player_game_state.get_talon_size()
    # add this features to the feature set
    state_feature_list.append(np.array([talon_size], dtype=np.int_))

    # - if this player is leader (1-hot encoding)
    i_am_leader = [0, 1] if player_game_state.am_i_leader() == GamePhase.TWO else [1, 0]
    # add this features to the feature set
    state_feature_list.append(np.array(i_am_leader, dtype=np.int_))

    # gather all known deck information
    hand = player_game_state.get_hand()
    trump_card = player_game_state.get_trump_card()
    won_cards = player_game_state.get_won_cards()
    opponent_won_cards = player_game_state.get_opponent_won_cards()
    opponent_known_cards = player_game_state.get_known_cards_of_opponent_hand()
    # each card can either be i) on player's hand, ii) on player's won cards, iii) on opponent's hand, iv) on opponent's won cards
    # v) be the trump card or vi) in an unknown position -> either on the talon or on the opponent's hand
    # There are all different cases regarding card's knowledge, and we represent these 6 cases using one hot encoding vectors as seen bellow.

    deck_knowledge_in_one_hot_encoding: list[np.ndarray] = []

    for card in SchnapsenDeckGenerator.get_initial_deck():
        card_knowledge_in_one_hot_encoding: list[int]
        # i) on player's hand
        if card in hand:
            card_knowledge_in_one_hot_encoding = [0, 0, 0, 0, 0, 1]
        # ii) on player's won cards
        elif card in won_cards:
            card_knowledge_in_one_hot_encoding = [0, 0, 0, 0, 1, 0]
        # iii) on opponent's hand
        elif card in opponent_known_cards:
            card_knowledge_in_one_hot_encoding = [0, 0, 0, 1, 0, 0]
        # iv) on opponent's won cards
        elif card in opponent_won_cards:
            card_knowledge_in_one_hot_encoding = [0, 0, 1, 0, 0, 0]
        # v) be the trump card
        elif card == trump_card:
            card_knowledge_in_one_hot_encoding = [0, 1, 0, 0, 0, 0]
        # vi) in an unknown position as it is invisible to this player. Thus, it is either on the talon or on the opponent's hand
        else:
            card_knowledge_in_one_hot_encoding = [1, 0, 0, 0, 0, 0]
        # translating the one hot encoding from list to a numpy array
        card_knowledge_in_one_hot_encoding_numpy_array: np.ndarray = np.array(card_knowledge_in_one_hot_encoding, dtype=np.int_)
        # this results to a list of length 20, where each element is a numpy array of shape (6,)
        deck_knowledge_in_one_hot_encoding.append(card_knowledge_in_one_hot_encoding_numpy_array)
    # Translating the list of numpy arrays into one long 1-dimensional numpy array of shape (120,)
    deck_knowledge_flattened: np.ndarray = np.concatenate(tuple(deck_knowledge_in_one_hot_encoding), axis=0)

    # add this features to the feature set
    state_feature_list.append(deck_knowledge_flattened)

    # concatenate all feature vectors into one single dimension - flattened - feature vector
    state_feature_vector_flattened: np.ndarray = np.concatenate(tuple(state_feature_list), axis=0)

    return state_feature_vector_flattened


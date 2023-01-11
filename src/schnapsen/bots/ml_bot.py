from schnapsen.game import Bot, PlayerPerspective, SchnapsenDeckGenerator, Move, Trick, GamePhase
from typing import List, Optional, cast
from schnapsen.deck import Suit, Rank
from sklearn.neural_network import MLPClassifier
import joblib
import os
import time


class MLPlayingBot(Bot):
    """
    This class loads a trained ML model and uses it to play
    """

    def __init__(self, model_name: str = 'test_model', model_dir: str = "ML_models") -> None:
        model_file_path = os.path.join(model_dir, model_name)
        if not os.path.exists(model_file_path):
            raise ValueError("Model could not be found at: " + model_file_path)
        else:
            # load model
            self.__model = joblib.load(model_file_path)

    def get_move(self, player_perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        # get the sate feature representation
        state_representation = get_state_feature_vector(player_perspective)
        # get the leader's move representation, even if it is None
        leader_move_representation = get_move_feature_vector(leader_move)
        # get all my valid moves
        my_valid_moves = player_perspective.valid_moves()
        # get the feature representations for all my valid moves
        my_move_representations: list[list[int]] = []
        for my_move in my_valid_moves:
            my_move_representations.append(get_move_feature_vector(my_move))

        # create all model inputs, for all bot's valid moves
        action_state_representations: list[list[int]] = []

        if player_perspective.am_i_leader():
            follower_move_representation = get_move_feature_vector(None)
            for my_move_representation in my_move_representations:
                action_state_representations.append(

                    state_representation + my_move_representation + follower_move_representation)
        else:
            for my_move_representation in my_move_representations:
                action_state_representations.append(
                    state_representation + leader_move_representation + my_move_representation)

        model_output = self.__model.predict_proba(action_state_representations)
        winning_probabilities_of_moves = [outcome_prob[1] for outcome_prob in model_output]
        highest_value: float = -1
        best_move: Move
        for index, value in enumerate(winning_probabilities_of_moves):
            if value > highest_value:
                highest_value = value
                best_move = my_valid_moves[index]
        assert best_move
        return best_move


class MLDataBot(Bot):
    """
    This class is defined to allow the creation of a training schnapsen bot dataset, that allows us to train a Machine Learning (ML) Bot
    Practically, it helps us record how the game plays out according to a provided Bot behaviour; build what is called a "replay memory"
    In more detail, we create one training sample for each decision the bot makes within a game, where a decision is an action selection for a specific game state.
    Then we relate each decision with the outcome of the game, i.e. whether this bot won or not.
    This way we can then train a bot according to the assumption that:
        "decisions in earlier games that ended up in victories should be preferred over decisions that lead to lost games"
    This class only records the decisions and game outcomes of the provided bot, according to its own perspective - incomplete game state knowledge.
    The replay memories are stored under the directory "ML_replay_memories" in a file whose filename
    is passed through the parameter "replay_memory_filename" when creating a MLDataBot object.
    """

    def __init__(self, bot: Bot, replay_memory_file_path: str) -> None:
        """
        bot: the provided bot that will actually play the game and make decisions
        replay_memory_filename: the filename under which the replay memory records will be stored, under the directory "ML_replay_memories"
        """
        self.bot: Bot = bot
        # self.my_history: Optional[list[tuple[PlayerPerspective, Optional[PartialTrick]]]] = None
        self.replay_memory_file_path: str = replay_memory_file_path

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """
            This function simply calls the get_move of the provided bot
        """
        return self.bot.get_move(state=state, leader_move=leader_move)

    def notify_game_end(self, won: bool, player_perspective: PlayerPerspective) -> None:
        """
        When the game ends, this function retrieves the game history and more specifically all the replay memories that can
        be derived from it, and stores them in the form of state-actions vector representations and the corresponding outcome of the game

        param won: Did this bot win the game?
        param player_perspective: The final state of the game.
        """
        # we retrieve the game history while actually discarding the last useless history record (which is after the game has ended), we know none of the Tricks can be None
        game_history: list[tuple[PlayerPerspective, Trick]] = cast(list[tuple[PlayerPerspective, Trick]], player_perspective.get_game_history()[:-1])
        # we also save the training label "won or lost"
        won_label = won

        # we iterate over all the rounds of the game
        for round_player_perspective, round_trick in game_history:

            if round_trick.is_trump_exchange():
                leader_move = round_trick.exchange
                follower_move = None
            else:
                leader_move = round_trick.leader_move
                follower_move = round_trick.follower_move

            # we do not want this representation to include actions that followed. So if this agent was the leader, we ignore the followers move
            if round_player_perspective.am_i_leader():
                follower_move = None

            state_actions_representation = create_state_and_actions_vector_representation(
                player_perspective=round_player_perspective, leader_move=leader_move, follower_move=follower_move)

            # append replay memory to file
            with open(file=self.replay_memory_file_path, mode="a") as replay_memory_file:
                # replay_memory_line: List[Tuple[list, number]] = [state_actions_representation, won_label]
                # writing to replay memory file in the form "[feature list] || int(won_label)]
                replay_memory_file.write(f"{str(state_actions_representation)[1:-1]} || {int(won_label)}\n")


def train_ML_model(replay_memory_filename: str = 'test_replay_memory',
                   replay_memories_directory: str = 'ML_replay_memories',
                   model_name: str = 'test_model', model_dir: str = "ML_models", overwrite: bool = True) -> None:
    # check if directory exists, and if not, then create it
    if not os.path.exists(model_dir):
        os.mkdir(model_dir)

    # Check if model exists already
    model_file_path = os.path.join(model_dir, model_name)
    if os.path.exists(model_file_path):
        if overwrite:
            print(
                "Model with name: " + model_name + ", in directory: " + model_dir + ", exists already and will be overwritten as selected.")
            os.remove(model_file_path)
        else:
            raise ValueError(
                "Model with name: " + model_name + ", in directory: " + model_dir + ", exists already and overwrite is set to False."
                "\nNo new model will be trained, process terminates")

    replay_memory_file_path = os.path.join(replay_memories_directory, replay_memory_filename)

    # check that the replay memory dataset is found at the specified location
    if not os.path.exists(replay_memory_file_path):
        raise ValueError(f"Dataset was not found at: {replay_memory_file_path} !")

    data: list[list[int]] = []
    targets: list[int] = []
    with open(file=replay_memory_file_path, mode="r") as replay_memory_file:
        for line in replay_memory_file:
            feature_string, won_label_str = line.split("||")
            feature_list_strings: list[str] = feature_string.split(",")
            feature_list = [int(feature) for feature in feature_list_strings]
            won_label = int(won_label_str)
            data.append(feature_list)
            targets.append(won_label)

    print("Dataset Statistics:")
    samples_of_wins = sum(targets)
    samples_of_losses = len(targets) - samples_of_wins
    print("Samples of wins:", samples_of_wins)
    print("Samples of losses:", samples_of_losses)

    # Play around with the model parameters below

    # HINT: Use tournament fast mode (-f flag) to quickly test your different models.

    # The following tuple specifies the number of hidden layers in the neural
    # network, as well as the number of layers, implicitly through its length.
    # You can set any number of hidden layers, even just one. Experiment and see what works.
    hidden_layer_sizes = (64, 32)

    # The learning rate determines how fast we move towards the optimal solution.
    # A low learning rate will converge slowly, but a large one might overshoot.
    learning_rate = 0.0001

    # The regularization term aims to prevent overfitting, and we can tweak its strength here.
    regularization_strength = 0.0001

    #############################################

    start = time.time()

    print("Starting training phase...")

    # Train a neural network
    learner = MLPClassifier(hidden_layer_sizes=hidden_layer_sizes, learning_rate_init=learning_rate,
                            alpha=regularization_strength, verbose=True, early_stopping=True, n_iter_no_change=6)
    # learner = sklearn.linear_model.LogisticRegression()

    model = learner.fit(data, targets)

    # Store the model
    joblib.dump(model, model_file_path)

    end = time.time()

    print('Done. Time to train:', (end - start) / 60, 'minutes.')


def create_state_and_actions_vector_representation(player_perspective: PlayerPerspective, leader_move: Optional[Move],
                                                   follower_move: Optional[Move]) -> List[int]:
    """
    This function takes as input a PlayerPerspective variable, and the two moves of leader and follower,
    and returns a list of complete feature representation that contains all information
    """
    player_game_state_representation = get_state_feature_vector(player_perspective)
    leader_move_representation = get_move_feature_vector(leader_move)
    follower_move_representation = get_move_feature_vector(follower_move)

    return player_game_state_representation + leader_move_representation + follower_move_representation


def get_one_hot_encoding_of_card_suit(card_suit: Suit) -> List[int]:
    """
    Translating the suit of a card into one hot vector encoding of size 4 and type of numpy ndarray.
    """
    card_suit_one_hot: list[int]
    if card_suit == Suit.HEARTS:
        card_suit_one_hot = [0, 0, 0, 1]
    elif card_suit == Suit.CLUBS:
        card_suit_one_hot = [0, 0, 1, 0]
    elif card_suit == Suit.SPADES:
        card_suit_one_hot = [0, 1, 0, 0]
    elif card_suit == Suit.DIAMONDS:
        card_suit_one_hot = [1, 0, 0, 0]
    else:
        raise ValueError("Suit of card was not found!")

    return card_suit_one_hot


def get_one_hot_encoding_of_card_rank(card_rank: Rank) -> List[int]:
    """
    Translating the rank of a card into one hot vector encoding of size 13 and type of numpy ndarray.
    """
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
    elif card_rank == Rank.KING:
        card_rank_one_hot = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    else:
        raise AssertionError("Provided card Rank does not exist!")
    return card_rank_one_hot


def get_move_feature_vector(move: Optional[Move]) -> List[int]:
    """
        in case there isn't any move provided move to encode, we still need to create a "padding"-"meaningless" vector of the same size,
        filled with 0s, since the ML models need to receive input of the same dimensionality always.
        Otherwise, we create all the information of the move i) move type, ii) played card rank and iii) played card suit
        translate this information into one-hot vectors respectively, and concatenate these vectors into one move feature representation vector
    """

    if move is None:
        move_type_one_hot_encoding_numpy_array = [0, 0, 0]
        card_rank_one_hot_encoding_numpy_array = [0, 0, 0, 0]
        card_suit_one_hot_encoding_numpy_array = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

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
        move_type_one_hot_encoding_numpy_array = move_type_one_hot_encoding
        card_rank_one_hot_encoding_numpy_array = get_one_hot_encoding_of_card_rank(card.rank)
        card_suit_one_hot_encoding_numpy_array = get_one_hot_encoding_of_card_suit(card.suit)

    return move_type_one_hot_encoding_numpy_array + card_rank_one_hot_encoding_numpy_array + card_suit_one_hot_encoding_numpy_array


def get_state_feature_vector(player_perspective: PlayerPerspective) -> List[int]:
    """
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
    """
    # a list of all the features that consist the state feature set, of type np.ndarray
    state_feature_list: list[int] = []

    player_score = player_perspective.get_my_score()
    # - points of this player (int)
    player_points = player_score.direct_points
    # - pending points of this player (int)
    player_pending_points = player_score.pending_points

    # add the features to the feature set
    state_feature_list += [player_points]
    state_feature_list += [player_pending_points]

    opponents_score = player_perspective.get_opponent_score()
    # - points of the opponent (int)
    opponents_points = opponents_score.direct_points
    # - pending points of opponent (int)
    opponents_pending_points = opponents_score.pending_points

    # add the features to the feature set
    state_feature_list += [opponents_points]
    state_feature_list += [opponents_pending_points]

    # - the trump suit (1-hot encoding)
    trump_suit = player_perspective.get_trump_suit()
    trump_suit_one_hot = get_one_hot_encoding_of_card_suit(trump_suit)
    # add this features to the feature set
    state_feature_list += trump_suit_one_hot

    # - phase of game (1-hot encoding)
    game_phase_encoded = [1, 0] if player_perspective.get_phase() == GamePhase.TWO else [0, 1]
    # add this features to the feature set
    state_feature_list += game_phase_encoded

    # - talon size (int)
    talon_size = player_perspective.get_talon_size()
    # add this features to the feature set
    state_feature_list += [talon_size]

    # - if this player is leader (1-hot encoding)
    i_am_leader = [0, 1] if player_perspective.am_i_leader() else [1, 0]
    # add this features to the feature set
    state_feature_list += i_am_leader

    # gather all known deck information
    hand_cards = player_perspective.get_hand().cards
    trump_card = player_perspective.get_trump_card()
    won_cards = player_perspective.get_won_cards().get_cards()
    opponent_won_cards = player_perspective.get_opponent_won_cards().get_cards()
    opponent_known_cards = player_perspective.get_known_cards_of_opponent_hand().get_cards()
    # each card can either be i) on player's hand, ii) on player's won cards, iii) on opponent's hand, iv) on opponent's won cards
    # v) be the trump card or vi) in an unknown position -> either on the talon or on the opponent's hand
    # There are all different cases regarding card's knowledge, and we represent these 6 cases using one hot encoding vectors as seen bellow.

    deck_knowledge_in_consecutive_one_hot_encodings: list[int] = []

    for card in SchnapsenDeckGenerator.get_initial_deck():
        card_knowledge_in_one_hot_encoding: list[int]
        # i) on player's hand
        if card in hand_cards:
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
        # This list eventually develops to one long 1-dimensional numpy array of shape (120,)
        deck_knowledge_in_consecutive_one_hot_encodings += card_knowledge_in_one_hot_encoding
    # deck_knowledge_flattened: np.ndarray = np.concatenate(tuple(deck_knowledge_in_one_hot_encoding), axis=0)

    # add this features to the feature set
    state_feature_list += deck_knowledge_in_consecutive_one_hot_encodings

    return state_feature_list

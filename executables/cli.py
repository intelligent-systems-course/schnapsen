import os.path
import random
from typing import Optional

import click
from schnapsen.bots import MLDataBot, train_ML_model, MLPlayingBot

from schnapsen.bots.example_bot import ExampleBot

from schnapsen.game import (Bot, Move, PlayerPerspective,
                            SchnapsenGamePlayEngine, Trump_Exchange)
from schnapsen.twenty_four_card_schnapsen import \
    TwentyFourSchnapsenGamePlayEngine

from schnapsen.bots.rdeep import RdeepBot


@click.group()
def main() -> None:
    """Various Schnapsen Game Examples"""


class RandBot(Bot):
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.rng = random.Random(self.seed)

    def get_move(self, player_perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves = player_perspective.valid_moves()
        move = self.rng.choice(list(moves))
        return move

    def __repr__(self) -> str:
        return f"RandBot(seed={self.seed})"


@main.command()
def random_game() -> None:
    engine = SchnapsenGamePlayEngine()
    bot1 = RandBot(12112121)
    bot2 = RandBot(464566)
    for i in range(1000):
        winner_id, game_points, score = engine.play_game(bot1, bot2, random.Random(i))
        print(f"Game ended. Winner is {winner_id} with {game_points} points, score {score}")


class NotificationExampleBot(Bot):

    def get_move(self, player_perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves = player_perspective.valid_moves()
        return moves[0]

    def notify_game_end(self, won: bool, state: PlayerPerspective) -> None:
        print(f'result {"win" if won else "lost"}')
        print(f'I still have {len(state.get_hand())} cards left')

    def notify_trump_exchange(self, move: Trump_Exchange) -> None:
        print(f"That trump exchanged! {move.jack}")


@main.command()
def notification_game() -> None:
    engine = TwentyFourSchnapsenGamePlayEngine()
    bot1 = NotificationExampleBot()
    bot2 = RandBot(464566)
    engine.play_game(bot1, bot2, random.Random(94))


class HistoryBot(Bot):
    def get_move(self, player_perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        history = player_perspective.get_game_history()
        print(f'the initial state of this game was {history[0][0]}')
        moves = player_perspective.valid_moves()
        return moves[0]


@main.group()
def ml() -> None:
    """Commands for the ML bot"""


@ml.command()
def create_replay_memory_dataset() -> None:
    # define replay memory database creation parameters
    num_of_games: int = 1000
    replay_memory_dir: str = 'ML_replay_memories'
    replay_memory_filename: str = 'test_replay_memory.txt'
    bot_1_behaviour = RandBot(5234243)
    bot_2_behaviour = RandBot(54354)
    random_seed: int = 1
    delete_existing_older_dataset = True

    # check if needed to delete any older versions of the dataset
    replay_memory_file_path = os.path.join(replay_memory_dir, replay_memory_filename)
    if delete_existing_older_dataset and os.path.exists(replay_memory_file_path):
        print(f"An existing dataset was found at location '{replay_memory_file_path}', which will be deleted as selected.")
        os.remove(replay_memory_file_path)

    # in any case make sure the directory exists
    if not os.path.exists(replay_memory_dir):
        os.mkdir(replay_memory_dir)

    # create new replay memory dataset, according to the behaviour of the provided bots and the provided random seed
    engine = SchnapsenGamePlayEngine()
    replay_memory_recording_bot_1 = MLDataBot(bot_1_behaviour, replay_memory_file_path=replay_memory_file_path)
    replay_memory_recording_bot_2 = MLDataBot(bot_2_behaviour, replay_memory_file_path=replay_memory_file_path)
    for i in range(num_of_games):
        engine.play_game(replay_memory_recording_bot_1, replay_memory_recording_bot_2, random.Random(random_seed))
    print(f"Replay memory dataset recorder for {num_of_games} games.\nDataset is stored at: {replay_memory_file_path}")


@ml.command()
def train_model() -> None:
    replay_memory_filename = 'test_replay_memory.txt'
    replay_memories_directory = 'ML_replay_memories'
    model_name = 'test_model'
    model_dir = "ML_models"
    overwrite = False

    train_ML_model(replay_memory_filename=replay_memory_filename, replay_memories_directory=replay_memories_directory,
                   model_name=model_name, model_dir=model_dir, overwrite=overwrite)


@ml.command()
def try_bot_game() -> None:
    engine = SchnapsenGamePlayEngine()
    bot1 = MLPlayingBot(model_name='test_model', model_dir="ML_models")
    bot2 = RandBot(464566)
    winner, points, score = engine.play_game(bot1, bot2, random.Random(1))
    print(f"Winner is: {winner}, with {points} points!")


@main.command()
def game_24() -> None:
    engine = TwentyFourSchnapsenGamePlayEngine()
    bot1 = RandBot(12112121)
    bot2 = RandBot(464566)
    for i in range(1000):
        winner_id, game_points, score = engine.play_game(bot1, bot2, random.Random(i))
        print(f"Game ended. Winner is {winner_id} with {game_points} points, score {score}")


@main.command()
def rdeep_game() -> None:
    bot1: Bot
    bot2: Bot
    engine = SchnapsenGamePlayEngine()
    rdeep = bot1 = RdeepBot(num_samples=16, depth=4, rand=random.Random(4564654644))
    bot2 = RandBot(464566)
    wins = 0
    amount = 101
    for i in range(amount):
        if i % 2 == 0:
            bot1, bot2 = bot2, bot1
        winner_id, _, _ = engine.play_game(bot1, bot2, random.Random(5))
        if winner_id == rdeep:
            wins += 1
        if i > 0 and i % 10 == 0:
            print(f"won {wins} out of {i}")


@main.command()
def try_example_bot_game() -> None:
    engine = SchnapsenGamePlayEngine()
    bot1 = ExampleBot()
    bot2 = RandBot(464566)
    winner, points, score = engine.play_game(bot1, bot2, random.Random(1))
    print(f"Winner is: {winner}, with {points} points!")


if __name__ == "__main__":
    main()

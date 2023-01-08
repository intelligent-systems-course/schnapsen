import importlib
import click
import schnapsen.game
import schnapsen.twenty_four_card_schnapsen
import random
from typing import Optional


@click.group()
def main() -> None:
    """The main entry point."""


# @main.group()
# def fuzzers():
#     "Commands for fuzzing stuff"


@main.command()
@click.option("--module-name", default=".")
def load_schnapsen_bot(module_name: str) -> None:
    import sys
    # Adding the empty directory -- seems to be the cwd to the path.
    # This makes it possible to load bots which are in suer defined modules
    sys.path.insert(0, "")
    # importing the module also registers it with the BOT_REGISTRY
    importlib.import_module(name=module_name)
    # taking the entry back out of the path. Not sure what that will do...
    sys.path.pop(0)


class RandBot(schnapsen.game.Bot):
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.rng = random.Random(self.seed)

    def get_move(self, state: schnapsen.game.PlayerGameState, leader_move: Optional[schnapsen.game.PartialTrick]) -> schnapsen.game.Move:
        moves = state.valid_moves()
        move = self.rng.choice(list(moves))
        return move

    def notify_game_end(self, won: bool, state: schnapsen.game.PlayerGameState) -> None:
        history = state.get_game_history()
        print(f'result {"win" if won else "lost"}')
        print(history)

    def notify_trump_exchange(self, move: schnapsen.game.Trump_Exchange) -> None:
        print(f"That trump exchanged! {move.jack}")

    def __repr__(self) -> str:
        return f"RandBot(seed={self.seed})"


@main.command()
def try_game() -> None:
    engine = schnapsen.game.SchnapsenGamePlayEngine()
    bot1 = RandBot(12112121)
    bot2 = RandBot(464566)
    for i in range(1000):
        engine.play_game(bot1, bot2, random.Random(i))


@main.command()
def try_24_game() -> None:
    engine = schnapsen.twenty_four_card_schnapsen.TwentyFourSchnapsenGamePlayEngine()
    bot1 = RandBot(12112121)
    bot2 = RandBot(464566)
    for i in range(1000):
        engine.play_game(bot1, bot2, random.Random(i))


class HistoryBot(schnapsen.game.Bot):
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.rng = random.Random(self.seed)

    def get_move(self, state: schnapsen.game.PlayerGameState, leader_move: Optional[schnapsen.game.PartialTrick]) -> schnapsen.game.Move:
        history = state.get_game_history()
        print(history)

        moves = state.valid_moves()
        move = self.rng.choice(list(moves))
        return move

    def __repr__(self) -> str:
        return f"HistoryBot(seed={self.seed})"


@main.command()
def try_history() -> None:
    engine = schnapsen.game.SchnapsenGamePlayEngine()
    bot1 = HistoryBot(12112121)
    bot2 = HistoryBot(464566)
    engine.play_game(bot1, bot2, random.Random(1))

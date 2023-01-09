import random
from typing import Optional

import click

from schnapsen.game import (Bot, Move, PlayerPerspective,
                            SchnapsenGamePlayEngine, Trump_Exchange)
from schnapsen.twenty_four_card_schnapsen import \
    TwentyFourSchnapsenGamePlayEngine


@click.group()
def main() -> None:
    """Various Schnapsen Game Examples"""


class RandBot(Bot):
    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.rng = random.Random(self.seed)

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves = state.valid_moves()
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

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        moves = state.valid_moves()
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
    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        history = state.get_game_history()
        print(f'the initial state of this game was {history[0][0]}')
        moves = state.valid_moves()
        return moves[0]


@main.command()
def history_game() -> None:
    engine = SchnapsenGamePlayEngine()
    bot1 = HistoryBot()
    bot2 = HistoryBot()
    engine.play_game(bot1, bot2, random.Random(1))


@main.command()
def game_24() -> None:
    engine = TwentyFourSchnapsenGamePlayEngine()
    bot1 = RandBot(12112121)
    bot2 = RandBot(464566)
    for i in range(1000):
        winner_id, game_points, score = engine.play_game(bot1, bot2, random.Random(i))
        print(f"Game ended. Winner is {winner_id} with {game_points} points, score {score}")


if __name__ == "__main__":
    main()

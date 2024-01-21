import math
import random
from typing import Optional
from schnapsen.game import Bot, PlayerPerspective, Move, RegularMove


class BullyBot(Bot):
    """This bot plays plays as follows (deterministically using the random number generator provided).
        The bully bot only plays valid moves.
        If the bot has cards of the trump suit, it plays one of them at random
        Else, if the bot is follower and has cards of the same suit as the opponent, play one of these at random.
        Else, randomly play one of its cards with the highest score
    Args:
        rand (random.Random): The random number generator used to make the random choice of cards
        name (Optional[str]): The optional name of this bot
    """

    def __init__(self, rand: random.Random, name: Optional[str] = None) -> None:
        super().__init__(name)
        self.rng = rand

    def get_move(
        self,
        perspective: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:

        valid_regular_moves: list[RegularMove] = [move.as_regular_move() for move in perspective.valid_moves() if move.is_regular_move()]

        # If the bot has cards of the trump suit, it plays one of them at random
        trump_suit = perspective.get_trump_suit()
        trumps: list[RegularMove] = [move for move in valid_regular_moves if move.card.suit == trump_suit]
        if trumps:
            return self.rng.choice(trumps)

        # Else, if the bot is follower and has cards of the same suit as the opponent, play one of these at random.
        if leader_move is not None:
            leader_suit = leader_move.cards[0].suit
            same_suit_moves = [move for move in valid_regular_moves if move.card.suit == leader_suit]
            if same_suit_moves:
                return self.rng.choice(same_suit_moves)

        # Else, randomly play one of its cards with the highest score
        scorer = perspective.get_engine().trick_scorer

        highest_score_till_now = -math.inf
        highest_moves_till_now = []
        for move in valid_regular_moves:
            score = scorer.rank_to_points(move.card.rank)
            if score > highest_score_till_now:
                highest_score_till_now = score
                highest_moves_till_now = [move]
            elif score == highest_score_till_now:
                highest_moves_till_now.append(move)
            else:
                pass  # not scoring higher, so ignored
        return self.rng.choice(highest_moves_till_now)

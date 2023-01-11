from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer, Score
from schnapsen.deck import Suit, Card, Rank
from typing import Optional


class ExampleBot(Bot):
    """
    This Bot is here to serve as an example of the different methods the PlayerPerspective provides.
    In the end it is just playing the first valid move.
    """

    def get_move(self, state: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        # You can get information on the state from your perspective
        print(state.am_i_leader())
        print(state.get_my_score())
        print(state.get_opponent_won_cards())
        # more methods in the documentation

        # Get valid moves
        moves: list[Move] = state.valid_moves()
        one_move: Move = moves[0]
        # You can ask a move whether it is a marriage or a trum exchange
        print(one_move.is_marriage())
        print(one_move.is_trump_exchange())

        # we can get our current score
        my_score: Score = state.get_my_score()
        # A score has both direct and pending points
        print(f"I have {my_score.direct_points} direct points and {my_score.pending_points} pending points.")

        if leader_move is not None:
            if leader_move.cards[0].suit == state.get_trump_suit():
                print("The opponent played a card of the trump suit")

        # Check the cards in the moves
        if one_move.is_marriage():
            marriage = one_move
            queen: Card = marriage.cards[0]
            king: Card = marriage.cards[1]
            print(king)
            print(queen)
            # Find the suits and ranks of cards
            print(king.suit)
            print(queen.rank)
            if queen.suit == Suit.DIAMONDS:
                print("The opponent played a diamond marriage")
        elif one_move.is_trump_exchange():
            exchange = one_move
            jack: Card = exchange.cards[0]
            assert jack.rank == Rank.JACK
        else:
            normal_move = one_move
            card: Card = normal_move.cards[0]
            print(card.suit)
            print(card.rank)
            scorer = SchnapsenTrickScorer()
            points: int = scorer.rank_to_points(card.rank)
            print(points)
        return one_move

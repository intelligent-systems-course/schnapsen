from schnapsen.game import Bot, PlayerPerspective, Move, SchnapsenTrickScorer
from schnapsen.deck import Suit, Card, Rank
from typing import Optional


class ExampleBot(Bot):
    def get_move(self, state: 'PlayerPerspective', leader_move: Optional['Move']) -> 'Move':
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

        # Check the cards in the moves
        if one_move.is_marriage():
            marriage = one_move
            queen = marriage.cards[0]
            king = marriage.cards[1]
        elif one_move.is_trump_exchange():
            exchange = one_move
            jack = exchange.cards[0]
        else:
            normal_move = one_move
            card: Card = normal_move.cards[0]
            print(card.suit)
            print(card.rank)
            scorer = SchnapsenTrickScorer()
            points = scorer.rank_to_points(card.rank)
            print(points)
        return one_move

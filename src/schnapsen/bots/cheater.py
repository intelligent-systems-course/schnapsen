from typing import Optional, cast
from schnapsen.game import Bot, GameState, PlayerPerspective, Move


class CheaterBot(Bot):

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        state: GameState = cast(GameState, perspective._LeaderPerspective__game_state)  # type: ignore
        trump_suit = perspective.get_trump_suit()

        talon = state.talon.copy()
        if len(talon) > 0:
            try_to_win = True
            card_for_winner = next(iter(talon.draw_cards(1)))
            card_for_loser = next(iter(talon.draw_cards(1)))

            ranker = perspective.get_engine().trick_scorer.rank_to_points
            

            if card_for_loser.suit == trump_suit:
                if card_for_winner.suit == trump_suit:
                    if ranker(card_for_loser.rank) > ranker(card_for_winner.rank):
                        try_to_win = False
                else:
                    try_to_win = False


            my_trump_moves = [move for move in perspective.valid_moves() if move.is_regular_move() and move.cards[0].suit == trump_suit]

            if leader_move is None:
                opponent_hand = state.follower.hand
                # look at cards

                
            # have a look at the talon

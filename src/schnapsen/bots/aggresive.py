from schnapsen.game import Bot, Move, PlayerPerspective
from schnapsen.game import SchnapsenTrickScorer
from schnapsen.deck import Card, Suit, Rank


class RiskTakingBot(Bot):
    def get_move(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        Schnapsen bot, with a risk taking strategy.
        Playing the high cards first in order to win the game as quick as possible.
        """

        if self.condition1(perspective, leader_move):
            return self.action1(perspective, leader_move)
        elif self.condition2(perspective, leader_move):
            if self.condition3(perspective, leader_move):
                return self.action2(perspective, leader_move)
            else:
                return self.action3(perspective, leader_move)
        else:
            return self.action4(perspective, leader_move)
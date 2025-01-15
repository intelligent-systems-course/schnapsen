from schnapsen.game import Bot, Move, PlayerPerspective
from schnapsen.game import SchnapsenTrickScorer
from schnapsen.deck import Card, Suit, Rank


class AssignmentBot(Bot):
    def get_move(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """Get the move for the Bot.
        The basic structure for your bot is already implemented and must not be modified.
        To implement your bot, only modify the condition and action methods below.
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
from schnapsen.game import Bot, Move, PlayerPerspective
from schnapsen.game import SchnapsenTrickScorer
from schnapsen.deck import Card, Suit, Rank

class IS_project_bot(Bot):
    """
    This is our own bot, created with human strategies.
    In order to make the bot easier to understand and less complicated to build up,
    we are going to use different functions through the whole class
    """

    def get_move(self, perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        This is the basic strategy for every move that the bot is going to use.
        In order to make it easier, we are going to use condition and actions functions
        """
        if leader_move:
            if self.condition1(perspective, leader_move):
                self.action1(perspective, leader_move)
            if self.condition2(perspective, leader_move):
                return self.action2(perspective, leader_move)
            else:
                return self.action3(perspective, leader_move)
            
        if not leader_move:
            if self.condition3(perspective, leader_move):
                return self.action4(perspective, leader_move)
            else:
                if self.condition4(perspective, leader_move):
                    return self.action3(perspective, leader_move)
                else:
                    if self.condition5(perspective, leader_move):
                        return self.action5(perspective, leader_move)
                    else:
                        return self.action3(perspective, leader_move)
    

    def condition1(perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """
        Checks if there is a trump jack in our hand, that can be swapped for more powerful trump card
        """
        raise NotImplementedError("Not yet implemented")

    def action1(perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        Swaps the trump card
        """
        raise NotImplementedError("Not yet implemented")

    def condition2(perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """
        Checks if there is a marriage in our hand
        """
        raise NotImplementedError("Not yet implemented")

    def action2(perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        Plays the marriage in our hand. (If there are 2 or even 3 marriages, always prioritize the trump marriage, if there we have one)
        """
        raise NotImplementedError("Not yet implemented")
    
    def action3(perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        Plays the card with the lowest points, which is not a trump card!
        """
        raise NotImplementedError("Not yet implemented")

    def condition3(perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """
        Checks if there there is a higher points card from the same suit in our hand, than the one that has been played by the bot
        """
        raise NotImplementedError("Not yet implemented")
    
    def action4(perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        plays the highest possible card from the same suit, so we can take the hand with it
        """
        raise NotImplementedError("Not yet implemented")

    def condition4(perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """
        Checks if the played card from the opponent was king, queen or jack 
        """
        raise NotImplementedError("Not yet implemented")

    def condition5(perspective: PlayerPerspective, leader_move: Move | None) -> bool:
        """
        Checks if there is a trump card in our deck
        """
        raise NotImplementedError("Not yet implemented")

    def action5(perspective: PlayerPerspective, leader_move: Move | None) -> Move:
        """
        Plays the lowest trump card from our hand
        """
        raise NotImplementedError("Not yet implemented")
    
    def _card_points(self, card: Card) -> int:
            """
            Calculate points for a card.
            It is going to be used for the basic strategy,
            so the bot can choose the most valuable card possible.
            """
            if card.rank == Rank.ACE:
                return 11
            elif card.rank == Rank.TEN:
                return 10
            elif card.rank == Rank.KING:
                return 4
            elif card.rank == Rank.QUEEN:
                return 3
            elif card.rank == Rank.JACK:
                return 2
            else:
                return 0
            
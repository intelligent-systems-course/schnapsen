"""Two stage bot"""
from typing import Optional
from schnapsen.game import (
    Bot,
    Move,
    PlayerPerspective,
    GamePhase,
)


class TwoStageBot(Bot):
    """Bot which plays first the one, than the other startegy"""

    def __init__(self, bot1: Bot, bot2: Bot, name: Optional[str] = None) -> None:
        super().__init__(name)
        self.bot_phase1: Bot = bot1
        self.bot_phase2: Bot = bot2

    def get_move(
        self, perspective: PlayerPerspective, leader_move: Optional[Move]
    ) -> Move:
        if perspective.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(perspective, leader_move)
        else:
            raise AssertionError("Phase ain't right.")

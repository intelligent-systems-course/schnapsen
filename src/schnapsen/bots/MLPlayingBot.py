from src.schnapsen.game import Bot, PlayerGameState, PartialTrick, Move
from src.schnapsen.bots.MLBaseBot import MLBaseBot
from typing import Optional


class MLPlayingBot(MLBaseBot):
    def __init__(self) -> None:
        super().__init__()
        # load model

    def get_move(self, state: 'PlayerGameState', leader_move: Optional[PartialTrick]) -> 'Move':
        # apply model
        return super().get_move(state, leader_move)
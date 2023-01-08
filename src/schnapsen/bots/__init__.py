"""Create a bot in a separate .py and import them here, so that one can simply import
it by from schnapsen.bots import MyBot.
"""
from .rand import RandBot
from .minimax import MiniMaxBot
from .alphabeta import AlphaBetaBot

__all__ = ["RandBot", "MiniMaxBot", "AlphaBetaBot"]

"""
This package provides the GUI. It is implemented as a special bot, the GUIBot.
This bot, when requested to make a move, makes sure the perspective gets rendered in the browser and then waits for a move to be played on the GUI.
That move gets captured and returned as the move of the bot.

This design allows using the GUIBot to be used as any normal schnapsen Bot.
"""
from .guibot import SchnapsenServer


__all__ = ["SchnapsenServer"]

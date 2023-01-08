"""Create a bot in a separate .py and import them here, so that one can simply import
it by from schnapsen.bots import MyBot.
"""
from .guibot import SchnapsenServer


__all__ = ["SchnapsenServer"]

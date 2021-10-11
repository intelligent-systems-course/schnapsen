from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import inspect
from typing import Dict, Iterable, List, Optional, Type
import functools


# experimenting with a decorator for registering bots



@dataclass
class _BotEntry:
    bot_class: Type
    bot_name: str


class _BotRegistry:
    def __init__(self) -> None:
        self.register: Dict[str, _BotEntry] = {}

    def register_bot(self, bot_id: str, bot_class: Type, bot_name=None):
        assert bot_id not in self.register, "A bot with this id already exists"
        self.register[bot_id] = _BotEntry(bot_class, bot_name)


BOT_REGISTRY = _BotRegistry()


# Arguments can be added as keyword arguments
def Bot(_bot_class: Type = None, *, bot_name: str = None, bot_id: str = None):
    print(f"the Bot with name '{bot_name}' has now been registered")

    def decorator_name(bot_class):
        # register the bot
        # This is needed to access the variable in the outer scope.
        # MC: I am uncertain why this is not needed for the bot_id
        nonlocal bot_name
        if bot_name is None:
            bot_name = bot_class.__name__
        BOT_REGISTRY.register_bot(bot_id=bot_id, bot_class=bot_class, bot_name=bot_name)
        # TODO do some sanity checks on the bot:
        # This is indeed inspect.isfucntion and not inspect.ismethod. Presumably because this is the class and not an object of the class.
        methods = inspect.getmembers(bot_class, predicate=inspect.isfunction)
        if "get_move" not in {method[0] for method in methods}:
            raise Exception(f"get_move() method not found on bot {bot_name} with id {id}")
        get_move_params = inspect.signature(bot_class.get_move).parameters
        # TODO check parameters
        if not len(get_move_params) == 2:
            raise Exception("get_move must accept two parameters, self, and the game state")

        @functools.wraps(bot_class)
        def wrapper_name(*args, **kwargs):
            # Do something before using arg_1, ...
            value = bot_class(*args, **kwargs)
            # Do something after using arg_1, ...
            return value
        return wrapper_name
    if _bot_class is None:
        return decorator_name
    else:
        return decorator_name(_bot_class)

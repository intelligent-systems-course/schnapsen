from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import inspect
from typing import Dict, Iterable, List, Type
import functools


class Suit(Enum):
    HEARTS = auto()
    CLUBS = auto()
    SPADES = auto()
    DIAMONDS = auto()

# TODO these are now all cards, so we can esily extend the game.


class Rank(Enum):
    ACE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()


class Card(Enum):
    ACE_HEARTS = (Rank.ACE, Suit.HEARTS, "🂱")
    TWO_HEARTS = (Rank.TWO, Suit.HEARTS, "🂲")
    THREE_HEARTS = (Rank.THREE, Suit.HEARTS, "🂳")
    FOUR_HEARTS = (Rank.FOUR, Suit.HEARTS, "🂴")
    FIVE_HEARTS = (Rank.FIVE, Suit.HEARTS, "🂵")
    SIX_HEARTS = (Rank.SIX, Suit.HEARTS, "🂶")
    SEVEN_HEARTS = (Rank.SEVEN, Suit.HEARTS, "🂷")
    EIGHT_HEARTS = (Rank.EIGHT, Suit.HEARTS, "🂸")
    NINE_HEARTS = (Rank.NINE, Suit.HEARTS, "🂹")
    TEN_HEARTS = (Rank.TEN, Suit.HEARTS, "🂺")
    JACK_HEARTS = (Rank.JACK, Suit.HEARTS, "🂻")
    QUEEN_HEARTS = (Rank.QUEEN, Suit.HEARTS, "🂽")
    KING_HEARTS = (Rank.KING, Suit.HEARTS, "🂾")

    ACE_CLUBS = (Rank.ACE, Suit.CLUBS, "🃑")
    TWO_CLUBS = (Rank.TWO, Suit.CLUBS, "🃒")
    THREE_CLUBS = (Rank.THREE, Suit.CLUBS, "🃓")
    FOUR_CLUBS = (Rank.FOUR, Suit.CLUBS, "🃔")
    FIVE_CLUBS = (Rank.FIVE, Suit.CLUBS, "🃕")
    SIX_CLUBS = (Rank.SIX, Suit.CLUBS, "🃖")
    SEVEN_CLUBS = (Rank.SEVEN, Suit.CLUBS, "🃗")
    EIGHT_CLUBS = (Rank.EIGHT, Suit.CLUBS, "🃘")
    NINE_CLUBS = (Rank.NINE, Suit.CLUBS, "🃙")
    TEN_CLUBS = (Rank.TEN, Suit.CLUBS, "🃚")
    JACK_CLUBS = (Rank.JACK, Suit.CLUBS, "🃛")
    QUEEN_CLUBS = (Rank.QUEEN, Suit.CLUBS, "🃝")
    KING_CLUBS = (Rank.KING, Suit.CLUBS, "🃞")

    ACE_SPADES = (Rank.ACE, Suit.SPADES, "🂡")
    TWO_SPADES = (Rank.TWO, Suit.SPADES, "🂢")
    THREE_SPADES = (Rank.THREE, Suit.SPADES, "🂣")
    FOUR_SPADES = (Rank.FOUR, Suit.SPADES, "🂤")
    FIVE_SPADES = (Rank.FIVE, Suit.SPADES, "🂥")
    SIX_SPADES = (Rank.SIX, Suit.SPADES, "🂦")
    SEVEN_SPADES = (Rank.SEVEN, Suit.SPADES, "🂧")
    EIGHT_SPADES = (Rank.EIGHT, Suit.SPADES, "🂨")
    NINE_SPADES = (Rank.NINE, Suit.SPADES, "🂩")
    TEN_SPADES = (Rank.TEN, Suit.SPADES, "🂪")
    JACK_SPADES = (Rank.JACK, Suit.SPADES, "🂫")
    QUEEN_SPADES = (Rank.QUEEN, Suit.SPADES, "🂭")
    KING_SPADES = (Rank.KING, Suit.SPADES, "🂮")

    ACE_DIAMONDS = (Rank.ACE, Suit.DIAMONDS, "🃁")
    TWO_DIAMONDS = (Rank.TWO, Suit.DIAMONDS, "🃂")
    THREE_DIAMONDS = (Rank.THREE, Suit.DIAMONDS, "🃃")
    FOUR_DIAMONDS = (Rank.FOUR, Suit.DIAMONDS, "🃄")
    FIVE_DIAMONDS = (Rank.FIVE, Suit.DIAMONDS, "🃅")
    SIX_DIAMONDS = (Rank.SIX, Suit.DIAMONDS, "🃆")
    SEVEN_DIAMONDS = (Rank.SEVEN, Suit.DIAMONDS, "🃇")
    EIGHT_DIAMONDS = (Rank.EIGHT, Suit.DIAMONDS, "🃈")
    NINE_DIAMONDS = (Rank.NINE, Suit.DIAMONDS, "🃉")
    TEN_DIAMONDS = (Rank.TEN, Suit.DIAMONDS, "🃊")
    JACK_DIAMONDS = (Rank.JACK, Suit.DIAMONDS, "🃋")
    QUEEN_DIAMONDS = (Rank.QUEEN, Suit.DIAMONDS, "🃍")
    KING_DIAMONDS = (Rank.KING, Suit.DIAMONDS, "🃎")

    def is_suit(self, suit: Suit):
        return self.value[1] == suit

    def is_rank(self, rank: Rank):
        return self.value[0] == rank

    @staticmethod
    def get_card(rank: Rank, suit: Suit):
        for card in Card:
            (card_rank, card_suit, _) = card.value
            if rank == card_rank and suit == card_suit:
                return card
        raise Exception(f"This card does not exist: {card_rank}, {card_suit}. This should be impossible as all combinations are defined")


class CardCollection(ABC):

    @abstractmethod
    def get_cards(self) -> Iterable[Card]:
        pass

    def filter(self, suit: Suit) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided suit"""
        results: List[Card] = list(filter(lambda x: x.is_suit(suit), self.get_cards()))
        return results


class OrderedCardCollection(CardCollection):
    def __init__(self) -> None:
        self._cards: List[Card] = []

    def get_cards(self) -> Iterable[Card]:
        return self._cards


class Hand (CardCollection):
    def __init__(self) -> None:
        pass


class Talon (CardCollection):
    pass


class PartialTrick:
    pass

# TODO: this used to have a better name, but I forgot


class Trick(PartialTrick):
    pass


class Score:
    pass


class TrickScorer:
    @abstractmethod
    def score(self, trick: Trick) -> Score:
        pass


@dataclass
class GameState:
    hand1: Hand
    hand2: Hand
    trump: Card
    talon: Talon

    play: PartialTrick


class PlayerGameState:
    player_hand: Hand
    opponent_hand: Hand
    on_table: PartialTrick
    trump: Card
    talon: Talon


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

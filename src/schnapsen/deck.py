"""
In this module you will find the definition of deck elements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
import enum
from typing import Any, Iterable, Iterator, Optional
import itertools


class Suit(Enum):
    """
    Class used for classification of card suits.
    """

    HEARTS = auto()
    CLUBS = auto()
    SPADES = auto()
    DIAMONDS = auto()

    def __str__(self) -> str:
        """
        __str__ method, returns the name of the suit as a string (eg. str(Suit.HEARTS) -> "HEARTS")

        :return: (str): The name of the suit as a string.
        """
        return self.name


class Rank(Enum):
    """
    Class defining the card ranks.
    """

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

    def __str__(self) -> str:
        """
        __str__ method, returns the name of the rank as a string (eg. str(Rank.ACE) -> "ACE")

        :return: (str): The name of the rank as a string.
        """
        return self.name


@enum.unique
class Card(Enum):
    """
     Class defining individual cards.

    :param rank (Rank): The rank of the card.
    :param suit (Suit): The suit of the card.
    :param character (str): The character representation of the card.
    :attr rank (Rank): The rank of the card.
    :attr suit (Suit): The suit of the card.
    :attr character (str): The character representation of the card.
    """

    # Each possible card is definied below as a tuple of (rank, suit, character)
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

    def __init__(self, rank: Rank, suit: Suit, character: str) -> None:
        self.rank = rank
        self.suit = suit
        self.character = character

    @staticmethod
    def _get_card(rank: Rank, suit: Suit) -> Card:
        """
        Returns a card object with the provided rank and suit.

        :param rank: (Rank): The rank of the card.
        :param suit: (Suit): The suit of the card.
        :return: (Card): A card object.
        """

        for card in Card:
            (card_rank, card_suit, _) = card.value
            if rank == card_rank and suit == card_suit:
                return card
        raise Exception(f"This card does not exist: {card_rank}, {card_suit}. This should be impossible as all combinations are defined")

    @staticmethod
    def get_card(rank: Rank, suit: Suit) -> Card:
        """
        Get a Card for the provided Rank and Suit.

        Internally, this uses a cache for effieciency and to prevent duplicate card objects.

        :param rank: (Rank): The rank of the card.
        :param suit: (Suit): The suit of the card.
        :return: (Card): The desired Card
        """

        # _CardCache._CARD_CACHE is a dict with tuples of (rank, suit) as keys and card objects as values.
        return _CardCache._CARD_CACHE[(rank, suit)]

    def __repr__(self) -> str:
        """
        Str method for the card class.

        :return: (str): The string representation of the card.
        """

        return f"Card.{self.name}"


class _CardCache:
    """
    Card cache class. This class is used to cache all possible cards in the game as a dict.

    This class is private to this module. It is supposed to be only used internally and might change.
    """

    _CARD_CACHE: dict[tuple[Rank, Suit], Card] = {(card_rank, card_suit): Card._get_card(card_rank, card_suit) for (card_rank, card_suit) in itertools.product(Rank, Suit)}


class CardCollection(ABC):
    """A collection of cards for which the order is not significant and not guaranteed."""

    @abstractmethod
    def get_cards(self) -> Iterable[Card]:
        """
        Get an Iterable of the cards in this collection. Changes to this Iterable will not be reflected in this Collection.
        """
        raise NotImplementedError()

    def filter_suit(self, suit: Suit) -> list[Card]:
        """
        Returns a list with in it all cards which have the provided suit

        :param suit: (Suit): The suit to filter on.
        :return: (list[Card]): A list of cards with the provided suit.
        """

        results: list[Card] = list(filter(lambda x: x.suit is suit, self.get_cards()))
        return results

    def filter_rank(self, rank: Rank) -> list[Card]:
        """
        Returns a list with in it all cards which have the provided rank

        :param rank: (Rank): The rank to filter on.
        :return: (list[Card]): A list of cards with the provided rank.
        """

        results: list[Card] = list(filter(lambda x: x.rank is rank, self.get_cards()))
        return results

    @abstractmethod
    def is_empty(self) -> bool:
        """
        True in case this CardCollection does not contain any Cards. False otherwise.
        """
        pass

    def __len__(self) -> int:
        """
        Returns the number of cards in this collection.

        :return: (int): The number of cards in this collection.
        """

        return sum(1 for _ in self.get_cards())

    def __iter__(self) -> Iterator[Card]:
        """
        Returns an iterator over the cards in this collection.

        :return: (Iterator[Card]): An iterator over the cards in this collection.
        """

        return self.get_cards().__iter__()

    def __contains__(self, item: Any) -> bool:
        """
        Returns whether the provided item is in this collection.

        :param item: (Any): The item to check.
        :return: (bool): Whether the item is in this collection.
        """

        assert isinstance(item, Card), "Only cards can be contained in a card collection"
        return item in self.get_cards()


class OrderedCardCollection(CardCollection):
    """
    A collection of cards for which the order is significant and guaranteed

    :param cards: (Optional[Iterable[Card]]): An Iterable of cards to initialize the collection with. Defaults to None.
    """

    def __init__(self, cards: Optional[Iterable[Card]] = None) -> None:
        self._cards: list[Card] = list(cards or [])

    def is_empty(self) -> bool:
        """
        Returns True if this collection is empty, False otherwise.

        :return: (bool): Whether this collection is empty.
        """

        return len(self._cards) == 0

    def get_cards(self) -> list[Card]:
        """
        Returns a defensive copy of the cards in this collection.

        :return: (list[Card]): list of cards in this collection.
        """

        return list(self._cards)

    def __len__(self) -> int:
        """
        Returns the number of cards in this collection.

        :return: (int): The number of cards in this collection.
        """
        return len(self._cards)

    def __iter__(self) -> Iterator[Card]:
        """
        Returns an iterator over the cards in this collection.

        :return: (Iterator[Card]): An iterator over the cards in this collection.
        """
        return self._cards.__iter__()

    def __contains__(self, item: Any) -> bool:
        """
        Returns whether the provided item is in this collection.

        :param item: (Any): The item to check.
        :return: (bool): Whether the item is in this collection.
        """

        assert isinstance(item, Card), "Only cards can be contained in a card collection"
        return item in self._cards

    def filter_suit(self, suit: Suit) -> list[Card]:
        """
        Returns an Iterable with in it all cards which have the provided suit

        :param suit: (Suit): The suit to filter on.
        :return: (list[Card]): An Iterable of cards with the provided suit.
        """

        assert suit in Suit
        results: list[Card] = [card for card in self._cards if card.suit is suit]
        return results

    def filter_rank(self, rank: Rank) -> list[Card]:
        """
        Returns an Iterable with in it all cards which have the provided rank

        :param rank: (Rank): The rank to filter on.
        :return: (list[Card]): An Iterable of cards with the provided rank.
        """
        assert rank in Rank
        results: list[Card] = [card for card in self._cards if card.rank is rank]
        return results

    def __repr__(self) -> str:
        """
        Returns a string representation of this collection.

        :return: (str): A string representation of this collection.
        """

        return f"OrderedCardCollection(cards={self._cards})"

from abc import ABC, abstractmethod
from enum import Enum, auto
import enum
from typing import Any, Iterable, Iterator, List, Optional
import itertools


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


@enum.unique
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

    def __init__(self, rank: Rank, suit: Suit, character: str) -> None:
        self.rank = rank
        self.suit = suit
        self.character = character

    @staticmethod
    def _get_card(rank: Rank, suit: Suit) -> 'Card':
        for card in Card:
            (card_rank, card_suit, _) = card.value
            if rank == card_rank and suit == card_suit:
                return card
        raise Exception(f"This card does not exist: {card_rank}, {card_suit}. This should be impossible as all combinations are defined")

    @staticmethod
    def get_card(rank: Rank, suit: Suit) -> 'Card':
        return _CardCache._CARD_CACHE[(rank, suit)]
#        return _CARD_CACHE[(rank, suit)]

    def __str__(self) -> str:
        return f"{self.rank.name} of {self.suit.name} ({self.value[2]} )"


class _CardCache:
    _CARD_CACHE = {(card_rank, card_suit): Card._get_card(card_rank, card_suit) for (card_rank, card_suit) in itertools.product(Rank, Suit)}


class CardCollection(ABC):

    @abstractmethod
    def get_cards(self) -> Iterable[Card]:
        """
        Get an Iterable of the cards in this collection. Changes to this Iterable will not be reflected in this Collection
        """
        raise NotImplementedError()

    def filter_suit(self, suit: Suit) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided suit"""
        results: List[Card] = list(filter(lambda x: x.suit is suit, self.get_cards()))
        return results

    def filter_rank(self, rank: Rank) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided rank"""
        results: List[Card] = list(filter(lambda x: x.rank is rank, self.get_cards()))
        return results

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    def __len__(self) -> int:
        return sum(1 for _ in self.get_cards())

    def __iter__(self) -> Iterator[Card]:
        return self.get_cards().__iter__()

    def __contains__(self, item: Any) -> bool:
        assert isinstance(item, Card), "Only cards can be contained in a card collection"
        return item in self.get_cards()


class OrderedCardCollection(CardCollection):
    def __init__(self, cards: Optional[Iterable[Card]] = None) -> None:
        """
        Create an ordered collection of cards. The cards are in the order as specified in the Iterable.
        By default the Collection is empty.
        This constructor will make a defensive copy of the argument.
        """
        self._cards: List[Card] = list(cards or [])

    def is_empty(self) -> bool:
        return len(self._cards) == 0

    def get_cards(self) -> Iterable[Card]:
        return list(self._cards)

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self) -> Iterator[Card]:
        return self._cards.__iter__()

    def __contains__(self, item: Any) -> bool:
        assert isinstance(item, Card), "Only cards can be contained in a card collection"
        return item in self._cards

    def filter_suit(self, suit: Suit) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided suit"""
        assert suit in Suit
        results = [card for card in self._cards if card.suit is suit]
        return results

    def filter_rank(self, rank: Rank) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided rank"""
        assert rank in Rank
        results = [card for card in self._cards if card.rank is rank]
        return results

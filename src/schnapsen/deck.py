from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Iterable, List, Optional
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

    # This is a bit of trickery to still allow these as direct members, rather than methods
    # we define suit and rank here, but tell the enum system to ignore them
    # we, however, dynamically serve them in __getattribute__ upoon request
    # it appears something similar should be possible using a __new__ method, but MC could nto figure this out yet.
    # https://docs.python.org/3/library/enum.html#when-to-use-new-vs-init
    _ignore_ = ["suit", "rank"]
    suit: Suit
    rank: Rank

    def __getattribute__(self, name: str) -> Any:
        if name == "suit":
            return self.value[1]
        elif name == "rank":
            return self.value[0]
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "suit" or name == "rank":
            raise AttributeError("suit and rank of a card cannot be changed")
        return super().__setattr__(name, value)

    @staticmethod
    def _get_card(rank: Rank, suit: Suit) -> 'Card':
        for card in Card:
            (card_rank, card_suit, _) = card.value
            if rank == card_rank and suit == card_suit:
                return card
        raise Exception(f"This card does not exist: {card_rank}, {card_suit}. This should be impossible as all combinations are defined")

    @staticmethod
    def get_card(rank: Rank, suit: Suit) -> 'Card':
        global _CARD_CACHE
        return _CARD_CACHE[(rank, suit)]

    def __str__(self) -> str:
        return f"{self.rank.name} of {self.suit.name} ({self.value[2]} )"


_CARD_CACHE = {(card_rank, card_suit): Card._get_card(card_rank, card_suit) for (card_rank, card_suit) in itertools.product(Rank, Suit)}


class CardCollection(ABC):

    @abstractmethod
    def get_cards(self) -> Iterable[Card]:
        """
        Get an Iterable of the cards in this collection. Changes to this Iterable will not be reflected in this Collection
        """
        raise NotImplementedError()

    def filter(self, suit: Suit) -> Iterable[Card]:
        """Returns an Iterable with in it all cards which have the provided suit"""
        results: List[Card] = list(filter(lambda x: x.suit is suit, self.get_cards()))
        return results


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


# TODO: some more thinking is needed for the class hierarchy for the different collections of cards

def get_schnapsen_deck() -> OrderedCardCollection:
    deck = OrderedCardCollection()
    for suit in Suit:
        for rank in [Rank.JACK, Rank.QUEEN, Rank.KING, Rank.TEN, Rank.ACE]:
            deck._cards.append(Card.get_card(rank, suit))
    return deck

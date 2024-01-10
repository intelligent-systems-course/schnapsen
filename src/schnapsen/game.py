"""
In this module you will find all parts related to playing a game of Schnapsen.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import contextlib
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO
from random import Random
import sys
from typing import Generator, Iterable, Optional, Union, cast, Any
from .deck import CardCollection, OrderedCardCollection, Card, Rank, Suit
import itertools


class Bot(ABC):
    """
    The Bot baseclass. Derive your own bots from this class and implement the get_move method to use it in games.
    Besides the get_move method, it is also possible to override notify_trump_exchange and notify_game_end to get notified when these events happen.

    :param name: (str): Optionally, specify a name for the bot. Defaults to None.
    """

    def __init__(self, name: Optional[str] = None) -> None:
        if name:
            self.__name = name

    @abstractmethod
    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """
        Get the move this Bot wants to play. This is the method that gets called by the engine to get the bot's next move.
        If this Bot is leading, the leader_move will be None. If this both is following, the leader_move will contain the move the opponent just played

        :param perspective: (PlayerPerspective): The PlayerPerspective which contains the information on the current state of the game from the perspective of this player
        :param leader_move: (Optional[Move]): The move made by the leader of the trick. This is None if this bot is the leader.
        """

    def notify_trump_exchange(self, move: TrumpExchange) -> None:
        """
        The engine will call this method when a trump exchange is made.
        Overide this method to get notified about trump exchanges. Note that this notification is sent to both bots.

        :param move: (TrumpExchange): the Trump Exchange move that was played.
        """

    def notify_game_end(self, won: bool, perspective: PlayerPerspective) -> None:
        """
        The engine will call this method when the game ends.
        Override this method to get notified about the end of the game.

        :param won: (bool): Did this bot win the game?
        :param perspective: (PlayerPerspective) The final perspective of the game.
        """

    def __str__(self) -> str:
        """
        A string representation of the Bot. If the bot was constructed with a name, it will be that name.
        Otherwise it will be the class name and the memory address of the bot.

        :returns: (str): A string representation of the bot.
        """
        return self.__name if hasattr(self, '_Bot__name') else super().__str__()


class Move(ABC):
    """
    A single move during a game. There are several types of move possible: normal moves, trump exchanges, and marriages.
    They are implmented in classes inheriting from this class.
    """

    cards: list[Card]  # implementation detail: The creation of this list is defered to the derived classes in _cards()
    """The cards played in this move"""

    def is_regular_move(self) -> bool:
        """
        Is this Move a regular move (not a mariage or trump exchange)

        :returns: a bool indicating whether this is a regular move
        """
        return False

    def as_regular_move(self) -> RegularMove:
        """Returns this same move but as a Marriage."""
        raise AssertionError("as_regular_move called on a Move which is not a regular move. Check with is_regular_move first.")

    def is_marriage(self) -> bool:
        """
        Is this Move a marriage?

        :returns: a bool indicating whether this move is a marriage
        """
        return False

    def as_marriage(self) -> Marriage:
        """Returns this same move but as a Marriage."""
        raise AssertionError("as_marriage called on a Move which is not a Marriage. Check with is_marriage first.")

    def is_trump_exchange(self) -> bool:
        """
        Is this Move a trump exchange move?

        :returns: a bool indicating whether this move is a trump exchange
        """
        return False

    def as_trump_exchange(self) -> TrumpExchange:
        """Returns this same move but as a TrumpExchange."""
        raise AssertionError("as_trump_exchange called on a Move which is not a TrumpExchange. Check with is_trump_exchange first.")

    def __getattribute__(self, __name: str) -> Any:
        if __name == "cards":
            # We call the method to compute the card list
            return object.__getattribute__(self, "_cards")()
        return object.__getattribute__(self, __name)

    @abstractmethod
    def _cards(self) -> list[Card]:
        """
        Get the list of cards in this move. This method should not be called direcly, use the cards property instead.
        Private abstract method for other classes to inherit and/or override.
        """

    @abstractmethod
    def __eq__(self, __o: object) -> bool:
        """
        Compares two moves with each other. Two moves are equal in case they are of the same type and if they contain the same cards.
        Abstract method for derived classes to override.
        """


@dataclass(frozen=True)
class RegularMove(Move):
    """A regular move in the game"""

    card: Card
    """The card which is played"""

    def _cards(self) -> list[Card]:
        return [self.card]

    @staticmethod
    def from_cards(cards: Iterable[Card]) -> list[Move]:
        """Create an iterable of Moves from an iterable of cards."""
        return [RegularMove(card) for card in cards]

    def is_regular_move(self) -> bool:
        return True

    def as_regular_move(self) -> RegularMove:
        return self

    def __repr__(self) -> str:
        return f"RegularMove(card={self.card})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, RegularMove):
            return False
        return self.card == __o.card


@dataclass(frozen=True)
class TrumpExchange(Move):
    """A move that implements the exchange of the trump card for a Jack of the same suit."""

    jack: Card
    """The Jack which will be placed at the bottom of the Talon"""

    def __post_init__(self) -> None:
        """
        Asserts that the card is a Jack
        """
        assert self.jack.rank is Rank.JACK, f"The rank card {self.jack} used to initialize the {TrumpExchange.__name__} was not Rank.JACK"

    def is_trump_exchange(self) -> bool:
        """
        Returns True if this is a trump exchange.
        """
        return True

    def as_trump_exchange(self) -> TrumpExchange:
        """
        Returns this same move but as a TrumpExchange.

        """
        return self

    def _cards(self) -> list[Card]:
        return [self.jack]

    def __repr__(self) -> str:
        return f"TrumpExchange(jack={self.jack})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, TrumpExchange):
            return False
        return self.jack == __o.jack


@dataclass(frozen=True)
class Marriage(Move):
    """
    A Move representing a marriage in the game. This move has two cards, a king and a queen of the same suit.
    Right after the marriage is played, the player must play either the queen or the king.
    Because it can only be beneficial to play the king, it is chosen automatically.
    This Regular move is part of this Move already and does not have to be played separatly.
    """

    queen_card: Card
    """The queen card of this marriage"""

    king_card: Card
    """The king card of this marriage"""

    suit: Suit = field(init=False, repr=False, hash=False)
    """The suit of this marriage, gets derived from the suit of the queen and king."""

    def __post_init__(self) -> None:
        """
        Ensures that the suits of the fields all have the same suit and are a king and a queen.
        Finally, sets the suit field.
        """
        assert self.queen_card.rank is Rank.QUEEN, f"The rank card {self.queen_card} used to initialize the {Marriage.__name__} was not Rank.QUEEN"
        assert self.king_card.rank is Rank.KING, f"The rank card {self.king_card} used to initialize the {Marriage.__name__} was not Rank.KING"
        assert self.queen_card.suit == self.king_card.suit, f"The cards used to inialize the Marriage {self.queen_card} and {self.king_card} so not have the same suit."
        object.__setattr__(self, "suit", self.queen_card.suit)

    def is_marriage(self) -> bool:
        return True

    def as_marriage(self) -> Marriage:
        return self

    def underlying_regular_move(self) -> RegularMove:
        """
        Get the regular move which was played because of the marriage. In this engine this is always the queen card.

        :returns: (RegularMove): The regular move which was played because of the marriage.
        """
        # this limits you to only have the queen to play after a marriage, while in general you would have a choice.
        # This is not an issue since playing the king give you the highest score.
        return RegularMove(self.king_card)

    def _cards(self) -> list[Card]:
        return [self.queen_card, self.king_card]

    def __repr__(self) -> str:
        return f"Marriage(queen_card={self.queen_card}, king_card={self.king_card})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Marriage):
            return False
        return self.queen_card == __o.queen_card and self.king_card == self.king_card


class Hand(CardCollection):
    """
    The cards in the hand of a player. These are the cards which the player can see and which he can play with in the turn.

    :param cards: (Iterable[Card]): The cards to be added to the hand
    :param max_size: (int): The maximum number of cards the hand can contain. If the number of cards goes beyond, an Exception is raised. Defaults to 5.

    :attr cards: The cards in the hand - initialized from the cards parameter.
    :attr max_size: The maximum number of cards the hand can contain - initialized from the max_size parameter.
    """

    def __init__(self, cards: Iterable[Card], max_size: int = 5) -> None:
        self.max_size = max_size
        cards = list(cards)
        assert len(cards) <= max_size, f"The number of cards {len(cards)} is larger than the maximum number fo allowed cards {max_size}"
        self.cards = cards

    def remove(self, card: Card) -> None:
        """
        Remove one occurence of the card from this hand

        :param card: (Card): The card to be removed from the hand.
        """
        try:
            self.cards.remove(card)
        except ValueError as ve:
            raise Exception(f"Trying to remove a card from the hand which is not in the hand. Hand is {self.cards}, trying to remove {card}") from ve

    def add(self, card: Card) -> None:
        """
        Add a card to the Hand

        :param card:  The card to be added to the hand
        """
        assert len(self.cards) < self.max_size, "Adding one more card to the hand will cause a hand with too many cards"
        self.cards.append(card)

    def has_cards(self, cards: Iterable[Card]) -> bool:
        """
        Are all the cards contained in this Hand?

        :param cards: An iterable of cards which need to be checked
        :returns: Whether all cards in the provided iterable are in this Hand
        """
        return all(card in self.cards for card in cards)

    def copy(self) -> Hand:
        """
        Create a deep copy of this Hand

        :returns: A deep copy of this hand. Changes to the original will not affect the copy and vice versa.
        """
        return Hand(list(self.cards), max_size=self.max_size)

    def is_empty(self) -> bool:
        """
        Is the Hand emoty?

        :returns: A bool indicating whether the hand is empty
        """
        return len(self.cards) == 0

    def get_cards(self) -> list[Card]:
        """
        Returns the cards in the hand

        :returns: (list[Card]): A defensive copy of the list of Cards in this Hand.
        """
        return list(self.cards)

    def filter_suit(self, suit: Suit) -> list[Card]:
        """
        Return a list of all cards in the hand which have the specified suit.

        :param suit: (Suit): The suit to filter on.
        :returns: (list(Card)): A list of cards which have the specified suit.
        """
        results: list[Card] = [card for card in self.cards if card.suit is suit]
        return results

    def filter_rank(self, rank: Rank) -> list[Card]:
        """
        Return a list of all cards in the hand which have the specified rank.

        :param suit: (Rank): The rank to filter on.
        :returns: (list(Card)): A list of cards which have the specified rank.
        """
        results: list[Card] = [card for card in self.cards if card.rank is rank]
        return results

    def __repr__(self) -> str:
        return f"Hand(cards={self.cards}, max_size={self.max_size})"


class Talon(OrderedCardCollection):
    """
    The Talon contains the cards which have not yet been given to the players.

    :param cards: The cards to be put on this talon, a defensive copy will be made.
    :param trump_suit: The trump suit of the Talon, important if there are no more cards to be taken.
    :attr _cards: The cards of the Talon (defined in super().__init__)
    :attr __trump_suit: The trump suit of the Talon.
    """

    def __init__(self, cards: Iterable[Card], trump_suit: Optional[Suit] = None) -> None:
        """
        The cards of the Talon. The last card of the iterable is the bottommost card.
        The first one is the top card (which will be taken when/if a card is drawn)
        The Trump card is at the bottom of the Talon.
        The trump_suit can also be specified explicitly, which is important when the Talon is empty.
        If the trump_suit is specified and there are cards, then the suit of the bottommost card must be the same.
        """
        if cards:
            trump_card_suit = list(cards)[-1].suit
            assert not trump_suit or trump_card_suit == trump_suit, "If the trump suit is specified, and there are cards on the talon, the suit must be the same!"
            self.__trump_suit = trump_card_suit
        else:
            assert trump_suit, f"If an empty {Talon.__name__} is created, the trump_suit must be specified"
            self.__trump_suit = trump_suit

        super().__init__(cards)

    def copy(self) -> Talon:
        """
        Create an independent copy of this talon.

        :returns: (Talon): A deep copy of this talon. Changes to the original will not affect the copy and vice versa.
        """
        # We do not need to make a copy of the cards as this happend in the constructor of Talon.
        return Talon(self._cards, self.__trump_suit)

    def trump_exchange(self, new_trump: Card) -> Card:
        """
        perfom a trump-jack exchange. The card to be put as the trump card must be a Jack of the same suit.
        As a result, this Talon changed: the old trump is removed and the new_trump is at the bottom of the Talon

        We also require that there must be two cards on the Talon, which is always the case in a normal game of Schnapsen

        :param new_trump: (Card):The card to be put. It must be a Jack of the same suit as the card at the bottom
        :returns: (Card): The card which was at the bottom of the Talon before the exchange.

        """
        assert new_trump.rank is Rank.JACK, f"the rank of the card used for the exchange {new_trump} is not a Rank.JACK"
        assert len(self._cards) >= 2, f"There must be at least two cards on the talon to do an exchange len = {len(self._cards)}"
        assert new_trump.suit is self._cards[-1].suit, f"The suit of the new card {new_trump} is not equal to the current bottom {self._cards[-1].suit}"
        old_trump = self._cards.pop(len(self._cards) - 1)
        self._cards.append(new_trump)
        return old_trump

    def draw_cards(self, amount: int) -> Iterable[Card]:
        """
        Draw a card from this Talon. This does not change the talon, btu rather returns a talon with the change applied and the card drawn

        param amount: (int): The number of cards to be drawn
        :returns: (Talon): A new Talon with the cards drawn and the trump_suit set to the same value as this Talon.
        """

        assert len(self._cards) >= amount, f"There are only {len(self._cards)} on the Talon, but {amount} cards are requested"
        draw = self._cards[:amount]
        self._cards = self._cards[amount:]
        return draw

    def trump_suit(self) -> Suit:
        """
        Return the suit of the trump card, i.e., the bottommost card.
        This still works, even when the Talon has become empty.

        :returns: (Suit): the trump suit of the Talon
        """
        return self.__trump_suit

    def trump_card(self) -> Optional[Card]:
        """
        Returns the current trump card, i.e., the bottommost card.
        Or None in case this Talon is empty

        :returns: (Card): The trump card, or None if the Talon is empty
        """
        if len(self._cards) > 0:
            return self._cards[-1]
        return None

    def __repr__(self) -> str:
        """
        A string representation of the Talon.

        :returns: (str): A string representation of the Talon.
        """
        return f"Talon(cards={self._cards}, trump_suit={self.__trump_suit})"


@dataclass(frozen=True)
class Trick(ABC):
    """
    A complete trick. This is, the move of the leader and if that was not an exchange, the move of the follower.
    """

    cards: Iterable[Card] = field(init=False, repr=False, hash=False)
    """All cards used as part of this trick. This includes cards used in marriages"""

    @abstractmethod
    def is_trump_exchange(self) -> bool:
        """
        Returns True if this is a trump exchange

        :returns: True in case this was a trump exchange
        """

    @abstractmethod
    def as_partial(self) -> PartialTrick:
        """
        Returns the first part of this trick. Raises an Exceptption if this is not a Trick with two parts

        :returns: The first part of this trick
        """

    def __getattribute__(self, __name: str) -> Any:
        if __name == "cards":
            # We call the method to compute the card list
            return object.__getattribute__(self, "_cards")()
        return object.__getattribute__(self, __name)

    @abstractmethod
    def _cards(self) -> Iterable[Card]:
        """
        Get all cards used in this tick. This method should not be called directly.
        Use the cards property instead.

        :returns: (Iterable[Card]): All cards used in this trick.
        """


@dataclass(frozen=True)
class ExchangeTrick(Trick):
    """
    A Trick in which the player does a trump exchange.
    """

    exchange: TrumpExchange
    """A trump exchange by the leading player"""

    trump_card: Card
    """The card at the bottom of the talon"""

    def is_trump_exchange(self) -> bool:
        """Returns True if this is a trump exchange"""
        return True

    def as_partial(self) -> PartialTrick:
        """ Returns the first part of this trick. Raises an Exceptption if this is not a Trick with two parts"""
        raise Exception("An Exchange Trick does not have a first part")

    def _cards(self) -> Iterable[Card]:
        """Get all cards used in this tick. This method should not be called directly."""
        exchange = self.exchange.cards
        exchange.append(self.trump_card)
        return exchange


@dataclass(frozen=True)
class PartialTrick:
    """
    A partial trick is the move(s) played by the leading player.
    """
    leader_move: Union[RegularMove, Marriage]
    """The move played by the leader of the trick"""

    def is_trump_exchange(self) -> bool:
        """Returns false to indicate that this trick is not a trump exchange"""
        return False

    def __repr__(self) -> str:
        return f"PartialTrick(leader_move={self.leader_move})"


@dataclass(frozen=True)
class RegularTrick(Trick, PartialTrick):
    """
    A regular trick, with a move by the leader and a move by the follower
    """
    follower_move: RegularMove
    """The move played by the follower"""

    def is_trump_exchange(self) -> bool:
        """Returns false to indicate that this trick is not a trump exchange"""
        return False

    def as_partial(self) -> PartialTrick:
        """Returns the first part of this trick. Raises an Exceptption if this is not a Trick with two parts"""
        return PartialTrick(self.leader_move)

    def _cards(self) -> Iterable[Card]:
        """Get all cards used in this tick. This method should not be called directly."""
        return itertools.chain(self.leader_move.cards, self.follower_move.cards)

    def __repr__(self) -> str:
        """A string representation of the Trick"""
        return f"RegularTrick(leader_move={self.leader_move}, follower_move={self.follower_move})"


@dataclass(frozen=True)
class Score:
    """
    The score of one of the bots. This consists of the current points and potential pending points because of an earlier played marriage.
    Note that the socre object is immutable and supports the `+` operator, so it can be used somewhat as a usual number.
    """
    direct_points: int = 0
    """The current number of points"""
    pending_points: int = 0
    """Points to be applied in the future because of a past marriage"""

    def __add__(self, other: Score) -> Score:
        """
        Adds two scores together. Direct points and pending points are added separately.

        :param other: (Score): The score to be added to the current one.
        :returns: (Score): A new score object with the points of the current score and the other combined
        """
        total_direct_points = self.direct_points + other.direct_points
        total_pending_points = self.pending_points + other.pending_points
        return Score(total_direct_points, total_pending_points)

    def redeem_pending_points(self) -> Score:
        """
        Redeem the pending points

        :returns: (Score):A new score object with the pending points added to the direct points and the pending points set to zero.
        """
        return Score(direct_points=self.direct_points + self.pending_points, pending_points=0)

    def __repr__(self) -> str:
        """A string representation of the Score"""
        return f"Score(direct_points={self.direct_points}, pending_points={self.pending_points})"


class GamePhase(Enum):
    """
    An indicator about the phase of the game. This is used because in Schnapsen, the rules change when the game enters the second phase.
    """
    ONE = 1
    TWO = 2


@dataclass
class BotState:
    """A bot with its implementation and current state in a game"""

    implementation: Bot
    hand: Hand
    score: Score = field(default_factory=Score)
    won_cards: list[Card] = field(default_factory=list)

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """
        Gets the next move from the bot itself, passing it the state.
        Does a quick check to make sure that the hand has the cards which are played. More advanced checks are performed outside of this call.

        :param state: (PlayerPerspective): The PlayerGameState which contains the information on the current state of the game from the perspective of this player
        :param leader_move: (Optional[Move]): The move made by the leader of the trick. This is None if the bot is the leader.
        :returns: The move the played
        """
        move = self.implementation.get_move(perspective, leader_move=leader_move)
        assert move is not None, f"The bot {self.implementation} returned a move which is None"
        if not isinstance(move, Move):
            raise AssertionError(f"The bot {self.implementation} returned an object which is not a Move, got {move}")
        return move

    def copy(self) -> BotState:
        """
        Makes a deep copy of the current state.

        :returns: (BotState): The deep copy.
        """
        new_bot = BotState(
            implementation=self.implementation,
            hand=self.hand.copy(),
            score=self.score,  # does not need a copy because it is not mutable
            won_cards=list(self.won_cards),
        )
        return new_bot

    def __repr__(self) -> str:
        return f"BotState(implementation={self.implementation}, hand={self.hand}, "\
               f"score={self.score}, won_cards={self.won_cards})"


@dataclass(frozen=True)
class Previous:
    """
    Information about the previous GameState.
    This object can be used to access the history which lead to the current GameState
    """

    state: GameState
    """The previous state of the game. """
    trick: Trick
    """The trick which led to the current Gamestate from the Previous state"""
    leader_remained_leader: bool
    """Did the leader of remain the leader."""


@dataclass
class GameState:
    """
    The current state of the game, as seen by the game engine.
    This contains all information about the positions of the cards, bots, scores, etc.
    The bot must not get direct access to this information because it would allow it to cheat.
    """
    leader: BotState
    """The current leader, i.e., the one who will play the first move in the next trick"""
    follower: BotState
    """The current follower, i.e., the one who will play the second move in the next trick"""
    trump_suit: Suit = field(init=False)
    """The trump suit in this game. This information is also in the Talon."""
    talon: Talon
    """The talon, containing the cards not yet in the hand of the player and the trump card at the bottom"""
    previous: Optional[Previous]
    """The events which led to this GameState, or None, if this is the initial GameState (or previous tricks and states are unknown)"""

    def __getattribute__(self, __name: str) -> Any:
        if __name == "trump_suit":
            # We get it from the talon
            return self.talon.trump_suit()
        return object.__getattribute__(self, __name)

    def copy_for_next(self) -> GameState:
        """
        Make a copy of the gamestate, modified such that the previous state is this state, but the previous trick is not filled yet.
        This is used to create a GameState which will be modified to become the next gamestate.

        :returns: (Gamestate): A copy of the gamestate, with the previous trick not filled yet.
        """
        # We intentionally do no initialize the previous information. It is not known yet
        new_state = GameState(
            leader=self.leader.copy(),
            follower=self.follower.copy(),
            talon=self.talon.copy(),
            previous=None
        )
        return new_state

    def copy_with_other_bots(self, new_leader: Bot, new_follower: Bot) -> GameState:
        """
        Make a copy of the gamestate, modified such that the bots are replaced by the provided ones.
        This is used to continue playing an existing GameState with different bots.

        :param new_leader: (Bot): The new leader
        :param new_follower: (Bot): The new follower
        :returns: (Gamestate): A copy of the gamestate, with the bots replaced.
        """
        new_state = GameState(
            leader=self.leader.copy(),
            follower=self.follower.copy(),
            talon=self.talon.copy(),
            previous=self.previous
        )
        new_state.leader.implementation = new_leader
        new_state.follower.implementation = new_follower
        return new_state

    def game_phase(self) -> GamePhase:
        """What is the current phase of the game

        :returns: GamePhase.ONE or GamePahse.TWO indicating the current phase
        """
        if self.talon.is_empty():
            return GamePhase.TWO
        return GamePhase.ONE

    def are_all_cards_played(self) -> bool:
        """Returns True in case the players have played all their cards and the game is has come to an end

        :returns: (bool): True if all cards have been played, False otherwise
        """
        return self.leader.hand.is_empty() and self.follower.hand.is_empty() and self.talon.is_empty()

    def __repr__(self) -> str:
        return f"GameState(leader={self.leader}, follower={self.follower}, "\
               f"talon={self.talon}, previous={self.previous})"


class PlayerPerspective(ABC):
    """
    The perspective a player has on the state of the game. This only gives access to the partially observable information.
    The Bot gets passed an instance of this class when it gets requested a move by the GamePlayEngine

    This class has several convenience methods to get more information about the current state.

    :param state: (GameState): The current state of the game
    :param engine: (GamePlayEngine): The engine which is used to play the game5
    :attr __game_state: (GameState): The current state of the game - initialized from the state parameter.5
    :attr __engine: (GamePlayEngine): The engine which is used to play the game - initialized from the engine parameter.
    """

    def __init__(self, state: GameState, engine: GamePlayEngine) -> None:
        self.__game_state = state
        self.__engine = engine

    @abstractmethod
    def valid_moves(self) -> list[Move]:
        """
        Get a list of all valid moves the bot can play at this point in the game.

        Design note: this could also return an Iterable[Move], but list[Move] was chosen to make the API easier to use.
        """

    def get_game_history(self) -> list[tuple[PlayerPerspective, Optional[Trick]]]:
        """
        The game history from the perspective of the player. This means all the past PlayerPerspective this bot has seen, and the Tricks played.
        This only provides access to cards the Bot is allowed to see.

        :returns: (list[tuple[PlayerPerspective, Optional[Trick]]]): The PlayerPerspective and Tricks in chronological order, index 0 is the first round played. Only the last Trick will be None.
        The last pair will contain the current PlayerGameState.
        """

        # We reconstruct the history backwards.
        game_state_history: list[tuple[PlayerPerspective, Optional[Trick]]] = []
        # We first push the current state to the end
        game_state_history.insert(0, (self, None))

        current_leader = self.am_i_leader()
        current = self.__game_state.previous

        while current:
            # If we were leader, and we remained, then we were leader before
            # If we were follower, and we remained, then we were follower before
            # If we were leader, and we did not remain, then we were follower before
            # If we were follower, and we did not remain, then we were leader before
            # This logic gets reflected by the negation of a xor
            current_leader = not current_leader ^ current.leader_remained_leader

            current_player_perspective: PlayerPerspective
            if current_leader:
                current_player_perspective = LeaderPerspective(current.state, self.__engine)
            else:  # We are following
                if current.trick.is_trump_exchange():
                    current_player_perspective = ExchangeFollowerPerspective(current.state, self.__engine)
                else:
                    current_player_perspective = FollowerPerspective(current.state, self.__engine, current.trick.as_partial().leader_move)
            history_record = (current_player_perspective, current.trick)
            game_state_history.insert(0, history_record)

            current = current.state.previous
        return game_state_history

    @abstractmethod
    def get_hand(self) -> Hand:
        """Get the cards in the hand of the current player"""

    @abstractmethod
    def get_my_score(self) -> Score:
        """Get the socre of the current player. The return Score object contains both the direct points and pending points from a marriage."""

    @abstractmethod
    def get_opponent_score(self) -> Score:
        """Get the socre of the other player. The return Score object contains both the direct points and pending points from a marriage."""

    def get_trump_suit(self) -> Suit:
        """Get the suit of the trump"""
        return self.__game_state.trump_suit

    def get_trump_card(self) -> Optional[Card]:
        """Get the card which is at the bottom of the talon. Will be None if the talon is empty"""
        return self.__game_state.talon.trump_card()

    def get_talon_size(self) -> int:
        """How many cards are still on the talon?"""
        return len(self.__game_state.talon)

    def get_phase(self) -> GamePhase:
        """What is the pahse of the game? This returns a GamePhase object.
        You can check the phase by checking state.get_phase == GamePhase.ONE
        """
        return self.__game_state.game_phase()

    @abstractmethod
    def get_opponent_hand_in_phase_two(self) -> Hand:
        """If the game is in the second phase, you can get the cards in the hand of the opponent.
        If this gets called, but the second pahse has not started yet, this will throw en Exception
        """

    @abstractmethod
    def am_i_leader(self) -> bool:
        """Returns True if the bot is the leader of this trick, False if it is a follower."""

    @abstractmethod
    def get_won_cards(self) -> CardCollection:
        """Get a list of all cards this Bot has won until now."""

    @abstractmethod
    def get_opponent_won_cards(self) -> CardCollection:
        """Get the list of cards the opponent has won until now."""

    def __get_own_bot_state(self) -> BotState:
        """Get the internal state object of this bot. This should not be used by a bot."""
        bot: BotState
        if self.am_i_leader():
            bot = self.__game_state.leader
        else:
            bot = self.__game_state.follower
        return bot

    def __get_opponent_bot_state(self) -> BotState:
        """Get the internal state object of the other bot. This should not be used by a bot."""
        bot: BotState
        if self.am_i_leader():
            bot = self.__game_state.follower
        else:
            bot = self.__game_state.leader
        return bot

    def seen_cards(self, leader_move: Optional[Move]) -> CardCollection:
        """Get a list of all cards your bot has seen until now

        :param leader_move: (Optional[Move]):The move made by the leader of the trick. These cards have also been seen until now.
        :returns: (CardCollection): A list of all cards your bot has seen until now
        """
        bot = self.__get_own_bot_state()

        seen_cards: set[Card] = set()  # We make it a set to remove duplicates

        # in own hand
        seen_cards.update(bot.hand)

        # the trump card
        trump = self.get_trump_card()
        if trump:
            seen_cards.add(trump)

        # all cards which were played in Tricks (icludes marriages and Trump exchanges)

        seen_cards.update(self.__past_tricks_cards())
        if leader_move is not None:
            seen_cards.update(leader_move.cards)

        return OrderedCardCollection(seen_cards)

    def __past_tricks_cards(self) -> set[Card]:
        """
        Gets the cards played in past tricks

        :returns: (set[Card]): A set of all cards played in past tricks
        """
        past_cards: set[Card] = set()
        prev = self.__game_state.previous
        while prev:
            past_cards.update(prev.trick.cards)
            prev = prev.state.previous
        return past_cards

    def get_known_cards_of_opponent_hand(self) -> CardCollection:
        """Get all cards which are in the opponents hand, but known to your Bot. This includes cards earlier used in marriages, or a trump exchange.
        All cards in the second pahse of the game.

        :returns: (CardCollection): A list of all cards which are in the opponents hand, which are known to the bot.
        """
        opponent_hand = self.__get_opponent_bot_state().hand
        if self.get_phase() == GamePhase.TWO:
            return opponent_hand
        # We only disclose cards which have been part of a move, i.e., an Exchange or a Marriage
        past_trick_cards = self.__past_tricks_cards()
        return OrderedCardCollection(filter(lambda c: c in past_trick_cards, opponent_hand))

    def get_engine(self) -> GamePlayEngine:
        """
        Get the GamePlayEngine in use for the current game.
        This engine can be used to retrieve all information about what kind of game we are playing,
        but can also be used to simulate alternative game rollouts.

        :returns: (GamePlayEngine): The GamePlayEngine in use for the current game.
        """
        return self.__engine

    def get_state_in_phase_two(self) -> GameState:
        """
        In phase TWO of the game, all information is known, so you can get the complete state

        This removes the real bots from the GameState. If you want to continue the game, provide new Bots. See copy_with_other_bots in the GameState class.

        :retruns: (GameState): The GameState in phase two of the game - the active bots are replaced by dummy bots.
        """

        if self.get_phase() == GamePhase.TWO:
            return self.__game_state.copy_with_other_bots(_DummyBot(), _DummyBot())
        raise AssertionError("You cannot get the state in phase one")

    def make_assumption(self, leader_move: Optional[Move], rand: Random) -> GameState:
        """
        Takes the current imperfect information state and makes a random guess as to the position of the unknown cards.
        This also takes into account cards seen earlier during marriages played by the opponent, as well as potential trump jack exchanges

        This removes the real bots from the GameState. If you want to continue the game, provide new Bots. See copy_with_other_bots in the GameState class.

        :param leader_move: (Optional[Move]): the optional already executed leader_move in the current trick. This card is guaranteed to be in the hand of the leader in the returned GameState.
        :param rand: (Random):the source of random numbers to do the random assignment of unknown cards

        :returns: GameState: A perfect information state object.
        """
        opponent_hand = self.__get_opponent_bot_state().hand.copy()

        if leader_move is not None:
            assert all(card in opponent_hand for card in leader_move.cards), f"The specified leader_move {leader_move} is not in the hand of the opponent {opponent_hand}"

        full_state = self.__game_state.copy_with_other_bots(_DummyBot(), _DummyBot())
        if self.get_phase() == GamePhase.TWO:
            return full_state

        seen_cards = self.seen_cards(leader_move)
        full_deck = self.__engine.deck_generator.get_initial_deck()

        opponent_hand = self.__get_opponent_bot_state().hand.copy()
        unseen_opponent_hand = list(filter(lambda card: card not in seen_cards, opponent_hand))

        talon = full_state.talon
        unseen_talon = list(filter(lambda card: card not in seen_cards, talon))

        unseen_cards = list(filter(lambda card: card not in seen_cards, full_deck))
        if len(unseen_cards) > 1:
            rand.shuffle(unseen_cards)

        assert len(unseen_talon) + len(unseen_opponent_hand) == len(unseen_cards), "Logical error. The number of unseen cards in the opponents hand and in the talon must be equal to the number of unseen cards"

        new_talon: list[Card] = []
        for card in talon:
            if card in unseen_talon:
                # take one of the random cards
                new_talon.append(unseen_cards.pop())
            else:
                new_talon.append(card)

        full_state.talon = Talon(new_talon)

        new_opponent_hand = []
        for card in opponent_hand:
            if card in unseen_opponent_hand:
                new_opponent_hand.append(unseen_cards.pop())
            else:
                new_opponent_hand.append(card)
        if self.am_i_leader():
            full_state.follower.hand = Hand(new_opponent_hand)
        else:
            full_state.leader.hand = Hand(new_opponent_hand)

        assert len(unseen_cards) == 0, "All cards must be consumed by either the opponent hand or talon by now"

        return full_state


class _DummyBot(Bot):
    """A bot used by PlayerPerspective.make_assumption to replace the real bots. This bot cannot play and will throw an Exception for everything"""

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        raise Exception("The GameState from make_assumption removes the real bots from the Game. If you want to continue the game, provide new Bots. See copy_with_other_bots in the GameState class.")

    def notify_game_end(self, won: bool, perspective: PlayerPerspective) -> None:
        raise Exception("The GameState from make_assumption removes the real bots from the Game. If you want to continue the game, provide new Bots. See copy_with_other_bots in the GameState class.")

    def notify_trump_exchange(self, move: TrumpExchange) -> None:
        raise Exception("The GameState from make_assumption removes the real bots from the Game. If you want to continue the game, provide new Bots. See copy_with_other_bots in the GameState class.")


class LeaderPerspective(PlayerPerspective):
    """
    The playerperspective of the Leader.

    :param state: (GameState): The current state of the game
    :param engine: (GamePlayEngine): The engine which is used to play the game
    :attr __game_state: (GameState): The current state of the game - initialized from the state parameter.
    :attr __engine: (GamePlayEngine): The engine which is used to play the game - initialized from the engine parameter.
    """

    def __init__(self, state: GameState, engine: GamePlayEngine) -> None:
        super().__init__(state, engine)
        self.__game_state = state
        self.__engine = engine

    def valid_moves(self) -> list[Move]:
        """
        Get a list of all valid moves the bot can play at this point in the game.

        :returns: (list[Move]): A list of all valid moves the bot can play at this point in the game.
        """
        moves = self.__engine.move_validator.get_legal_leader_moves(self.__engine, self.__game_state)
        return list(moves)

    def get_hand(self) -> Hand:
        """
        Get the cards in the hand of the leader

        :returns: (Hand): The cards in the hand of the leader
        """
        return self.__game_state.leader.hand.copy()

    def get_my_score(self) -> Score:
        """
        Get the score of the leader

        :returns: (Score): The score of the leader
        """
        return self.__game_state.leader.score

    def get_opponent_score(self) -> Score:
        """
        Get the score of the follower
        """
        return self.__game_state.follower.score

    def get_opponent_hand_in_phase_two(self) -> Hand:
        """
        Get the cards in the hand of the follower. This is only allowed in the second phase of the game.

        :returns: (Hand): The cards in the hand of the follower
        """
        assert self.get_phase() == GamePhase.TWO, "Cannot get the hand of the opponent in pahse one"
        return self.__game_state.follower.hand.copy()

    def am_i_leader(self) -> bool:
        """
        Returns True because this is the leader perspective
        """
        return True

    def get_won_cards(self) -> CardCollection:
        """
        Get a list of all tricks the leader has won until now.

        :returns: (CardCollection): A CardCollection of all tricks the leader has won until now.
        """
        return OrderedCardCollection(self.__game_state.leader.won_cards)

    def get_opponent_won_cards(self) -> CardCollection:
        """
        Get a list of all tricks the follower has won until now.

        :returns: (CardCollection): A CardCollection of all tricks the follower has won until now.
        """

        return OrderedCardCollection(self.__game_state.follower.won_cards)

    def __repr__(self) -> str:
        return f"LeaderPerspective(state={self.__game_state}, engine={self.__engine})"


class FollowerPerspective(PlayerPerspective):
    """
    The playerperspective of the Follower.

    :param state: (GameState): The current state of the game
    :param engine: (GamePlayEngine): The engine which is used to play the game
    :param leader_move: (Optional[Move]): The move made by the leader of the trick. This is None if the bot is the leader.
    :attr __game_state: (GameState): The current state of the game - initialized from the state parameter.
    :attr __engine: (GamePlayEngine): The engine which is used to play the game - initialized from the engine parameter.
    :attr __leader_move: (Optional[Move]): The move made by the leader of the trick. This is None if the bot is the leader.
    """

    def __init__(self, state: GameState, engine: GamePlayEngine, leader_move: Optional[Move]) -> None:
        super().__init__(state, engine)
        self.__game_state = state
        self.__engine = engine
        self.__leader_move = leader_move

    def valid_moves(self) -> list[Move]:
        """
        Get a list of all valid moves the bot can play at this point in the game.

        :returns: (list[Move]): A list of all valid moves the bot can play at this point in the game.
        """

        assert self.__leader_move, "There is no leader move for this follower, so no valid moves."
        return list(self.__engine.move_validator.get_legal_follower_moves(self.__engine, self.__game_state, self.__leader_move))

    def get_hand(self) -> Hand:
        """
        Get the cards in the hand of the follower

        :returns: (Hand): The cards in the hand of the follower
        """
        return self.__game_state.follower.hand.copy()

    def get_my_score(self) -> Score:
        """
        Get the score of the follower

        :returns: (Score): The score of the follower
        """
        return self.__game_state.follower.score

    def get_opponent_score(self) -> Score:
        """
        Get the score of the leader

        :returns: (Score): The score of the leader
        """

        return self.__game_state.leader.score

    def get_opponent_hand_in_phase_two(self) -> Hand:
        """
        Get the cards in the hand of the leader. This is only allowed in the second phase of the game.

        :returns: (Hand): The cards in the hand of the leader
        """

        assert self.get_phase() == GamePhase.TWO, "Cannot get the hand of the opponent in pahse one"
        return self.__game_state.leader.hand.copy()

    def am_i_leader(self) -> bool:
        """ Returns False because this is the follower perspective"""
        return False

    def get_won_cards(self) -> CardCollection:
        """
        Get a list of all tricks the follower has won until now.

        :returns: (CardCollection): A CardCollection of all tricks the follower has won until now.
        """

        return OrderedCardCollection(self.__game_state.follower.won_cards)

    def get_opponent_won_cards(self) -> CardCollection:
        """
        Get a list of all tricks the leader has won until now.

        :returns: (CardCollection): A CardCollection of all tricks the leader has won until now.
        """

        return OrderedCardCollection(self.__game_state.leader.won_cards)

    def __repr__(self) -> str:
        return f"FollowerPerspective(state={self.__game_state}, engine={self.__engine}, leader_move={self.__leader_move})"


class ExchangeFollowerPerspective(PlayerPerspective):
    """
    A special PlayerGameState only used for the history of a game in which a Trump Exchange happened.
    This state is does not allow any moves.

    :param state: (GameState): The current state of the game
    :param engine: (GamePlayEngine): The engine which is used to play the game
    :attr __game_state: (GameState): The current state of the game - initialized from the state parameter.
    :attr __engine: (GamePlayEngine): The engine which is used to play the game - initialized from the engine parameter.

    """

    def __init__(self, state: GameState, engine: GamePlayEngine) -> None:
        self.__game_state = state
        super().__init__(state, engine)

    def valid_moves(self) -> list[Move]:
        """
        Get a list of all valid moves the bot can play at this point in the game.

        Design note: this could also return an Iterable[Move], but list[Move] was chosen to make the API easier to use.

        :returns: (list[Move]): An empty list, because no moves are allowed in this state.
        """
        return []

    def get_hand(self) -> Hand:
        """
        Get the cards in the hand of the follower

        :returns: (Hand): The cards in the hand of the follower
        """

        return self.__game_state.follower.hand.copy()

    def get_my_score(self) -> Score:
        """
        Get the score of the follower

        :returns: (Score): The score of the follower
        """

        return self.__game_state.follower.score

    def get_opponent_score(self) -> Score:
        """
        Get the score of the leader

        :returns: (Score): The score of the leader
        """

        return self.__game_state.leader.score

    def get_trump_suit(self) -> Suit:
        """
        Get the suit of the trump

        :returns: (Suit): The suit of the trump
        """
        return self.__game_state.trump_suit

    def get_opponent_hand_in_phase_two(self) -> Hand:
        """
        Get the cards in the hand of the leader. This is only allowed in the second phase of the game.

        :returns: (Hand): The cards in the hand of the leader
        """
        assert self.get_phase() == GamePhase.TWO, "Cannot get the hand of the opponent in pahse one"
        return self.__game_state.leader.hand.copy()

    def get_opponent_won_cards(self) -> CardCollection:
        """
        Get a list of all tricks the leader has won until now.

        :returns: (CardCollection): A CardCollection of all tricks the leader has won until now.
        """
        return OrderedCardCollection(self.__game_state.leader.won_cards)

    def get_won_cards(self) -> CardCollection:
        """
        Get a list of all tricks the follower has won until now.

        :returns: (CardCollection): A CardCollection of all tricks the follower has won until now.
        """

        return OrderedCardCollection(self.__game_state.follower.won_cards)

    def am_i_leader(self) -> bool:
        """ Returns False because this is the follower perspective"""
        return False


class WinnerPerspective(LeaderPerspective):
    """
    The gamestate given to the winner of the game at the very end

    :param state: (GameState): The current state of the game
    :param engine: (GamePlayEngine): The engine which is used to play the game
    :attr __game_state: (GameState): The current state of the game - initialized from the state parameter.
    :attr __engine: (GamePlayEngine): The engine which is used to play the game - initialized from the engine parameter.
    """

    def __init__(self, state: GameState, engine: GamePlayEngine) -> None:
        self.__game_state = state
        self.__engine = engine
        super().__init__(state, engine)

    def valid_moves(self) -> list[Move]:
        """raise an Exception because the game is over"""
        raise Exception("Cannot request valid moves from the final PlayerGameState because the game is over")

    def __repr__(self) -> str:
        return f"WinnerGameState(state={self.__game_state}, engine={self.__engine})"


class LoserPerspective(FollowerPerspective):
    """
    The gamestate given to the loser of the game at the very end

    :param state: (GameState): The current state of the game
    :param engine: (GamePlayEngine): The engine which is used to play the game
    :attr __game_state: (GameState): The current state of the game - initialized from the state parameter.
    :attr __engine: (GamePlayEngine): The engine which is used to play the game - initialized from the engine parameter.
    """

    def __init__(self, state: GameState, engine: GamePlayEngine) -> None:
        self.__game_state = state
        self.__engine = engine
        super().__init__(state, engine, None)

    def valid_moves(self) -> list[Move]:
        """raise an Exception because the game is over"""
        raise Exception("Cannot request valid moves from the final PlayerGameState because the game is over")

    def __repr__(self) -> str:
        return f"LoserGameState(state={self.__game_state}, engine={self.__engine})"


class DeckGenerator(ABC):
    """
    A Deckgenerator specifies how what the cards for a game are.
    """

    @abstractmethod
    def get_initial_deck(self) -> OrderedCardCollection:
        """
        Get the intial deck of cards which are used in the game.
        This method must always return the same set of cards in the same order.
        """

    @classmethod
    def shuffle_deck(cls, deck: OrderedCardCollection, rng: Random) -> OrderedCardCollection:
        """
        Shuffle the given deck of cards, using the random number generator as a source of randomness.

        :param deck: (OrderedCardCollection): The deck to shuffle.
        :param rng: (Random): The source of randomness.
        :returns: (OrderedCardCollection): The shuffled deck.
        """
        the_cards = list(deck.get_cards())
        rng.shuffle(the_cards)
        return OrderedCardCollection(the_cards)


class SchnapsenDeckGenerator(DeckGenerator):
    """
    The deck generator for the game of Schnapsen. This generator always creates the same deck of cards, in the same order.

    :attr deck: (list[Card]): The deck of cards generated.
    """

    def __init__(self) -> None:
        self.deck: list[Card] = []
        for suit in Suit:
            for rank in [Rank.JACK, Rank.QUEEN, Rank.KING, Rank.TEN, Rank.ACE]:
                self.deck.append(Card.get_card(rank, suit))

    def get_initial_deck(self) -> OrderedCardCollection:
        """
        Get the intial deck of cards which are used in the game.

        :returns: (OrderedCardCollection): The deck of cards used in the game.
        """
        return OrderedCardCollection(self.deck)


class HandGenerator(ABC):
    """
    The HandGenerator specifies how the intial set of cards gets divided over the two player's hands and the talon
    """
    @abstractmethod
    def generateHands(self, cards: OrderedCardCollection) -> tuple[Hand, Hand, Talon]:
        """
        Divide the collection of cards over the two hands and the Talon

        :param cards: The cards to be dealt
        :returns: Two hands of cards and the talon. The first hand is for the first player, i.e, the one who will lead the first trick.
        """


class SchnapsenHandGenerator(HandGenerator):
    """Class used for generating the hands for the game of Schnapsen"""
    @classmethod
    def generateHands(self, cards: OrderedCardCollection) -> tuple[Hand, Hand, Talon]:
        """
        Divide the collection of cards over the two hands and the Talon

        :param cards: (OrderedCardCollection): The cards to be dealt
        :returns: (tuple[Hand, Hand, Talon]): Two hands of cards and the talon. The first hand is for the first player, i.e, the one who will lead the first trick.
        """

        the_cards = list(cards.get_cards())
        hand1 = Hand([the_cards[i] for i in range(0, 10, 2)], max_size=5)
        hand2 = Hand([the_cards[i] for i in range(1, 11, 2)], max_size=5)
        rest = Talon(the_cards[10:])
        return (hand1, hand2, rest)


class TrickImplementer(ABC):
    """
    The TrickImplementer is a blueprint for classes that specify how tricks are palyed in the game.
    """
    @abstractmethod
    def play_trick(self, game_engine: GamePlayEngine, game_state: GameState) -> GameState:
        """
        Plays a single Trick the game by asking the bots in the game_state for their Moves,
        using the MoveRequester from the game_engine.
        These moves are then also validated using the MoveValidator of the game_engine.
        Finally, the trick is recorder in the history (previous field) of the returned GameState.

        Note, the provided GameState does not get modified by this method.

        :param game_engine: The engine used to preform the underlying actions of the Trick.
        :param game_state: The state of the game before the trick is played. Thi state will not be modified.
        :returns: The GameState after the trick is completed.
        """

    @abstractmethod
    def play_trick_with_fixed_leader_move(self, game_engine: GamePlayEngine, game_state: GameState,
                                          leader_move: Move) -> GameState:
        """
        The same as play_trick, but also takes the leader_move to start with as an argument.
        """


class SchnapsenTrickImplementer(TrickImplementer):
    """
    Child of TrickImplementer, SchnapsenTrickImplementer specifies how tricks are played in the game.
    """

    def play_trick(self, game_engine: GamePlayEngine, game_state: GameState) -> GameState:
        # TODO: Fix the docstring
        """
        Plays a single Trick the game by asking the bots in the game_state for their Moves,
        first asks the leader for their move, and then depending on the resulting gamestate
        in self.play_trick_with_fixed_leader_move, will ask (or not ask) the follower for a move.

        :param game_engine: (GamePlayEngine): The engine used to preform the underlying actions of the Trick.
        :param game_state: (GameState): The state of the game before the trick is played. This state will not be modified.
        :returns: (GameState): The GameState after the trick is completed.
        """
        leader_move = self.get_leader_move(game_engine, game_state)
        return self.play_trick_with_fixed_leader_move(game_engine=game_engine, game_state=game_state, leader_move=leader_move)

    def play_trick_with_fixed_leader_move(self, game_engine: GamePlayEngine, game_state: GameState,
                                          leader_move: Move) -> GameState:
        """
        Plays a trick with a fixed leader move, in order to determine the follower move. Potentially asks the folower for a move.

        :param game_engine: (GamePlayEngine): The engine used to preform the underlying actions of the Trick.
        :param game_state: (GameState): The state of the game before the trick is played. This state will not be modified.
        :param leader_move: (Move): The move made by the leader of the trick.
        :returns: (GameState): The GameState after the trick is completed.
        """
        if leader_move.is_trump_exchange():
            next_game_state = game_state.copy_for_next()
            exchange = cast(TrumpExchange, leader_move)
            old_trump_card = game_state.talon.trump_card()
            assert old_trump_card, "There is no card at the bottom of the talon"
            self.play_trump_exchange(next_game_state, exchange)
            # remember the previous state
            next_game_state.previous = Previous(game_state, ExchangeTrick(exchange, old_trump_card), True)
            # The whole trick ends here.
            return next_game_state

        # We have a PartialTrick, ask the follower for its move
        leader_move = cast(Union[Marriage, RegularMove], leader_move)
        follower_move = self.get_follower_move(game_engine, game_state, leader_move)

        trick = RegularTrick(leader_move=leader_move, follower_move=follower_move)
        return self._apply_regular_trick(game_engine=game_engine, game_state=game_state, trick=trick)

    def _apply_regular_trick(self, game_engine: GamePlayEngine, game_state: GameState, trick: RegularTrick) -> GameState:
        """
        Applies the given regular trick to the given game state, returning the resulting game state.

        :param game_engine: (GamePlayEngine): The engine used to preform the underlying actions of the Trick.
        :param game_state: (GameState): The state of the game before the trick is played. This state will not be modified.
        :param trick: (RegularTrick): The trick to be applied to the game state.
        :returns: (GameState): The GameState after the trick is completed.
        """

        # apply the trick to the next_game_state
        # The next game state will be modified during this trick. We start from the previous state
        next_game_state = game_state.copy_for_next()

        if trick.leader_move.is_marriage():
            marriage_move: Marriage = cast(Marriage, trick.leader_move)
            self._play_marriage(game_engine, next_game_state, marriage_move=marriage_move)
            regular_leader_move: RegularMove = cast(Marriage, trick.leader_move).underlying_regular_move()
        else:
            regular_leader_move = cast(RegularMove, trick.leader_move)

        # # apply changes in the hand and talon
        next_game_state.leader.hand.remove(regular_leader_move.card)
        next_game_state.follower.hand.remove(trick.follower_move.card)

        # We set the leader for the next state based on what the scorer decides
        next_game_state.leader, next_game_state.follower, leader_remained_leader = game_engine.trick_scorer.score(trick, next_game_state.leader, next_game_state.follower, next_game_state.trump_suit)

        # important: the winner takes the first card of the talon, the loser the second one.
        # this also ensures that the loser of the last trick of the first phase gets the face up trump
        if not next_game_state.talon.is_empty():
            drawn = iter(next_game_state.talon.draw_cards(2))
            next_game_state.leader.hand.add(next(drawn))
            next_game_state.follower.hand.add(next(drawn))

        next_game_state.previous = Previous(game_state, trick=trick, leader_remained_leader=leader_remained_leader)

        return next_game_state

    def get_leader_move(self, game_engine: GamePlayEngine, game_state: GameState) -> Move:
        """
        Get the move of the leader of the trick.

        :param game_engine: (GamePlayEngine): The engine used to preform the underlying actions of the Trick.
        :param game_state: (GameState): The state of the game before the trick is played. This state will not be modified.
        :returns: (Move): The move of the leader of the trick.
        """

        # ask first players move trough the requester
        leader_game_state = LeaderPerspective(game_state, game_engine)
        leader_move = game_engine.move_requester.get_move(game_state.leader, leader_game_state, None)
        if not game_engine.move_validator.is_legal_leader_move(game_engine, game_state, leader_move):
            raise Exception(f"Leader {game_state.leader.implementation} played an illegal move")

        return leader_move

    def play_trump_exchange(self, game_state: GameState, trump_exchange: TrumpExchange) -> None:
        """
        Apply a trump exchange to the given game state. This method modifies the game state.

        :param game_state: (GameState): The state of the game before the trump exchange is played. This state will be modified.
        :param trump_exchange: (TrumpExchange): The trump exchange to be applied to the game state.
        """
        assert trump_exchange.jack.suit is game_state.trump_suit, \
            f"A trump exchange can only be done with a Jack of the same suit as the current trump. Got a {trump_exchange.jack} while the  Trump card is a {game_state.trump_suit}"
        # apply the changes in the gamestate
        game_state.leader.hand.remove(trump_exchange.jack)
        old_trump = game_state.talon.trump_exchange(trump_exchange.jack)
        game_state.leader.hand.add(old_trump)
        # We notify the both bots that an exchange happened
        game_state.leader.implementation.notify_trump_exchange(trump_exchange)
        game_state.follower.implementation.notify_trump_exchange(trump_exchange)

    def _play_marriage(self, game_engine: GamePlayEngine, game_state: GameState, marriage_move: Marriage) -> None:
        """
        Apply a marriage to the given game state. This method modifies the game state.

        :param game_engine: (GamePlayEngine): The engine used to preform the underlying actions of the Trick.
        :param game_state: (GameState): The state of the game before the marriage is played. This state will be modified.
        :param marriage_move: (Marriage): The marriage to be applied to the game state.
        """

        score = game_engine.trick_scorer.marriage(marriage_move, game_state)
        game_state.leader.score += score

    def get_follower_move(self, game_engine: GamePlayEngine, game_state: GameState, leader_move: Move) -> RegularMove:
        """
        Get the move of the follower of the trick.

        :param game_engine: (GamePlayEngine): The engine used to preform the underlying actions of the Trick.
        :param game_state: (GameState): The state of the game before the trick is played. This state will not be modified.
        :param leader_move: (Move): The move made by the leader of the trick.
        :returns: (RegularMove): The move of the follower of the trick.
        """

        follower_game_state = FollowerPerspective(game_state, game_engine, leader_move)

        follower_move = game_engine.move_requester.get_move(game_state.follower, follower_game_state, leader_move)
        if not game_engine.move_validator.is_legal_follower_move(game_engine, game_state, leader_move, follower_move):
            raise Exception(f"Follower {game_state.follower.implementation} played an illegal move")
        return cast(RegularMove, follower_move)


class MoveRequester:
    """
    An moveRequester captures the logic of requesting a move from a bot.
    This logic also determines what happens in case the bot is to slow, throws an exception during operation, etc
    """

    @abstractmethod
    def get_move(self, bot: BotState, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """
        Get a move from the bot, potentially applying timeout logic.

        """


class SimpleMoveRequester(MoveRequester):
    """The SimplemoveRquester just asks the move, and does not time out"""

    def get_move(self, bot: BotState, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """
        Get a move from the bot

        :param bot: (BotState): The bot to request the move from
        :param perspective: (PlayerPerspective): The perspective of the bot
        :param leader_move: (Optional[Move]): The move made by the leader of the trick. This is None if the bot is the leader.
        """
        return bot.get_move(perspective, leader_move=leader_move)


class _DummyFile(StringIO):
    """
    A dummy file that does not write anything.
    """

    def write(self, _: str) -> int:
        return 0

    def flush(self) -> None:
        pass


class SilencingMoveRequester(MoveRequester):
    """
    This MoveRequester just asks the move, but before doing so it routes stdout to a dummy file

    :param requester: (MoveRequester): The MoveRequester to use to request the move.
    """

    def __init__(self, requester: MoveRequester) -> None:
        self.requester = requester

    @contextlib.contextmanager
    @staticmethod
    def __nostdout() -> Generator[None, Any, None]:
        """
        A context manager that silences stdout

        :returns: (Generator[None, Any, None]): A context manager that silences stdout
        """

        save_stdout = sys.stdout
        sys.stdout = _DummyFile()
        yield
        sys.stdout = save_stdout

    def get_move(self, bot: BotState, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        """
        Get a move from the bot, potentially applying timeout logic.

        :param bot: (BotState): The bot to request the move from
        :param perspective: (PlayerPerspective): The perspective of the bot
        :param leader_move: (Optional[Move]): The move made by the leader of the trick. This is None if the bot is the leader.
        :returns: (Move): The move returned by the bot.
        """

        with SilencingMoveRequester.__nostdout():
            return self.requester.get_move(bot, perspective, leader_move)


class MoveValidator(ABC):
    """
    An object of this class can be used to check whether a move is valid.
    """
    @abstractmethod
    def get_legal_leader_moves(self, game_engine: GamePlayEngine, game_state: GameState) -> Iterable[Move]:
        """
        Get all legal moves for the current leader of the game.

        :param game_engine: The engine which is playing the game
        :param game_state: The current state of the game

        :returns: An iterable containing the current legal moves.
        """

    def is_legal_leader_move(self, game_engine: GamePlayEngine, game_state: GameState, move: Move) -> bool:
        """
        Whether the provided move is legal for the leader to play.
        The basic implementation checks whether the move is in the legal leader moves.
        Derived classes might implement this more performantly.
        """
        assert move, 'The move played by the leader cannot be None'
        return move in self.get_legal_leader_moves(game_engine, game_state)

    @abstractmethod
    def get_legal_follower_moves(self, game_engine: GamePlayEngine, game_state: GameState, leader_move: Move) -> Iterable[Move]:
        """
        Get all legal moves for the current follower of the game.

        :param game_engine: The engine which is playing the game
        :param game_state: The current state of the game
        :param leader_move: The move played by the leader of the trick.

        :returns: An iterable containing the current legal moves.
        """

    def is_legal_follower_move(self, game_engine: GamePlayEngine, game_state: GameState, leader_move: Move, move: Move) -> bool:
        """
        Whether the provided move is legal for the follower to play.
        The basic implementation checks whether the move is in the legal fllower moves.
        Derived classes might implement this more performantly.
        """
        assert move, 'The move played by the follower cannot be None'
        assert leader_move, 'The move played by the leader cannot be None'
        return move in self.get_legal_follower_moves(game_engine=game_engine, game_state=game_state, leader_move=leader_move)


class SchnapsenMoveValidator(MoveValidator):
    """
    The move validator for the game of Schnapsen.
    """

    def get_legal_leader_moves(self, game_engine: GamePlayEngine, game_state: GameState) -> Iterable[Move]:
        """
        Get all legal moves for the current leader of the game.

        :param game_engine: The engine which is playing the game
        :param game_state: The current state of the game

        :returns: An iterable containing the current legal moves.
        """
        # all cards in the hand can be played
        cards_in_hand = game_state.leader.hand
        valid_moves: list[Move] = [RegularMove(card) for card in cards_in_hand]
        # trump exchanges
        if not game_state.talon.is_empty():
            trump_jack = Card.get_card(Rank.JACK, game_state.trump_suit)
            if trump_jack in cards_in_hand:
                valid_moves.append(TrumpExchange(trump_jack))
        # mariages
        for card in cards_in_hand.filter_rank(Rank.QUEEN):
            king_card = Card.get_card(Rank.KING, card.suit)
            if king_card in cards_in_hand:
                valid_moves.append(Marriage(card, king_card))
        return valid_moves

    def is_legal_leader_move(self, game_engine: GamePlayEngine, game_state: GameState, move: Move) -> bool:
        """
        Whether the provided move is legal for the leader to play.

        :param game_engine: (GamePlayEngine): The engine which is playing the game
        :param game_state: (GameState): The current state of the game
        :param move: (Move): The move to check

        :returns: (bool): Whether the move is legal
        """
        cards_in_hand = game_state.leader.hand
        if move.is_marriage():
            marriage_move = cast(Marriage, move)
            # we do not have to check whether they are the same suit because of the implementation of Marriage
            return marriage_move.queen_card in cards_in_hand and marriage_move.king_card in cards_in_hand
        if move.is_trump_exchange():
            if game_state.talon.is_empty():
                return False
            trump_move: TrumpExchange = cast(TrumpExchange, move)
            return trump_move.jack in cards_in_hand
        # it has to be a regular move
        regular_move = cast(RegularMove, move)
        return regular_move.card in cards_in_hand

    def get_legal_follower_moves(self, game_engine: GamePlayEngine, game_state: GameState, leader_move: Move) -> Iterable[Move]:
        """
        Get all legal moves for the current follower of the game.

        :param game_engine: (GamePlayEngine): The engine which is playing the game
        :param game_state: (GameState): The current state of the game
        :param leader_move: (Move): The move played by the leader of the trick.

        :returns: (Iterable[Move]): An iterable containing the current legal moves.
        """

        hand = game_state.follower.hand
        if leader_move.is_marriage():
            leader_card = cast(Marriage, leader_move).queen_card
        else:
            leader_card = cast(RegularMove, leader_move).card
        if game_state.game_phase() is GamePhase.ONE:
            # no need to follow, any card in the hand is a legal move
            return RegularMove.from_cards(hand.get_cards())
        # information from https://www.pagat.com/marriage/schnaps.html
        # ## original formulation ##
        # if your opponent leads a non-trump:
        #     you must play a higher card of the same suit if you can;
        #     failing this you must play a lower card of the same suit;
        #     if you have no card of the suit that was led you must play a trump;
        #     if you have no trumps either you may play anything.
        # If your opponent leads a trump:
        #     you must play a higher trump if possible;
        #     if you have no higher trump you must play a lower trump;
        #     if you have no trumps at all you may play anything.
        # ## implemented version, realizing that the rules for trump are overlapping with the normal case ##
        # you must play a higher card of the same suit if you can
        # failing this, you must play a lower card of the same suit;
        # --new--> failing this, if the opponen did not play a trump, you must play a trump
        # failing this, you can play anything
        leader_card_score = game_engine.trick_scorer.rank_to_points(leader_card.rank)
        # you must play a higher card of the same suit if you can;
        same_suit_cards = hand.filter_suit(leader_card.suit)
        if same_suit_cards:
            higher_same_suit, lower_same_suit = [], []
            for card in same_suit_cards:
                # TODO this is slightly ambigousm should this be >= ??
                higher_same_suit.append(card) if game_engine.trick_scorer.rank_to_points(card.rank) > leader_card_score else lower_same_suit.append(card)
            if higher_same_suit:
                return RegularMove.from_cards(higher_same_suit)
        # failing this, you must play a lower card of the same suit;
            elif lower_same_suit:
                return RegularMove.from_cards(lower_same_suit)
            raise AssertionError("Somethign is wrong in the logic here. There should be cards, but they are neither placed in the low, nor higher list")
        # failing this, if the opponen did not play a trump, you must play a trump
        trump_cards = hand.filter_suit(game_state.trump_suit)
        if leader_card.suit != game_state.trump_suit and trump_cards:
            return RegularMove.from_cards(trump_cards)
        # failing this, you can play anything
        return RegularMove.from_cards(hand.get_cards())


class TrickScorer(ABC):
    @abstractmethod
    def score(self, trick: RegularTrick, leader: BotState, follower: BotState, trump: Suit) -> tuple[BotState, BotState, bool]:
        """
        Score the trick for the given leader and follower. The returned bots are the same bots provided (not copies) and have the score of the trick applied.
        They are returned in order (new_leader, new_follower). If appropriate, also pending points have been applied.
        The boolean is True if the leading bot remained the same, i.e., the past leader remains the leader
        """

    @abstractmethod
    def declare_winner(self, game_state: GameState) -> Optional[tuple[BotState, int]]:
        """return a bot and the number of points if there is a winner of this game already

        :param game_state: The current state of the game
        :returns: The botstate of the winner and the number of game points, in case there is a winner already. Otherwise None.

        """

    @abstractmethod
    def rank_to_points(self, rank: Rank) -> int:
        """Get the point value for a given rank

        :param rank: the rank of a card for which you want to obtain the points
        :returns: The score for that card
        """

    @abstractmethod
    def marriage(self, move: Marriage, gamestate: GameState) -> Score:
        """Get the score which the player obtains for the given marriage

        :param move: The marriage for which to get the score
        :param gamestate: the current state of the game, usually used to get the trump suit
        :returns: The score for this marriage
        """


class SchnapsenTrickScorer(TrickScorer):
    """
    A TrickScorer that scores ac cording to the Schnapsen rules
    """

    SCORES = {
        Rank.ACE: 11,
        Rank.TEN: 10,
        Rank.KING: 4,
        Rank.QUEEN: 3,
        Rank.JACK: 2,
    }

    def rank_to_points(self, rank: Rank) -> int:
        """
        Convert a rank to the number of points it is worth.

        :param rank: The rank to convert.
        :returns: The number of points the rank is worth.
        """
        return SchnapsenTrickScorer.SCORES[rank]

    def marriage(self, move: Marriage, gamestate: GameState) -> Score:
        """
        Get the score which the player obtains for the given marriage

        :param move: The marriage for which to get the score
        :param gamestate: the current state of the game, usually used to get the trump suit
        :returns: The score for this marriage
        """

        if move.suit is gamestate.trump_suit:
            # royal marriage
            return Score(pending_points=40)
        # any other marriage
        return Score(pending_points=20)

    def score(self, trick: RegularTrick, leader: BotState, follower: BotState, trump: Suit) -> tuple[BotState, BotState, bool]:
        """
        Score the trick for the given leader and follower. The returned bots are the same bots provided (not copies) and have the score of the trick applied.

        :param trick: The trick to score
        :param leader: The botstate of the leader
        :param follower: The botstate of the follower
        :param trump: The trump suit
        :returns: The botstate of the winner and the number of game points, in case there is a winner already. Otherwise None.
        """

        if trick.leader_move.is_marriage():
            regular_leader_move: RegularMove = cast(Marriage, trick.leader_move).underlying_regular_move()
        else:
            regular_leader_move = cast(RegularMove, trick.leader_move)

        leader_card = regular_leader_move.card
        follower_card = trick.follower_move.card
        assert leader_card != follower_card, f"The leader card {leader_card} and follower_card {follower_card} cannot be the same."
        leader_card_points = self.rank_to_points(leader_card.rank)
        follower_card_points = self.rank_to_points(follower_card.rank)

        if leader_card.suit is follower_card.suit:
            # same suit, either trump or not
            if leader_card_points > follower_card_points:
                leader_wins = True
            else:
                leader_wins = False
        elif leader_card.suit is trump:
            # the follower suit cannot be trumps as per the previous condition
            leader_wins = True
        elif follower_card.suit is trump:
            # the leader suit cannot be trumps because of the previous conditions
            leader_wins = False
        else:
            # the follower did not follow the suit of the leader and did not play trumps, hence the leader wins
            leader_wins = True
        winner, loser = (leader, follower) if leader_wins else (follower, leader)
        # record the win
        winner.won_cards.extend([leader_card, follower_card])
        # apply the points
        points_gained = leader_card_points + follower_card_points
        winner.score += Score(direct_points=points_gained)
        # add winner's total of direct and pending points as their new direct points
        winner.score = winner.score.redeem_pending_points()
        return winner, loser, leader_wins

    def declare_winner(self, game_state: GameState) -> Optional[tuple[BotState, int]]:
        """
        Declaring a winner uses the logic from https://web.archive.org/web/20230303074822/https://www.pagat.com/marriage/schnaps.html#out , but simplified, because we do not have closing of the Talon and no need to guess the scores.
        The following text adapted accordingly from that website.

        If a player has 66 or more points, she scores points toward game as follows:

            * one game point, if the opponent has made at least 33 points;
            * two game points, if the opponent has made fewer than 33 points, but has won at least one trick (opponent is said to be Schneider);
            * three game points, if the opponent has won no tricks (opponent is said to be Schwarz).

        If play continued to the very last trick with the talon exhausted, the player who takes the last trick wins the hand, scoring one game point, irrespective of the number of card points the players have taken.

        :param game_state: (GameState): The current gamestate
        :returns: (Optional[tuple[BotState, int]]): The botstate of the winner and the number of game points, in case there is a winner already. Otherwise None.
        """
        if game_state.leader.score.direct_points >= 66:
            follower_score = game_state.follower.score.direct_points
            if follower_score == 0:
                return game_state.leader, 3
            elif follower_score >= 33:
                return game_state.leader, 1
            else:
                # second case in explaination above, 0 < score < 33
                assert follower_score < 66, "Found a follower score of more than 66, while the leader also had more than 66. This must never happen."
                return game_state.leader, 2
        elif game_state.follower.score.direct_points >= 66:
            raise AssertionError("Would declare the follower winner, but this should never happen in the current implementation")
        elif game_state.are_all_cards_played():
            return game_state.leader, 1
        else:
            return None


@dataclass
class GamePlayEngine:
    """
    The GamePlayengine combines the different aspects of the game into an engine that can execute games.
    """
    deck_generator: DeckGenerator
    hand_generator: HandGenerator
    trick_implementer: TrickImplementer
    move_requester: MoveRequester
    move_validator: MoveValidator
    trick_scorer: TrickScorer

    def play_game(self, bot1: Bot, bot2: Bot, rng: Random) -> tuple[Bot, int, Score]:
        """
        Play a game between bot1 and bot2, using the rng to create the game.

        :param bot1: The first bot playing the game. This bot will be the leader for the first trick.
        :param bot2: The second bot playing the game. This bot will be the follower for the first trick.
        :param rng: The random number generator used to shuffle the deck.

        :returns: A tuple with the bot which won the game, the number of points obtained from this game and the score attained.
        """
        cards = self.deck_generator.get_initial_deck()
        shuffled = self.deck_generator.shuffle_deck(cards, rng)
        hand1, hand2, talon = self.hand_generator.generateHands(shuffled)

        leader_state = BotState(implementation=bot1, hand=hand1)
        follower_state = BotState(implementation=bot2, hand=hand2)

        game_state = GameState(
            leader=leader_state,
            follower=follower_state,
            talon=talon,
            previous=None
        )
        winner, points, score = self.play_game_from_state(game_state=game_state, leader_move=None)
        return winner, points, score

    def get_random_phase_two_state(self, rng: Random) -> GameState:
        """
        Get a random GameState in the second phase of the game.

        :param rng: The random number generator used to shuffle the deck.

        :returns: A GameState in the second phase of the game.
        """

        class RandBot(Bot):
            def __init__(self, rand: Random, name: Optional[str] = None) -> None:
                super().__init__(name)
                self.rng = rand

            def get_move(
                self,
                perspective: PlayerPerspective,
                leader_move: Optional[Move],
            ) -> Move:
                moves: list[Move] = perspective.valid_moves()
                move = self.rng.choice(moves)
                return move

        while True:
            cards = self.deck_generator.get_initial_deck()
            shuffled = self.deck_generator.shuffle_deck(cards, rng)
            hand1, hand2, talon = self.hand_generator.generateHands(shuffled)
            leader_state = BotState(implementation=RandBot(rand=rng), hand=hand1)
            follower_state = BotState(implementation=RandBot(rand=rng), hand=hand2)
            game_state = GameState(
                leader=leader_state,
                follower=follower_state,
                talon=talon,
                previous=None
            )
            second_phase_state, _ = self.play_at_most_n_tricks(game_state, RandBot(rand=rng), RandBot(rand=rng), 5)
            winner = self.trick_scorer.declare_winner(second_phase_state)
            if winner:
                continue
            if second_phase_state.game_phase() == GamePhase.TWO:
                return second_phase_state

    def play_game_from_state_with_new_bots(self, game_state: GameState, new_leader: Bot, new_follower: Bot, leader_move: Optional[Move]) -> tuple[Bot, int, Score]:
        """
        Continue a game  which might have started before with other bots, with new bots.
        The new bots are new_leader and new_follower.
        The leader move is an optional paramter which can be provided to force this first move from the leader.

        :param game_state: The state of the game to start from
        :param new_leader: The bot which will take the leader role in the game.
        :param new_follower: The bot which will take the follower in the game.
        :param leader_move: if provided, the leader will be forced to play this move as its first move.

        :returns: A tuple with the bot which won the game, the number of points obtained from this game and the score attained.
        """

        game_state_copy = game_state.copy_with_other_bots(new_leader=new_leader, new_follower=new_follower)
        return self.play_game_from_state(game_state_copy, leader_move=leader_move)

    def play_game_from_state(self, game_state: GameState, leader_move: Optional[Move]) -> tuple[Bot, int, Score]:
        """
        Continue a game  which might have been started before.
        The leader move is an optional paramter which can be provided to force this first move from the leader.

        :param game_state: The state of the game to start from
        :param leader_move: if provided, the leader will be forced to play this move as its first move.

        :returns: A tuple with the bot which won the game, the number of points obtained from this game and the score attained.
        """
        winner: Optional[BotState] = None
        points: int = -1
        while not winner:
            if leader_move is not None:
                # we continues from a game where the leading bot already did a move, we immitate that
                game_state = self.trick_implementer.play_trick_with_fixed_leader_move(game_engine=self, game_state=game_state, leader_move=leader_move)
                leader_move = None
            else:
                game_state = self.trick_implementer.play_trick(self, game_state)
            winner, points = self.trick_scorer.declare_winner(game_state) or (None, -1)

        winner_state = WinnerPerspective(game_state, self)
        winner.implementation.notify_game_end(won=True, perspective=winner_state)

        loser_state = LoserPerspective(game_state, self)
        game_state.follower.implementation.notify_game_end(False, perspective=loser_state)

        return winner.implementation, points, winner.score

    def play_one_trick(self, game_state: GameState, new_leader: Bot, new_follower: Bot) -> GameState:
        """
        Plays one tricks (including the one started by the leader, if provided) on a game which might have started before.
        The new bots are new_leader and new_follower.

        This method does not make changes to the provided game_state.

        :param game_state: The state of the game to start from
        :param new_leader: The bot which will take the leader role in the game.
        :param new_follower: The bot which will take the follower in the game.

        :returns: The GameState reached and the number of steps actually taken.
        """
        state, rounds = self.play_at_most_n_tricks(game_state, new_leader, new_follower, 1)
        assert rounds == 1, f"We called play_at_most_n_tricks with rounds=1, but it returned not excactly 1 round, got {rounds} rounds."
        return state

    def play_at_most_n_tricks(self, game_state: GameState, new_leader: Bot, new_follower: Bot, n: int) -> tuple[GameState, int]:
        """
        Plays up to n tricks (including the one started by the leader, if provided) on a game which might have started before.
        The number of tricks will be smaller than n in case the game ends before n tricks are played.
        The new bots are new_leader and new_follower.

        This method does not make changes to the provided game_state.

        :param game_state: The state of the game to start from
        :param new_leader: The bot which will take the leader role in the game.
        :param new_follower: The bot which will take the follower in the game.
        :param n: the maximum number of tricks to play

        :returns: The GameState reached and the number of steps actually taken.
        """
        assert n >= 0, "Cannot play less than 0 rounds"
        game_state_copy = game_state.copy_with_other_bots(new_leader=new_leader, new_follower=new_follower)

        winner: Optional[BotState] = None
        rounds_played = 0
        while not winner:
            if rounds_played == n:
                break
            game_state_copy = self.trick_implementer.play_trick(self, game_state_copy)
            winner, _ = self.trick_scorer.declare_winner(game_state_copy) or (None, -1)
            rounds_played += 1
        if winner:
            winner_state = WinnerPerspective(game_state_copy, self)
            winner.implementation.notify_game_end(won=True, perspective=winner_state)

            loser_state = LoserPerspective(game_state_copy, self)
            game_state_copy.follower.implementation.notify_game_end(False, perspective=loser_state)

        return game_state_copy, rounds_played

    def __repr__(self) -> str:
        return f"GamePlayEngine(deck_generator={self.deck_generator}, "\
               f"hand_generator={self.hand_generator}, "\
               f"trick_implementer={self.trick_implementer}, "\
               f"move_requester={self.move_requester}, "\
               f"move_validator={self.move_validator}, "\
               f"trick_scorer={self.trick_scorer})"


class SchnapsenGamePlayEngine(GamePlayEngine):
    """
    A GamePlayEngine configured according to the rules of Schnapsen
    """

    def __init__(self) -> None:
        super().__init__(
            deck_generator=SchnapsenDeckGenerator(),
            hand_generator=SchnapsenHandGenerator(),
            trick_implementer=SchnapsenTrickImplementer(),
            move_requester=SimpleMoveRequester(),
            move_validator=SchnapsenMoveValidator(),
            trick_scorer=SchnapsenTrickScorer()
        )

    def __repr__(self) -> str:
        return super().__repr__()

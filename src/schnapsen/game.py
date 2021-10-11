from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import FunctionType
from typing import Any, Callable, Iterable, Optional
from .deck import CardCollection, OrderedCardCollection, Card, Rank, Suit


class Move(ABC):
    @abstractmethod
    def is_marriage(self) -> bool:
        pass

    @abstractmethod
    def is_trump_exchange(self) -> bool:
        pass

    @abstractmethod
    def cards(self) -> Iterable[Card]:
        pass


@dataclass
class RegularMove(Move):
    card: Card

    def is_marriage(self) -> bool:
        return False

    def is_trump_exchange(self) -> bool:
        return False

    def cards(self) -> Iterable[Card]:
        return [self.card]


@dataclass
class Marriage(Move):
    queen_card: Card
    king_card: Card

    def __init__(self, queen_card: Card, king_card: Card) -> None:
        assert queen_card.is_rank(Rank.QUEEN)
        assert king_card.is_rank(Rank.KING)
        assert queen_card.suit() == king_card.suit()
        self.king_card = king_card
        self.queen_card = queen_card

    def is_marriage(self) -> bool:
        return True

    def is_trump_exchange(self) -> bool:
        return False

    def as_regular_move(self) -> RegularMove:
        # TODO this limits you to only have the queen to play after a marriage, while in general you would ahve a choice
        return RegularMove(self.queen_card)

    def cards(self) -> Iterable[Card]:
        return [self.queen_card, self.king_card]


@dataclass
class Trump_Exchange(Move):

    def __init__(self, card: Card) -> None:
        assert card.is_rank(Rank.JACK)
        self.jack = card

    def is_suit(self, suit: Suit) -> bool:
        return self.jack.is_suit(suit)

    def has_same_suit(self, card: Card) -> bool:
        return self.jack.is_same_suit(card)

    def is_trump_exchange() -> bool:
        return True

    def cards(self) -> Iterable[Card]:
        return [self.jack]


class Hand (CardCollection):
    def __init__(self, cards: Iterable[Card]) -> None:
        # TODO assert no duplicates in these cards
        # TODO assert masimal number of cards
        self.cards = list(cards)

    def remove(self, card: Card):
        try:
            self.cards.remove(card)
        except:
            raise Exception(f"Trying to play a card fromt he hand which is not in the hand. Hand is {self.cards}, trying to play {card}")

    def add(self, card: Card):
        assert card not in self.cards, "Adding a card to a hand, but there is already such a a card"
        self.cards.append(card)

    def has_cards(self, cards: Iterable[Card]):
        return all([card in self.cards for card in cards])


class Talon (OrderedCardCollection):
    pass


class PartialTrick:
    def __init__(self, move: Move) -> None:
        self.move = move


class Trick(PartialTrick):
    def __init__(self, part: PartialTrick, second_move: Move) -> None:
        assert not part.move.is_marriage()
        self.first_move = part.move
        self.second_move = second_move


@dataclass
class Score:
    direct_points: int = 0
    pending_points: int = 0

    def record_marriage(self):
        self.pending_points += 20

    def record_royal_marriage(self):
        self.pending_points += 40


# class TrickScorer:
#     @abstractmethod
#     def score(self, trick: Trick) -> Score:
#         pass


class InvibleTalon:
    pass


class PlayerGameState:
    player_hand: Hand
    opponent_hand: Optional[Hand]
    on_table: PartialTrick
    trump: Card
    talon: InvibleTalon

    def __init__(self, state: 'GameState', first_or_second) -> None:
        pass

    def valid_moves() -> Iterable[Card]:
        pass


# TODO move to a more logical palce
@dataclass
class Bot:
    implementation : Callable[['GameState'], Move]
    hand: Hand
    score: Score

    def get_move(self, state: PlayerGameState) -> Move:
        self.implementation.get_move(state)


@dataclass
class GameState:
    # first_player: Hand
    # second_player: Hand
    # TODO should these be here, or passed as arguments?
    bot1: Bot
    bot2: Bot
    leader: Bot
    follower: Bot
    trump: Card
    talon: Talon
    previous: 'GameState'
    # ongoing_trick: PartialTrick
    # scorer: TrickScorer

    def copy() -> 'GameState':
        """Make a copy of the gamestate"""

        # TODO copy the needed parts: bots, talon
        new_state = GameState(bot1, bot2, leader, follower, trump, talon, self)

    def play_trick(self) -> 'GameState':

        player_game_state = PlayerGameState(self, "first")
        # ask first players move
        move = self.leader.get_move(player_game_state)

        assert self.leader.hand.has_cards(move.cards()), \
            "Tried to play a move for which the player does not have the cards. Played {move.cards}, but has {self.leader.hand}"

        if move.is_trump_exchange():
            # create new GameState with moved cards
            trump_move: Trump_Exchange = move
            assert trump_move.has_same_suit(self.trump), \
                f"A trump exchange can only be done with a Jack o the same suit as the current trump. Got a {trump_move.jack} while the  Trump card is a {self.trump}"
            gamestate = self.copy()
            # apply the changes in the gamestate
            gamestate.leader.hand.remove(trump_move.jack)
            gamestate.leader.hand.add(self.trump)
            gamestate.trump = trump_move.jack
            return gamestate
            # TODO is this okay? We end the trick without a real trick being played
        if move.is_marriage():
            # record score, keep in mind the royal marriage
            marriage_move: Marriage = move
            if marriage_move.has_same_suit(self.trump):
                self.leader.score.record_royal_marriage()
            else:
                self.leader.score.record_marriage()

            move = move.as_regular_move()

        # normal play

            loser =
            winner =

            if second_player_wins:
                new_state = GameState(
                    self.bot1, self.bot2, leader=winner,
                    follower=loser,
                    # TODO and so on
                )

            # ask second player

            # make sure this is not a marriage/exchange

            # class GamestateBeforeFirstMove:
            #     pass
            # class GamestateBeforeSecondMove:
            #     pass
            # class GameStateAfterMoves:
            #     pass


class FirstMovePhaseOneState:
    player_hand: Hand
    trump: Card
    talon: InvibleTalon


class SecondMovePhaseTwoState:
    player_hand: Hand
    opponent_hand: Hand
    on_table: PartialTrick
    trump: Card

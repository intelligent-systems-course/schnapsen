from abc import ABC, abstractmethod
from dataclasses import dataclass
import dataclasses
from functools import partial
from types import FunctionType
from typing import Any, Callable, Iterable, Optional, Tuple
from .deck import CardCollection, OrderedCardCollection, Card, Rank, Suit


class Move(ABC):
    @abstractmethod
    def is_marriage(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def is_trump_exchange(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def cards(self) -> Iterable[Card]:
        raise NotImplementedError()


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

    def copy(self) -> 'Hand':
        return Hand(list(self.cards))


class Talon (OrderedCardCollection):
    def __init__(cards: Iterable[Card]) -> None:
        """The cards of the Talon. The first card is the bottommost card. The last on is the top card (which will be taken is a card is drawn)
            The Trump card is at the bottom of the Talon.
        """
        super().__init__(list(cards))

    def copy(self):
        return Talon(self._cards)

    def trump_exchange(self, new_trump: Card) -> Tuple['Talon', Card]:
        """ perfom a trump-jack exchange. The card to be put as the trump card must be a Jack od the same suit.
        As a result, this Talon is not changed, but rather a modified Talon and the exchanged card are returned."""
        assert new_trump.is_rank(Rank.JACK)
        assert len(self._cards) >= 2
        assert new_trump.is_same_suit(self._cards[0])
        new_talon = self.copy()
        old_trump = new_talon._cards.pop(0)
        new_talon.insert(0, new_trump)
        return (new_talon, old_trump)

    def draw_cards(self) -> Tuple['Talon', Card, Card]:
        """Draw a card from this Talon. This does not change the talon, btu rather returns a talon with the change applied and the card drawn"""
        assert len(self._cards)
        self._cards


class PartialTrick:
    def __init__(self, move: RegularMove) -> None:
        self.move = move


@dataclasses
class Trick(PartialTrick):
    first_move: RegularMove
    second_move: RegularMove

    def __init__(self, part: PartialTrick, second_move: RegularMove) -> None:
        assert not part.move.is_marriage()
        self.first_move = part.move
        self.second_move = second_move


@dataclass(frozen=True)
class Score:
    direct_points: int = 0
    pending_points: int = 0

    def __add__(self, other: 'Score'):
        total_direct_points = self.direct_points + other.direct_points
        total_pending_points = self.pending_points + other.pending_points
        return Score(total_direct_points, total_pending_points)

    def copy(self) -> 'Score':
        return Score(direct_points=self.direct_points, pending_points=self.pending_points)


# TODO move to a more logical palce
class Bot:
    """A bot with its implementation and current state in a game"""

    implementation: Callable[['GameState'], Move]
    hand: Hand
    score: Score

    def get_move(self, state: 'PlayerGameState') -> Move:
        move = self.implementation.get_move(state)
        assert self.hand.has_cards(move.cards()), \
            f"Tried to play a move for which the player does not have the cards. Played {move.cards}, but has {self.hand}"
        return move

    def copy(self) -> 'Bot':
        new_bot = Bot(implementation=self.implementation, hand=self.hand.copy(), score=self.score.copy())
        return new_bot

class TrickScorer:

    RANK_TO_POINTS = {
        Rank.ACE: 11,
        Rank.TEN: 10,
        Rank.KING: 4,
        Rank.QUEEN: 3,
        Rank.JACK: 2,
    }


    def score(t: Trick, m: Optional[Marriage], leader: Bot, follower: Bot) -> Tuple[Bot, Bot]:
        """The returned bots having the score of the marriageand  trick applied, and in order (new_leader, new_follower)"""
        raise NotImplementedError("TODO")

    def score(self, trick: Trick) -> Score:
        # score_one = trick.
        pass

    def marriage(self) -> 'Score':
        new_score = Score(pending_points=20)
        return new_score

    def royal_marriage(self) -> 'Score':
        new_score = Score(pending_points=40)
        return new_score


class InvisibleTalon:
    pass


class PlayerGameState:
    player_hand: Hand
    opponent_hand: Optional[Hand]
    on_table: PartialTrick
    trump: Card
    talon: InvisibleTalon

    def __init__(self, state: 'GameState', first_or_second) -> None:
        pass

    def valid_moves() -> Iterable[Card]:
        pass





@dataclass
class GameState:
    # first_player: Hand
    # second_player: Hand
    # TODO should these be here, or passed as arguments?
    bot1: Bot
    bot2: Bot
    leader: Bot
    follower: Bot
    trump_suit: Suit
    talon: Talon
    previous: 'GameState'
    # ongoing_trick: PartialTrick
    scorer: TrickScorer = TrickScorer()

    def copy(self) -> 'GameState':
        """Make a copy of the gamestate"""

        # TODO copy the needed parts: bots, talon
        bot1 = self.bot1.copy()
        bot2 = self.bot2.copy()
        if self.leader == self.bot1:
            leader = bot1
            follower = bot2
        else:
            leader = bot2
            follower = bot1

        new_state = GameState(bot1=bot1, bot2=bot2, leader=leader, follower=follower, trump=self.trump, talon=self.talon.copy(), previous=self)
        return new_state

    def play_trum_exchange(self, trump_move: Trump_Exchange) -> 'GameState':
        assert trump_move.is_suit(self.trump_suit), \
            f"A trump exchange can only be done with a Jack o the same suit as the current trump. Got a {trump_move.jack} while the  Trump card is a {self.trump}"
        # create new GameState with moved cards
        gamestate = self.copy()
        # apply the changes in the gamestate
        gamestate.leader.hand.remove(trump_move.jack)
        modified_talon, old_trump = gamestate.talon.trump_exchange(trump_move.jack)
        gamestate.talon = modified_talon
        gamestate.leader.hand.add(old_trump)
        gamestate.trump = trump_move.jack
        return gamestate

    def _play_marriage(self, marriage_move: Marriage) -> Score:
        """Computes the new score from playing the mariage. This does not change the GameState"""
        if marriage_move.has_same_suit(self.trump):
            return self.leader.score + self.scorer.royal_marriage()
        else:
            return self.leader.score + self.scorer.marriage()

    def __decide_winer_and_loser(trick):
        pass

    def play_trick(self) -> 'GameState':

        leader_game_state = PlayerGameState(self, "leader")
        # ask first players move
        leader_move = self.leader.get_move(leader_game_state)

        if leader_move.is_trump_exchange():
            trump_move: Trump_Exchange = leader_move
            return self.play_trum_exchange(trump_move)
            # TODO is this okay? We end the trick without a real trick being played
        if leader_move.is_marriage():
            # record score, keep in mind the royal marriage
            marriage_move: Marriage = leader_move
            new_leader_score = self._play_marriage(marriage_move=marriage_move)
            leader_move = leader_move.as_regular_move()
        else:
            # normal move, make a copy of the score already
            new_leader_score = self.leader.score.copy()
        # normal play
        partial_trick = PartialTrick(leader_move)
        follower_game_state = PlayerGameState(self, "follower", partial_trick)
        follower_move = self.follower.get_move(follower_game_state)

        trick = Trick(partial_trick, follower_move)
        winner, loser = self.decide_winner_and_loser(trick)
        points = self.scorer.score

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


# class FirstMovePhaseOneState:
#     player_hand: Hand
#     trump: Card
#     talon: InvisibleTalon


# class SecondMovePhaseTwoState:
#     player_hand: Hand
#     opponent_hand: Hand
#     on_table: PartialTrick
#     trump: Card
